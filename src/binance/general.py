import requests

def ping_binance(BASE_URL):
    url = f"{BASE_URL}/api/v3/ping"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        return False
