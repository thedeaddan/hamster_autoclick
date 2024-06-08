import requests
import time
import threading
import random
import traceback
from modules.misc import *
from config import *
from modules.api import *

# Константы для URL
BASE_URL = 'https://api.hamsterkombat.io/clicker'
TAP_URL = f'{BASE_URL}/tap'




def get_profit_upgrades(token):
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post("https://api.hamsterkombat.io/clicker/upgrades-for-buy", headers=headers)
            info = requests.post(SYNC_URL, headers=headers).json()
            user = info.get("clickerUser")
            user_id = user.get("id")
            upgrades = response.json().get("upgradesForBuy")            
            if buy_type == "benefit":
                for upgrade in upgrades:
                    profit = int(upgrade.get("profitPerHourDelta"))
                    price = int(upgrade.get("price"))
                    name = upgrade.get("name")
                    upgrade_id = upgrade.get("id")
                    unlocked = upgrade.get("isAvailable")
                    expired = upgrade.get("isExpired")
                    if calc_profit(profit_percent_global,price,profit) and not expired and not check_maxlevel(upgrade) and check_cooldown(upgrade) and price <= cheap_limit:
                        if unlocked:
                            payload = {
                                "upgradeId": upgrade_id,
                                "timestamp": int(time.time())
                            }
                            response = requests.post("https://api.hamsterkombat.io/clicker/buy-upgrade", json = payload, headers=headers)
                            if response.status_code == 200:
                                print(f"[{user_id}][{name}] Куплено! | Цена: {price} | Профит/ч: {profit}")
                            else:
                                print(f"[{user_id}][{name}] Ошибка, код: {response.status_code}")
                            time.sleep(2)
            elif buy_type == "cheap":
                upgrades = sorted(upgrades, key=lambda x: x['price'])
                for upgrade in upgrades:
                    profit = int(upgrade.get("profitPerHourDelta"))
                    price = int(upgrade.get("price"))
                    name = upgrade.get("name")
                    upgrade_id = upgrade.get("id")
                    unlocked = upgrade.get("isAvailable")
                    expired = upgrade.get("isExpired")
                    if not expired and not check_maxlevel(upgrade) and check_cooldown(upgrade) and price <= cheap_limit:
                        if unlocked:
                            payload = {
                                "upgradeId": upgrade_id,
                                "timestamp": int(time.time())
                            }
                            response = requests.post("https://api.hamsterkombat.io/clicker/buy-upgrade", json = payload, headers=headers)
                            if response.status_code == 200:
                                print(f"[{user_id}][{name}] Куплено! | Цена: {price} | Профит/ч: {profit}")
                            else:
                                print(f"[{user_id}][{name}] Ошибка, код: {response.status_code}")
                            time.sleep(2)
            elif buy_type == "profit":
                upgrades = sorted(upgrades, key=lambda x: x['profitPerHour'],reverse=True)
                for upgrade in upgrades:
                    profit = int(upgrade.get("profitPerHourDelta"))
                    price = int(upgrade.get("price"))
                    name = upgrade.get("name")
                    upgrade_id = upgrade.get("id")
                    unlocked = upgrade.get("isAvailable")
                    expired = upgrade.get("isExpired")
                    if not expired and not check_maxlevel(upgrade) and check_cooldown(upgrade) and price <= cheap_limit:
                        if unlocked:
                            payload = {
                                "upgradeId": upgrade_id,
                                "timestamp": int(time.time())
                            }
                            response = requests.post("https://api.hamsterkombat.io/clicker/buy-upgrade", json = payload, headers=headers)
                            if response.status_code == 200:
                                print(f"[{user_id}][{name}] Куплено! | Цена: {price} | Профит/ч: {profit}")
                            else:
                                print(f"[{user_id}][{name}] Ошибка, код: {response.status_code}")
                            time.sleep(2)
            time.sleep(3)
        except:
            print(traceback.format_exc())
            pass
            
# Создание потока для выполнения запросов
def create_thread(token):
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post(SYNC_URL, headers=headers)
            if response.status_code == 200:
                info = response.json()
                user = info.get("clickerUser")
                available_taps = int(user.get("availableTaps"))
                passive_sec = user.get("earnPassivePerSec")
                passive_hour = user.get("earnPassivePerHour")
                user_id = user.get("id")

                if available_taps > 500:
                    available_taps = random.randint(500, 3000)

                payload = {
                    "count": available_taps,
                    "availableTaps": 0,
                    "timestamp": int(time.time())
                }
                response = requests.post(TAP_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    json_data = response.json()
                    balance = int(json_data.get('clickerUser').get('balanceCoins'))

                    # Вывод результата
                    print("=" * 5, f"Юзер {user_id}", "=" * 5)
                    print(f"Баланс: {balance} мон. | Заработок в сек/час: {int(passive_sec)}/{int(passive_hour)} мон.")
                    print(f"Кликов отправлено: {available_taps}")

                    if response.status_code == 200:
                        wait = random.randint(7, 20)
                    else:
                        print(f"Внимание! Статус-код: {response.status_code}! Ожидание повышено.")
                        wait = random.randint(300, 600)
                    print(f"Ожидание: {wait} сек.")
                    time.sleep(wait)
        except:
            print(response.text)

# Запуск потоков для каждого токена
for token in tokens:
    # threading.Thread(target=create_thread, args=(token,)).start()
    # threading.Thread(target=get_boosts, args=(generate_headers,token,)).start()
    threading.Thread(target=get_profit_upgrades, args=(token,)).start()
