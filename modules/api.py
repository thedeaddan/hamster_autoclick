import requests
import time

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
    print(f'[{user_id}] Отправлен запрос на покупку буста: {boost_id}, ответ: {response.status_code}')

# Проверка ежедневной задачи
def daily_check(headers, user_id):
    payload = {
        "taskId": "streak_days",
    }
    response = requests.post(CHECK_TASK_URL, headers=headers, json=payload)
    print(f'[{user_id}] Отправлен запрос на ежедневную награду, ответ: {response.status_code}')

def get_boosts(generate_headers,token):
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post(SYNC_URL, headers=headers)
            if response.status_code in [200,400]:
                info = response.json()
                user_id = info.get("clickerUser").get("id")
                buy_boost("BoostFullAvailableTaps", headers, user_id)
                daily_check(headers, user_id)
                time.sleep(3600)  # Спим 3600 секунд (1 час)
        except:
            pass

def get_user_info(generate_headers,token):
    headers = generate_headers(token)
    info = requests.post(SYNC_URL, headers=headers).json()
    user = info.get("clickerUser")
    user_id = user.get("id")
    available_taps = int(user.get("availableTaps"))
    passive_sec = user.get("earnPassivePerSec")
    passive_hour = user.get("earnPassivePerHour")
    return user,user_id,available_taps,passive_sec,passive_hour