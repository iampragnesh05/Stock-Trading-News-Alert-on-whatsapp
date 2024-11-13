import yfinance as yf
from datetime import datetime, timedelta
from twilio.rest import Client
import requests
# Twilio credentials
account_sid = 'AC2cb983b4f19059c4c5f5af821224b61d'
auth_token = '0137a381197616e99e67cceb5b3b7232'
client = Client(account_sid, auth_token)
#
# ## STEP 1: Use https://www.alphavantage.co
# # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# # Fetch historical data for the last 3 days
# # Function to get the first 3 news pieces
#
#
# ## STEP 3: Use https://www.twilio.com
# # Send a seperate message with the percentage change and each article's title and description to your phone number.
#
#
# #Optional: Format the SMS message like this:
# """
# TSLA: 🔺2%
# Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
# Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
# or
# "TSLA: 🔻5%
# Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
# Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
# """
#

def get_company_news(company_name, from_date, to_date, news_api_key):
    url = f"https://newsapi.org/v2/everything?q={company_name}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={news_api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        news_data = response.json()
        if news_data.get("totalResults", 0) > 0:
            articles = news_data["articles"][:3]
            return articles  # Return the list of articles if available
        else:
            return None  # No news articles found
    else:
        print("Error fetching news:", response.status_code)
        return None



def check_stock_percentage_change(stock_symbol, company_name, news_api_key):
    if not stock_symbol.endswith('.NS'):
        stock_symbol += '.NS'

    stock = yf.Ticker(stock_symbol)
    historical_data = stock.history(period="5d")

    if len(historical_data) >= 2:
        yesterday_close = historical_data['Close'].iloc[-1]
        day_before_yesterday_close = historical_data['Close'].iloc[-2]

        percentage_change = ((yesterday_close - day_before_yesterday_close) / day_before_yesterday_close) * 100

        print(f"Percentage change for {company_name} is {percentage_change:.2f}%")

        if abs(percentage_change) >= 5:
            print(f"\nStock price changed by {percentage_change:.2f}%. Fetching news...\n")
            today_date = datetime.now().date()
            articles = get_company_news(company_name, today_date, today_date, news_api_key)

            for article in articles:
                send_message_to_whatsapp(stock_symbol, percentage_change, article["title"], article["description"])

        else:
            send_message_to_whatsapp(stock_symbol, percentage_change, "No news articles found", "")
    else:
        print("Not enough data to calculate percentage change.")
def send_message_to_whatsapp(stock_symbol, percentage_change, headline, brief):
    change_icon = "🔺" if percentage_change > 0 else "🔻"
    if not headline:  # When there are no news articles
        message_body = f"{stock_symbol}: {change_icon}{abs(percentage_change)}%\nNo news articles found for today."
    else:
        message_body = f"{stock_symbol}: {change_icon}{abs(percentage_change)}%\nHeadline: {headline}\nBrief: {brief}"

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message_body,
        to='whatsapp:+919116955257'
    )

    print(f"Message sent with SID: {message.sid}")


# Main function to allow user to input new stock and company
def main():
    NEWS_API_KEY = "153e994c4a3e4565ad9c8d6056d36242"  # Replace with your actual NewsAPI key
    stock_symbol = input("Enter the stock symbol: ").strip()
    company_name = input("Enter the company name: ").strip()

    check_stock_percentage_change(stock_symbol, company_name, NEWS_API_KEY)


# Run the main function
if __name__ == "__main__":
    main()


