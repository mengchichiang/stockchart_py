# stockchart_py
Stockchart is portfolio managment, Historical quotes downloader and plot stock chart.
It is used for Taiwan, HongKong and US stock market. SQLite is default database after version 2.0.
If you want to use PostgreSQL, you could modify config.ini file and reference to README.md of version 1.4 to do setting.

## Quick start
1. `$git clone https://github.com/mengchichiang/stockchart_py.git`
2. install python3 package
3. create virtual environment
 ```
  $virtualenv stockchart
  $source stockchart/bin/activate
 ```
4. install package
 ```
  $pip install -r requirements.txt

 ```
5. server run
 ```
  $. python manage.py runserver localhost:8000
 ```
6. open browser 
    http://localhost:8000/

## Usage

### Portfolio example
  * Switch group to US and click ImportPortfolio to import csv file `/stockchart/portfolio/portfolioUS.csv`. Then click "Manage Data">"Download Data" to download data. Click stock symbol to plot charts.
  
### Add stock symbol to WatchList
  * Step 1. Click CreatePortfolio to create a new Portfolio.
  * Step 2. Key in stock symbol (for eaxmple, "AAPL") and then click "add Symbol" button. 
  * If the input stock symbol is not in current market group, the symbol format is xxxx__yyyy. xxxx is stock symbol and yyyy is market group. "__" is 2 underline "_". 
  For example,  add TW market stock symbol 2330 to group US. The  symbol is writed as "2330__TW".

### config.ini
  * Setup login user name and password.
  * Setup download start year.

###  customize stock symbol, market and data download source.
   Group is stock market name. If you want to define your stock market, you should do as follows: 
  1. Define the group xxxxx with pfGroupArray in  config.ini file.
  2. Edit stock symbol and data download source in the file "lib/symbolxxxxx.csv". If download source is yahoo, stcok symbol is identical to yahoo finance web site. 
  3. Download source yyyyy need a download modele "/lib/stockData/mod_yyyyy.py" to download historical quotes. (i.e. If download source is yahoo, the download modele is "/lib/stockData/mod_yahoo.py" ) 

  Note: Download source Google is not work now. You can try to write a new download module /lib/stockData/mod_google.py.

## License

MIT.

