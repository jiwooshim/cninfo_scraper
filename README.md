# CNINFO Scraper

This script will scrape the data from Cninfo website and store it in a SQLite3 database. 

## File name format
file name format: {YYYYMMDD}_{security code}_{report id}_{report title}.pdf  
file name example: 20220101_000528_1212076583_第九届监事会第一次会议决议公告.pdf  

## Usage
Use the below code for the params: category, exchange, sortName, sortType. 
Multiple inputs are allowed, separated by semicolon (;)  
Simply add the codes on the left of the arrow (=>) sign to the params.  

### 板块 Exchange  
sz => 深市 Shenzhen Stock Exchange  
szmb => 深主板 Shenzhen Main Board   
szcy => 创业板 Growth Enterprise Market  
sh => 沪市 Shanghai Stock market  
shmb => 沪主板 Shanghai Main Board  
shkcp => 科创板 Science and Technology Innovation Board  
bj => 北交所 Beijing Stock Exchange  
  
### 分类 Category  
category_ndbg_szsh => 年报 Annual report  
category_bndbg_szsh => 半年报 Semi-annual report  
category_yjdbg_szsh => 一季报 Quarterly report  
category_sjdbg_szsh => 三季报 Three quarterly report  
category_yjygjxz_szsh => 业绩预告 Performance forecast  
category_qyfpxzcs_szsh => 权益分派 Equity distribution  
category_dshgg_szsh => 董事会 Board  
category_jshgg_szsh => 监事会 Supervisory board  
category_gddh_szsh => 股东大会 General meeting of shareholders  
category_rcjy_szsh => 日常经营 Daily operation  
category_gszl_szsh => 公司治理 Corporate governance  
category_zj_szsh => 中介报告 Brokerage report  
category_sf_szsh => 首发 Initial public offering  
category_zf_szsh => 增发 Additional public offering  
category_gqjl_szsh => 股权激励 Stock incentive  
category_pg_szsh => 配股 Rights issue  
category_jj_szsh => 解禁 Unlocking  
category_gszq_szsh => 公司债 Corporate bonds  
category_kzzq_szsh => 可转债 Convertible bonds  
category_qtrz_szsh => 其他融资 Other financing  
category_gqbd_szsh => 股权变动 Equity change  
category_bcgz_szsh => 股权变动 Equity change  
category_cqdq_szsh => 澄清致歉 Clarification  
category_fxts_szsh => 风险提示 Risk warning  
category_tbclts_szsh => 特别处理和退市 Special treatment and delisting  
category_tszlq_szsh => 退市整理期 Delisting period  

### sortName
'code' or 'time'  
### sortType
'asc' or 'desc'

## Output  
Output files are saved in the "download" folder by default. A log file and a database file will be created as well, 
in the parent folder. 

The files inside the "download" folder are organized under subfolders capped at 1000 files per subfolder. 
The order of the files is determined by the sortName and sortType params.







