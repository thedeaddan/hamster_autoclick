import requests
import time
import threading
import random
#Создайте файл token.py и в нем впишите 
# token = "ВАШ ТОКЕН ИЗ ЗАПРОСА"
from config import token

url = 'https://api.hamsterkombat.io/clicker/tap'
headers = {
    #'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'api.hamsterkombat.io',
    'Origin': 'https://hamsterkombat.io',
    'Referer': 'https://hamsterkombat.io/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'accept': 'application/json',
    'authorization': f'Bearer {token}',
    'content-type': 'application/json',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def buy_boost(boost):
    url = "https://api.hamsterkombat.io/clicker/buy-boost"  

    payload = {
            "boostId": boost,
            "timestamp": int(time.time())  
        }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Отправлен запрос на покупку буста: {boost}, ответ: {response.status_code}")

def dayly_check():
    url = "https://api.hamsterkombat.io/clicker/check-task"  

    payload = {
            "taskId": "streak_days",
        }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Отправлен запрос на ежедневную награду, ответ: {response.status_code}")


def periodic_post_request():
    while True:
        buy_boost("BoostFullAvailableTaps")
        dayly_check()
        time.sleep(3600)  # Спим 3600 секунд (1 час)

# Создаем и запускаем поток
post_thread = threading.Thread(target=periodic_post_request)
post_thread.start()


balance = 0
while True:
    info = requests.post("https://api.hamsterkombat.io/clicker/sync", headers=headers).json()
    availableTaps = int(info.get("clickerUser").get("availableTaps"))
    passive_sec = info.get("clickerUser").get("earnPassivePerSec")
    passive_hour = info.get("clickerUser").get("earnPassivePerHour")
    old_balance = balance
    if availableTaps > 500:
        availableTaps = random.randint(10,100)
    payload = {
            "count": availableTaps,
            "availableTaps": 0,
            "timestamp": int(time.time())  
        }
    response = requests.post(url, headers=headers, json=payload)
    json_data = response.json()
    balance = int(json_data.get('clickerUser').get('balanceCoins'))
    # Выводим результат
    print("="*10)
    print(f"Баланс: {balance} мон. | Заработок в сек/час : {int(passive_sec)}/{int(passive_hour)} мон.")
    print(f"Кликов отправлено: {availableTaps}")
    
    #print(json.dumps(json_data, indent=4))
    if response.status_code == 200:
        wait = random.randint(7,20)
    else:
        print(f"Внимание! Статус-код: {response.status_code}! Ожидание повышено.")
        wait = random.randint(300,600)
    print(f"Ожидание: {wait} сек.")
    time.sleep(wait)
