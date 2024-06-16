import requests
import time
import threading
import random
from modules.misc import *
from config import *
from modules.api import *

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


# Константы для URL
BASE_URL = 'https://api.hamsterkombat.io/clicker'
TAP_URL = f'{BASE_URL}/tap'

logger.info(f"Стратегия покупки: {buy_type}")

def get_profit_upgrades(token):
    while True:
        try:
            user_id = get_name(token)
            headers = generate_headers(token)
            upgrades = get_upgrades(generate_headers,token)[1]
            if get_buy_status(token):
                if buy_type == "benefit":
                    process_upgrades_by_benefit(upgrades, headers, user_id,token)
                elif buy_type == "cheap":
                    process_upgrades_by_price(upgrades, headers, user_id,token)
                elif buy_type == "profit":
                    process_upgrades_by_profit(upgrades, headers, user_id,token)

                time.sleep(1)
            else:
                time.sleep(10)
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
            time.sleep(5)

def process_upgrades_by_benefit(upgrades, headers, user_id,token):
    for upgrade in upgrades:
        profit = int(upgrade.get("profitPerHourDelta"))
        price = int(upgrade.get("price"))
        if should_buy_upgrade(upgrade) and calc_profit(profit_percent_global, price, profit) and check_balance(token,price):
            buy_upgrade(upgrade, headers, user_id)

def process_upgrades_by_price(upgrades, headers, user_id,token):
    upgrades = sorted(upgrades, key=lambda x: x['price'])
    for upgrade in upgrades:
        if should_buy_upgrade(upgrade):
            price = int(upgrade.get("price"))
            if check_balance(token,price):
                buy_upgrade(upgrade, headers, user_id)
                break

def process_upgrades_by_profit(upgrades, headers, user_id,token):
    upgrades = sorted(upgrades, key=lambda x: x['profitPerHour'], reverse=True)
    for upgrade in upgrades:
        if should_buy_upgrade(upgrade):
            price = int(upgrade.get("price"))
            if check_balance(token,price):
                buy_upgrade(upgrade, headers, user_id)
                break

def should_buy_upgrade(upgrade):
    unlocked = upgrade.get("isAvailable")
    expired = upgrade.get("isExpired")
    price = int(upgrade.get("price"))
    return (
        not expired and
        not check_maxlevel(upgrade) and
        check_cooldown(upgrade) and
        price <= cheap_limit and
        unlocked
    )

def check_balance(token,price):
    balance = get_user_info(generate_headers,token)[0]
    if balance > price:
        return True
    else:
        return False
    

def buy_daily_cards(token):
    user_cards = []
    user_cards += daily_cards
    while True: 
        upgrades_price = []
        upgrades_id = []
        info, upgrades = get_upgrades(generate_headers,token)
        user_id = get_name(token)
        unlocked_cards = info.get("dailyCombo").get("upgradeIds")
        logger.debug(f"[{user_id}] Карты: {unlocked_cards}")
        
        if len(unlocked_cards) == 3:
            send_daily(generate_headers,token)
            break
        else:
            for upgrade in upgrades:
                upgrade_name = upgrade.get("name")
                upgrade_price = upgrade.get("price")
                upgrade_id = upgrade.get("id")
                for card in user_cards:
                    if upgrade_name.lower() == card.lower():
                        if upgrade_id in unlocked_cards and unlocked_cards != []:
                            logger.warning(f"[{user_id}] Ежедневная карта {card} уже куплена.")
                            user_cards.remove(card)
                        else:
                            upgrades_id.append(upgrade)
                            upgrades_price.append(upgrade_price)

            buy = True
            locked_cards = []
            for upgrade in upgrades_id:
                if upgrade.get("isAvailable") == True:
                    pass
                else:
                    buy = False
                    locked_cards.append(upgrade.get("name"))
            if buy:                
                if sum(upgrades_price) > 4900000:
                    logger.warning(f"[{user_id}] Стоимость карт больше 4,9 млн. Покупка ежедневных карт не выгодна.")
                    break
                else:
                    for upgrade in upgrades_id:
                        buy_upgrade(upgrade,generate_headers(token),user_id+"_daily")
            else:
                logger.warning(f"[{user_id}] Для покупки ежедневных карт требуется разблокировка карт: {locked_cards}")
                time.sleep(60)
        

def create_thread(token):
    time.sleep(10)
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post(SYNC_URL, headers=headers)
            response.raise_for_status()
            info = response.json()
            user = info.get("clickerUser")
            available_taps = int(user.get("availableTaps"))
            passive_hour = user.get("earnPassivePerHour")
            user_id = get_name(token)

            if available_taps > 500:
                available_taps = random.randint(500, 3000)

            payload = {
                "count": available_taps,
                "availableTaps": 0,
                "timestamp": int(time.time())
            }
            response = requests.post(TAP_URL, headers=headers, json=payload)
            response.raise_for_status()

            json_data = response.json()
            balance = int(json_data.get('clickerUser').get('balanceCoins'))

            logger.info("=" * 20 + f" {user_id} " + "=" * 20)
            logger.info(f"Баланс: {format_number_with_dots(balance)} мон. | Заработок в час: {format_number_with_dots(passive_hour)} мон.")
            logger.info(f"Кликов отправлено: {available_taps}")

            wait = random.randint(7, 20) if response.status_code == 200 else random.randint(300, 600)
            if response.status_code != 200:
                logger.warning(f"Внимание! Статус-код: {response.status_code}! Ожидание повышено.")
            logger.info(f"Ожидание: {wait} сек.")
            time.sleep(wait)
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
            time.sleep(5)



# Запуск потоков для каждого токена
for token in tokens:
    send_word(word, generate_headers, token)
    threading.Thread(target=get_boosts, args=(generate_headers, token,)).start()
    threading.Thread(target=get_profit_upgrades, args=(token,)).start()
    threading.Thread(target=create_thread, args=(token,)).start()
    threading.Thread(target=buy_daily_cards, args=(token,)).start()
