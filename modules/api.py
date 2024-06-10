import requests
import time
import traceback
from modules.misc import get_name

import logging
import colorlog

# Настройка логирования с цветами
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - [%(levelname)s] - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

BASE_URL = 'https://api.hamsterkombat.io/clicker'
BUY_BOOST_URL = f'{BASE_URL}/buy-boost'
CHECK_TASK_URL = f'{BASE_URL}/check-task'
SYNC_URL = f'{BASE_URL}/sync'

# Покупка буста
def buy_boost(boost_id, headers, user_id):
    payload = {
        "boostId": boost_id,
        "timestamp": int(time.time())
    }
    response = requests.post(BUY_BOOST_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info(f'[{user_id}] Отправлен запрос на покупку буста: {boost_id}, ответ: {response.status_code}')
    else:
        logger.error(f'[{user_id}] Ошибка при покупке буста: {boost_id}, ответ: {response.status_code}')

# Проверка ежедневной задачи
def daily_check(headers, user_id):
    payload = {
        "taskId": "streak_days",
    }
    response = requests.post(CHECK_TASK_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info(f'[{user_id}] Отправлен запрос на ежедневную награду, ответ: {response.status_code}')
    else:
        logger.error(f'[{user_id}] Ошибка при запросе на ежедневную награду, ответ: {response.status_code}')

def get_boosts(generate_headers, token):
    time.sleep(5)
    while True:
        try:
            headers = generate_headers(token)
            user_id = get_name(token)
            buy_boost("BoostFullAvailableTaps", headers, user_id)
            daily_check(headers, user_id)
            time.sleep(3600)  # Спим 3600 секунд (1 час)
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
            time.sleep(5)

def get_user_info(generate_headers, token):
    headers = generate_headers(token)
    info = requests.post(SYNC_URL, headers=headers).json()
    user = info.get("clickerUser")
    user_id = user.get("id")
    available_taps = int(user.get("availableTaps"))
    passive_sec = user.get("earnPassivePerSec")
    passive_hour = user.get("earnPassivePerHour")
    balance = user.get("balanceCoins")
    return balance, user_id, available_taps, passive_sec, passive_hour

def get_upgrades(generate_headers,token):
    headers = generate_headers(token)
    info = requests.post("https://api.hamsterkombat.io/clicker/upgrades-for-buy", headers=headers).json()
    upgrades = info.get("upgradesForBuy")
    return info,upgrades


def send_word(word, generate_headers, token):
    headers = generate_headers(token)
    user_id = get_name(token)
    payload = {
        "cipher": word
    }
    response = requests.post("https://api.hamsterkombat.io/clicker/claim-daily-cipher", headers=headers, json=payload)
    if response.status_code == 200:
        logger.info(f'[{user_id}] Отправлен запрос на отгадку шифра, ответ: {response.status_code}')
    else:
        logger.error(f'[{user_id}] Ошибка при отгадке шифра, ответ: {response.status_code}')

def buy_upgrade(upgrade, headers, user_id):
    upgrade_id = upgrade.get("id")
    name = upgrade.get("name")
    price = int(upgrade.get("price"))
    profit = int(upgrade.get("profitPerHourDelta"))
    payload = {
        "upgradeId": upgrade_id,
        "timestamp": int(time.time())
    }
    response = requests.post("https://api.hamsterkombat.io/clicker/buy-upgrade", json=payload, headers=headers)
    if response.status_code == 200:
        logger.debug(f"[{user_id}][{name}] Куплено! | Цена: {price} | Профит/ч: {profit}")
        return True
    else:
        if "Insufficient funds" in response.text:
            logger.error(f"[{user_id}][{name}] Ошибка покупки, недостаточно средств.")
        else:
            logger.error(f"[{user_id}][{name}] Ошибка, код: {response.text}")
        return False
    time.sleep(2)
