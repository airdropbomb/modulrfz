import cloudscraper
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from datetime import datetime

# URL for Modulr Faucet API
URL = "https://testnet.explorer.modulr.cloud/api/faucet"

# Standard User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
]

print_lock = Lock()

class Colors:
    RESET, BOLD, RED, GREEN, YELLOW, CYAN, GRAY = "\033[0m", "\033[1m", "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[90m"

def log_msg(type_color, label, message):
    with print_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{type_color}[{label}]{Colors.RESET} {Colors.GRAY}[{timestamp}]{Colors.RESET} {message}")

def get_headers():
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://testnet.explorer.modulr.cloud",
        "Referer": "https://testnet.explorer.modulr.cloud/faucet",
        "User-Agent": random.choice(USER_AGENTS)
    }

def faucet_request(address, proxy=None):
    # Create a scraper instance to bypass Cloudflare
    scraper = cloudscraper.create_scraper()
    payload = {"address": address}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        # Standard timeout set to 20s
        response = scraper.post(URL, json=payload, headers=get_headers(), proxies=proxies, timeout=20)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "ok":
                    log_msg(Colors.GREEN, "SUCCESS", f"{address[:10]}... | Claimed successfully!")
                else:
                    log_msg(Colors.YELLOW, "FAILED", f"{address[:10]}... | Msg: {data.get('message', 'Limit reached')}")
            except:
                log_msg(Colors.RED, "ERROR", f"Cloudflare blocked the request (HTML returned).")
        elif response.status_code == 429:
            log_msg(Colors.YELLOW, "RATE-LIMIT", f"IP or Wallet limited: {address[:10]}...")
        else:
            log_msg(Colors.RED, "ERROR", f"HTTP {response.status_code} for {address[:10]}...")
            
    except Exception as e:
        log_msg(Colors.RED, "ERROR", f"Connection error: {str(e)[:50]}")

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    print(f"{Colors.CYAN}{'='*50}\n   Modulr Auto Faucet - Multi-Wallet Mode\n{'='*50}{Colors.RESET}")
    
    wallets = load_file("wallets.txt")
    proxies = load_file("proxy.txt")

    if not wallets:
        log_msg(Colors.RED, "CRITICAL", "wallets.txt is empty! Add addresses first.")
        return

    log_msg(Colors.CYAN, "INFO", f"Loaded {len(wallets)} wallets and {len(proxies)} proxies.")
    
    try:
        thread_count = int(input(f"{Colors.BOLD}Enter number of threads: {Colors.RESET}"))
    except ValueError:
        thread_count = 1

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for addr in wallets:
            proxy = random.choice(proxies) if proxies else None
            executor.submit(faucet_request, addr, proxy)
            # Request တွေကြားထဲ ခဏနားပေးခြင်းဖြင့် block ခံရမှုကို လျှော့ချနိုင်သည်
            time.sleep(1) 

    log_msg(Colors.CYAN, "DONE", "All requests processed.")

if __name__ == "__main__":
    main()
