# stockchart_py
Stockchart is portfolio managment, Historical quotes downloader and plot stock chart.
It is used for Taiwan, HongKong and US stock market.

## Quick start
1. install postgresql
2. add user account and database to postgresql
 ```
  $sudo su - postgres
  $psql
  postgres=# CREATE ROLE test LOGIN PASSWORD '1234' NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE;
  postgres=# CREATE DATABASE stockdb WITH OWNER = test ENCODING = 'UTF8' TABLESPACE = pg_default;
  postgres=# \q
 ```
3. `$git clone https://github.com/mengchichiang/stockchart_py.git`
4. install python3 package
5. create virtual environment
 ```
  $virtualenv stockchart
  $source stockchart/bin/activate
 ```
6. install package
 ```
  $pip install -r requirements.txt

 ```
7. server run
 ```
  $. python manage.py runserver localhost:8000
 ```
8. open browser 
    http://localhost:8000/

9. login
 ```
 user name:test
 password:1234
 ```

## Usage

### Portfolio example
  * Switch group to US and click ImportPortfolio to import csv file `/stockchart/portfolio/portfolioUS.csv`. Then click "Manage Data">"Download Data" to download data. Click stock symbol to plot charts.
  
### Add stock symbol to WatchList
  * Key in stock symbol and click "add Symbol" button. If the input stock symbol is not in current market group, the symbol format is xxxx__yyyy. xxxx is stock symbol and yyyy is market group. "__" is 2 underline "_". For example, 
  at US group add TW market stock symbol 2330 must use "2330__TW".

### config.ini
  * Setup login user name and password.
  * Setup download start year.

### 
  The file "lib/custom.csv" let you to customize stock symbol and data source.

## License

MIT.


