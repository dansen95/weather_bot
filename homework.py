import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

handlers = [logging.FileHandler(filename="./main.log", encoding='utf-8')]
logging.basicConfig(
    handlers=handlers,
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

TOKEN = os.getenv('TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://api.weather.yandex.ru/v2/forecast?lat=59.9311&lon=30.3609'


def parse_weather_status(fact):
    try:
        temp = fact['temp']
        condition = fact['condition']
        feels_like = fact['feels_like']
        wind_speed = fact['wind_speed']
        verdict = f'Today in Saint-Petersburg {temp} degrees, feels like {feels_like}, {condition}, wind speed {wind_speed}'

        return verdict

    except (KeyError, ValueError) as e:
        logging.error(msg=f'Ошибка: {e}')
        return f'Ошибка: {e}'


def get_weather_status(current_timestamp):
    headers = {
        'X-Yandex-API-Key': f'{TOKEN}',
    }
    
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp,
    }
    try:
        weather_statuses = requests.get(
            API_URL, params=params, headers=headers
        )

        return weather_statuses.json()

    except requests.RequestException as error:
        raise error


def send_message(message, bot_client):
    logging.info('Отправлено сообщение в чат Telegram')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=str(TELEGRAM_TOKEN))
    logging.debug('Запуск Telegram-бота')
    current_timestamp = int(time.time())

    while True:
        try:
            new_weather = get_weather_status(current_timestamp)
            if new_weather.get('fact'):
                send_message(
                    parse_weather_status(new_weather.get('fact')),
                    bot_client
                )
            current_timestamp = new_weather.get(
                'now_dt',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.exception(msg=f'Ошибка: {e}')
            send_message(e, bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
