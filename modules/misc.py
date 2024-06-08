from config import names,tokens
def calc_profit(profit_percent_global,price,profit_per_hour):
    if price != 0 and profit_per_hour != 0:
        profit_percent = price/10/profit_per_hour*100
        if profit_percent <= profit_percent_global:
            return True
        else:
            return False
    else:
        return False

def check_maxlevel(upgrade):
    try:
        level = upgrade.get("condition").get("level")
        if upgrade.get("maxLevel") == level:
            return True
        else:
            False
    except:
        return False
    
def check_cooldown(upgrade):
    if upgrade.get("cooldownSeconds") != None and upgrade.get("cooldownSeconds") != 0:
        return False
    else:
        return True
    
# Генерация заголовков для запроса
def generate_headers(token):
    return {
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

def get_name(token):
    return names[tokens.index(token)]