from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from datetime import datetime
import requests, random, time, os

URL = "https://testnet.explorer.modulr.cloud/api/faucet"

# User Agents list (တူညီသောကြောင့် အတိုချုံ့ထားပါသည်)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
]

print_lock = Lock()

class Colors:
    RESET, BOLD, RED, GREEN, YELLOW, BLUE, CYAN, GRAY = "\033[0m", "\033[1m", "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[96m", "\033[90m"

def log_msg(type_color, label, message):
    with print_lock:
        print(f"{type_color}[{label}]{Colors.RESET} {Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET} {message}")

def get_headers():
    return {
        "Content-Type": "application/json",
        "Origin": "https://testnet.explorer.modulr.cloud",
        "Referer": "https://testnet.explorer.modulr.cloud/faucet",
        "User-Agent": random.choice(USER_AGENTS)
    }

def faucet_request(address, proxy=None):
    payload = {"address": address}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        response = requests.post(URL, json=payload, headers=get_headers(), proxies=proxies, timeout=20)
        if response.status_code == 200 and response.json().get("status") == "ok":
            log_msg(Colors.GREEN, "SUCCESS", f"Address: {address[:10]}... | Proxy: {proxy if proxy else 'None'}")
        else:
            log_msg(Colors.YELLOW, "WARNING", f"Failed: {address[:10]}... | {response.text[:50]}")
    except Exception as e:
        log_msg(Colors.RED, "ERROR", f"Error for {address[:10]}... | {type(e).__name__}")

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    print(f"{Colors.CYAN}{'='*40}\n   Modulr Auto Faucet (Multi-Wallet)\n{'='*40}{Colors.RESET}")
    
    wallets = load_file("wallets.txt")
    proxies = load_file("proxy.txt")

    if not wallets:
        log_msg(Colors.RED, "ERROR", "wallets.txt not found or empty!")
        return

    log_msg(Colors.CYAN, "INFO", f"Loaded {len(wallets)} wallets and {len(proxies)} proxies.")
    threads = int(input(f"{Colors.BOLD}Enter number of threads: {Colors.RESET}"))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for addr in wallets:
            proxy = random.choice(proxies) if proxies else None
            executor.submit(faucet_request, addr, proxy)

if __name__ == "__main__":
    main()
