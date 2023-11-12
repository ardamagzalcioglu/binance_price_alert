from binance.client import Client
from binance import exceptions
import requests
from telegram import Update,KeyboardButton,ReplyKeyboardMarkup,ReplyMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

api_key = 'IMvgRj4ypRCwW9rKuIL9ZKynWmB9DbmmKdzJZ49EMF3Z9dSOm1sZSn6zRDY4kTe1'
api_secret = 'eSW3UVmq0FgNpcJUWAtlNM0E7ZSvWJKscmcSNErP0bbKkvWDruSRs0VUwpcPKDPZ'
bot_token ="6676473175:AAEej6wXo2KvtKSTlqjk8CERCWuqbnAF6gY"

client = Client(api_key, api_secret)
user_id=1246307492

# Dictionary to store user-specific target prices
data= {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! You can use /addticker to add a new ticker and target price.")

def add_ticker(update: Update, context: CallbackContext):
    update.message.reply_text("Enter the ticker and target price in the format: ticker target_price (BTCUSDT 34500)")

def handle_ticker_input(update: Update, context: CallbackContext):
    try:
        user_id_given= update.message.from_user.id

        if user_id_given==user_id:

            try:

                user_input = update.message.text.split()

                if len(user_input) == 2:
                    ticker, target_price = user_input

                    ticker=ticker.upper()
                    ticker_info = client.get_ticker(symbol=ticker)
                    if ticker not in data:
                        data[ticker]=[]
                    current_price = float(ticker_info['lastPrice'])

                    data[ticker].append([float(target_price),float(current_price)])
                    update.message.reply_text(f"Ticker {ticker} added with a target price of {target_price}.")
                    print(data)
                else:
                    update.message.reply_text("Invalid input. Please use the format: ticker target_price")


            except exceptions.BinanceAPIException:
                update.message.reply_text(("You entered wrong symbol-ticker"))

        else:
            update.message.reply_text("You are not allowed to use this bot")
    except AttributeError:
        update.message.reply_text(("You entered wrong type"))

def price_alert(context: CallbackContext):
      # Assuming there's only one user
    try:
        for symbol in data:
            ticker_info = client.get_ticker(symbol=symbol)
            current_price = float(ticker_info['lastPrice'])
            for alert in data[symbol]:
                print(data)
                [target_price,alert_entry_price]=alert
                if alert_entry_price<target_price and current_price>target_price:
                    context.bot.send_message(chat_id=-1002056436889, text=f"Alert: {symbol} has reached or exceeded the target price of {target_price}")
                    data[symbol].remove(alert)
                elif alert_entry_price>target_price and current_price<target_price:
                    context.bot.send_message(chat_id=-1002056436889,
                                             text=f"Alert: {symbol} has reached or dropped the target price of {target_price}")
                    data[symbol].remove(alert)
    except Exception as e:
        if e is exceptions.BinanceAPIException:
            print("fsdfds")

def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('addticker', add_ticker))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_ticker_input))

    # Set up price alert job to run every minute
    updater.job_queue.run_repeating(price_alert, interval=20, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()