import asyncio
import requests

BOT_API_KEY = "5902646689:AAFTBbITdTUjrqXCZuwhGcR1o893ybFttSc"
MY_CHANNEL_NAME = "@echo_library"


async def app_bot(message):
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
