import requests
import os
from twilio.rest import Client
from datetime import datetime as dt

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
twil_phone = os.environ.get('TWIL_PHONE')
my_phone = os.environ.get('MY_PHONE')

stock_parameters = {
    "function":"TIME_SERIES_DAILY_ADJUSTED",
    "symbol":STOCK,
    "apikey":STOCK_API_KEY
}

news_parameters ={
    "q":COMPANY_NAME,
    "pageSize":3,
    "apiKey":NEWS_API_KEY,
}

#Get data
response = requests.get(url=STOCK_ENDPOINT, params = stock_parameters)
response.raise_for_status()
stock_data = response.json()

response = requests.get(url=NEWS_ENDPOINT, params = news_parameters)
response.raise_for_status()
news_data = response.json()

# Get today and yesterday dates
raw_today = dt.now()
year = raw_today.year

if raw_today.month <10:
    month = f"0{raw_today.month}"
else:
    month = raw_today.month

if raw_today.day<10:
    day = f"0{raw_today.day}"
else:
    day = raw_today.day

today = f"{year}-{month}-{day}"
yesterday = f"{year}-{month}-{day-1}"

# Calculate Closing Price Yesterday and Today
close_today = float(stock_data["Time Series (Daily)"][today]["4. close"])
close_yesterday = float(stock_data["Time Series (Daily)"][yesterday]["4. close"])

# Calculate Percent Change
percent_change = round(abs(((close_today - close_yesterday)/(close_yesterday))*100),2)
if ((close_today - close_yesterday)/close_yesterday)*100 > 0:
    direction = "+"
else:
    direction = "-"

# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday, fetch the first 3 articles for the COMPANY_NAME.
if percent_change >5:
    articles = {}
    for i in range (0,3):
        articles[news_data["articles"][i]["title"]]=news_data["articles"][i]["description"]

# Use Twilio to send a separate message with each article's title and description to my phone number.
    articles_list = [(k, v) for k, v in articles.items()]
    for i in range (0,3):
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
            body=f"{STOCK}: {direction}{percent_change}%\nHeadline: {articles_list[i][0]}\nBrief: {articles_list[i][1]}",
            from_=twil_phone,
            to=my_phone
    )
