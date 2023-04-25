import asyncio
import requests

BOT_API_KEY = "5902646689:AAFTBbITdTUjrqXCZuwhGcR1o893ybFttSc"
MY_CHANNEL_NAME = "@echo_library"


async def bot_notification(message):
    response = requests.get(
        f"https://api.telegram.org/bot{BOT_API_KEY}/sendMessage",
        {
            "chat_id": MY_CHANNEL_NAME,
            "text": f"Username --> {message.get('username', 'No username provided')}\n"
            f"Books taken --> {message.get('borrowed_book')}\n"
            f"Total price: {message.get('total_price')} UAH"
        }
    )

    if response.status_code == 200:
        print(f"Borrowing creating successfully sended to channel  --> {MY_CHANNEL_NAME}  <-- ")
    else:
        print(response.text)


async def bot_borrowing_message(
    book_info: tuple,
    user_data: tuple,
    borrowing_date: str,
    borrowing_return: str,
):
    response = requests.get(
        f"https://api.telegram.org/bot{BOT_API_KEY}/sendMessage",
        {
            "chat_id": MY_CHANNEL_NAME,
            "text": "===== User info =====\n"
            f"Username: {user_data[1]}\n"
            f"User-email: {user_data[0]}\n"
            f"===== Borrowed book ====\n"
            f"Book title: {book_info[0]}\n"
            f"Author: {book_info[2]}\n"
            f"Price: {book_info[1]} $\n"
            f"==== Time info ====\n"
            f"Borrowing date: {borrowing_date}\n"
            f"Returning date: {borrowing_return}"
        }
    )

    if response.status_code == 200:
        print(f"Borrowing data successfully sended to channel  --> {MY_CHANNEL_NAME}  <-- ")
    else:
        print(response.text)