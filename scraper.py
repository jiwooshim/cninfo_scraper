import os
import requests
import sqlite3
from tqdm import tqdm
from datetime import datetime, date
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from dateutil.rrule import rrule, DAILY, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta


class CninfoScraper:
    def __init__(self, logger, start_date, end_date, category="", exchange="", sort_name="time", sort_type="asc",
                 download_path="download", page_num=1):
        """
        :param start_date: start date of query, format: YYYY-MM-DD
        :param end_date: end date of query, format: YYYY-MM-DD
        :param category: report category code, separated by semicolon (;)
        :param exchange: stock exchange code, separated by semicolon (;)
        :param sort_name: sort by date or code, options: date, code
        :param sort_type: sort by ascending or descending, options: asc, desc
        """
        self.logger = logger
        self.conn = None
        self.session = None
        self.response = None
        self.report_name = None
        self.category = category
        self.exchange = exchange
        self.start_date = start_date
        self.end_date = end_date
        self.page_num = page_num
        self.download_path = download_path
        self.sort_name = sort_name
        self.sort_type = sort_type
        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)
        self.init_database()
        self.init_session()


    def get_requests_details(self):
        # self.url = 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search'
        self.url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        self.headers = {
            'Host': 'www.cninfo.com.cn',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://www.cninfo.com.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.params = {
            "pageNum": self.page_num,
            "pageSize": "30",
            "column": "szse",
            "tabName": "fulltext",
            "plate": self.exchange,
            "stock": "",
            "searchkey": "",
            "secid": "",
            "category": self.category,
            "trade": "",
            "seDate": f"{self.start_date}~{self.end_date}",
            "sortName": self.sort_name,
            "sortType": self.sort_type,
            "isHLtitle": "true"
        }
        
    def init_session(self):
        self.session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def download_report(self, report):
        try:
            report_url = f"http://static.cninfo.com.cn/{report['adjunctUrl']}"
            report_date = datetime.strftime(datetime.fromtimestamp(int(report['announcementTime'])/1000).date(), '%Y%m%d')
            self.report_name = f"{report_date}_{report['secCode']}_{report['announcementId']}_" \
                               f"{report['announcementTitle'].replace(' ', '-').replace('/', '-')}.pdf"
            self.download_subpath = self.init_download_path()
            self.report_path = os.path.join(self.download_subpath, self.report_name)

            res = self.session.get(report_url)
            res.raise_for_status()
            self.insert_database(report, self.download_subpath)
            if os.path.exists(self.report_path):
                return False, 'file already exists'
            with open(os.path.abspath(self.report_path), 'wb') as f:
                f.write(res.content)
            return True, 'success'
        except:
            return False, 'error'

    def init_download_path(self):
        subpath_list = os.listdir(self.download_path)
        subpath_list = [folder for folder in subpath_list
                        if not folder.startswith('.')
                        and not folder.endswith('.db')
                        and not folder.endswith('.log')]
        if len(subpath_list) > 0:
            download_subpath = os.path.join(
                self.download_path, max(subpath_list))
            if len(os.listdir(download_subpath)) < 1000:
                return download_subpath
        download_subpath = os.path.join(
            self.download_path, str(len(subpath_list) + 1).zfill(5))
        if not os.path.exists(download_subpath):
            os.makedirs(download_subpath)
        return download_subpath

    def init_database(self):
        self.conn = sqlite3.connect(os.path.join(self.download_path, "reports_metadata.db"))
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS reports
            (
                _id INTEGER PRIMARY KEY AUTOINCREMENT, 
                _insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                _insert_location TEXT,
                _insert_filename TEXT,
                _announcementTime_converted TIMESTAMP,
                adjunctSize TEXT,
                adjunctUrl TEXT,
                announcementContent TEXT,
                announcementId TEXT,
                announcementTime TEXT,
                announcementTitle TEXT,
                announcementType TEXT,
                announcementTypeName TEXT,
                associateAnnouncement TEXT,
                batchNum TEXT,
                columnId TEXT,
                id TEXT,
                important TEXT,
                orgId TEXT,
                orgName TEXT,
                pageColumn TEXT,
                secCode TEXT,
                secName TEXT,
                storageTime TEXT
            )
        ''')
        self.conn.commit()

    def insert_database(self, report, location):
        self.cur.execute(
            f"""INSERT INTO reports VALUES (
                    NULL, 
                    CURRENT_TIMESTAMP,
                    '{location}',
                    '{self.report_name}',
                    '{datetime.fromtimestamp(int(report['announcementTime'])/1000)}',
                    '{report['adjunctSize']}', 
                    '{report['adjunctUrl']}', 
                    '{report['announcementContent']}', 
                    '{report['announcementId']}', 
                    '{report['announcementTime']}', 
                    '{report['announcementTitle']}', 
                    '{report['announcementType']}', 
                    '{report['announcementTypeName']}', 
                    '{report['associateAnnouncement']}', 
                    '{report['batchNum']}', 
                    '{report['columnId']}', 
                    '{report['id']}', 
                    '{report['important']}', 
                    '{report['orgId']}', 
                    '{report['orgName']}', 
                    '{report['pageColumn']}', 
                    '{report['secCode']}', 
                    '{report['secName']}', 
                    '{report['storageTime']}'
                )""")
        self.conn.commit()

    def close_database(self):
        self.conn.commit()
        self.conn.close()

    def scrape(self):
        total_count = 0
        fail_count = 0
        success_count = 0
        duplicate_count = 0
        self.get_requests_details()
        res = requests.post(
            self.url, headers=self.headers, params=self.params)
        pbar = tqdm(total=res.json()['totalAnnouncement'])
        while True:
            self.get_requests_details()
            self.response = requests.post(
                self.url, headers=self.headers, params=self.params)
            self.response.raise_for_status()
            self.response = self.response.json()
            if self.response['totalAnnouncement'] == 0:
                self.logger.error(f"Total report number is 0, please check your parameters.")
                break
            for report in self.response['announcements']:
                total_count += 1
                report_success, report_status = self.download_report(report)
                if report_success:
                    self.logger.info(f"[Success] {self.report_path}")
                    pbar.update(1)
                    success_count += 1
                else:
                    self.logger.error(f"[Fail-{report_status}] {self.report_path}")
                    if report_status == 'error':
                        fail_count += 1
                    else:
                        duplicate_count += 1

            if self.response['hasMore'] and self.page_num < self.response['totalpages']:
                self.page_num += 1
                continue
            else:
                break
        self.logger.info(f"Total: {total_count}, Success: {success_count}, Fail: {fail_count}, Duplicate: {duplicate_count}")
        self.logger.info(f'Process ended at {datetime.now()}')
        self.logger.info('=' * 65)
        self.close_database()
        pbar.close()


def init_logger(logger_name='reports_download.log'):
    # log_file_name = logger_name
    logger = logging.getLogger(logger_name)
    # set log level and format
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y%m%d %H:%M:%S')
    # file handler config
    file_handler = logging.FileHandler(logger_name)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    file_handler.set_name(logger_name+'_handler')
    logger.addHandler(file_handler)
    # Initial log
    logger.info(f'Download started at {datetime.now()}')
    logger.info('=' * 65)
    return logger


def get_yearly_data(year):
    if not os.path.exists(os.path.join('download', str(year))):
        os.makedirs(os.path.join('download', str(year)))
    logger = init_logger(logger_name=f'download/{year}/reports_download{year}.log')
    logger.info('=' * 65)
    logger.info(f"Fetching year: {year}")
    for month in rrule(MONTHLY, dtstart=datetime(year, 1, 1), until=datetime(year, 12, 31)):
        logger.info(f"Fetching month: {month}")
        for dt in rrule(DAILY, dtstart=month, until=month + relativedelta(months=1) - relativedelta(days=1)):
            logger.info(f"Fetching day: {dt}")
            start_date = datetime.strftime(dt, '%Y-%m-%d')
            end_date = datetime.strftime(dt+relativedelta(days=1), '%Y-%m-%d')
            scraper = CninfoScraper(logger, download_path=f'download/{year}', start_date=start_date, end_date=end_date)
            scraper.scrape()


def multithreading(start_year, end_year):
    threads = []
    for year_range in range(end_year, start_year, - 5):
        for year in range(year_range, year_range - 5, -1):
            if year < start_year or year > end_year:
                continue
            t = threading.Thread(target=get_yearly_data, args=(year,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()


def main(start_year, end_year):
    for year in range(end_year, start_year-1, -1):
        get_yearly_data(year)


if __name__ == "__main__":
    start_year = 2000
    end_year = 2022
    multithreading(start_year, end_year)
    # main(start_year, end_year)
