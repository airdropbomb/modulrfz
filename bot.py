import cloudscraper
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from datetime import datetime

# URL for Modulr Faucet API
URL = "https://testnet.explorer.modulr.cloud/api/faucet"

print_lock = Lock()

class Colors:
    RESET, BOLD, RED, GREEN, YELLOW, CYAN, GRAY = "\033[0m", "\033[1m", "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[90m"

def log_msg(type_color, label, message):
    with print_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{type_color}[{label}]{Colors.RESET} {Colors.GRAY}[{timestamp}]{Colors.RESET} {message}")

def get_headers():
    # Screenshot ပါ Request Headers များအတိုင်း အတိအကျ ပြင်ဆင်ထားသည်
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://testnet.explorer.modulr.cloud",
        "Priority": "u=1, i",
        "Referer": "https://testnet.explorer.modulr.cloud/faucet",
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Herond";v="138"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Gpc": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

def faucet_request(address, proxy=None):
    # Cloudflare bypass အတွက် scraper ကို သုံးသည်
    scraper = cloudscraper.create_scraper()
    payload = {"address": address}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        # POST Request ပို့ခြင်း
        response = scraper.post(URL, json=payload, headers=get_headers(), proxies=proxies, timeout=20)
        
        # Status Code 200 ဆိုလျှင် အောင်မြင်သည်
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "ok":
                    log_msg(Colors.GREEN, "SUCCESS", f"{address[:10]}... | Claimed successfully!")
                else:
                    # Rate limit သို့မဟုတ် တစ်ခြား error ပြန်လာခြင်း
                    log_msg(Colors.YELLOW, "FAILED", f"{address[:10]}... | Msg: {data.get('message', 'Already claimed or limited')}")
            except:
                log_msg(Colors.RED, "ERROR", f"Cloudflare/Server returned HTML instead of JSON.")
        elif response.status_code == 429:
            log_msg(Colors.YELLOW, "RATE-LIMIT", f"IP or Wallet limited: {address[:10]}...")
        else:
            log_msg(Colors.RED, "ERROR", f"HTTP {response.status_code} | {response.text[:50]}")
            
    except Exception as e:
        log_msg(Colors.RED, "ERROR", f"Connection error: {str(e)[:50]}")

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    print(f"{Colors.CYAN}{'='*50}\n   Modulr Auto Faucet - Updated Headers\n{'='*50}{Colors.RESET}")
    
    wallets = load_file("wallets.txt")
    proxies = load_file("proxy.txt")

    if not wallets:
        log_msg(Colors.RED, "CRITICAL", "wallets.txt is empty!")
        return

    log_msg(Colors.CYAN, "INFO", f"Loaded {len(wallets)} wallets and {len(proxies)} proxies.")
    
    try:
        thread_count = int(input(f"{Colors.BOLD}Enter number of threads: {Colors.RESET}"))
    except ValueError:
        thread_count = 1

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for addr in wallets:
            # Proxy တစ်ခုကို random ရွေးသုံးမည်
            proxy = random.choice(proxies) if proxies else None
            executor.submit(faucet_request, addr, proxy)
            # IP block မခံရအောင် ၁ စက္ကန့်ခြားပြီး ပို့ပေးမည်
            time.sleep(1.5) 

    log_msg(Colors.CYAN, "DONE", "All requests processed.")

if __name__ == "__main__":
    main()
