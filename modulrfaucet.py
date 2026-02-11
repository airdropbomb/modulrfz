from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from datetime import datetime
import requests, random, time

URL = "https://testnet.explorer.modulr.cloud/api/faucet"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
]

print_lock = Lock()

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log_info(message):
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} {Colors.GRAY}[{get_timestamp()}]{Colors.RESET} {message}")

def log_success(message, index=None, total=None):
    prefix = f"[{index}/{total}] " if index else ""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {Colors.GRAY}[{get_timestamp()}]{Colors.RESET} {prefix}{message}")

def log_error(message, index=None, total=None):
    prefix = f"[{index}/{total}] " if index else ""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {Colors.GRAY}[{get_timestamp()}]{Colors.RESET} {prefix}{message}")

def log_warning(message, index=None, total=None):
    prefix = f"[{index}/{total}] " if index else ""
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {Colors.GRAY}[{get_timestamp()}]{Colors.RESET} {prefix}{message}")

def get_headers():
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Origin": "https://testnet.explorer.modulr.cloud",
        "Pragma": "no-cache",
        "Referer": "https://testnet.explorer.modulr.cloud/faucet",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": random.choice(USER_AGENTS)
    }

def faucet_request(address, index=None, total=None):
    payload = {"address": address}
    headers = get_headers()

    try:
        start_time = time.time()
        response = requests.post(URL, json=payload, headers=headers, timeout=20)
        elapsed = round(time.time() - start_time, 2)

        with print_lock:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    log_success(f"Request completed in {elapsed}s | Response: {data}", index, total)
                else:
                    log_warning(f"Request returned non-ok status | Response: {data}", index, total)
            else:
                log_error(f"HTTP {response.status_code} | Response: {response.text[:200]}", index, total)

    except requests.exceptions.Timeout:
        with print_lock:
            log_error("Request timeout after 20s", index, total)
    except requests.exceptions.RequestException as e:
        with print_lock:
            log_error(f"Request failed | {type(e).__name__}: {str(e)}", index, total)
    except Exception as e:
        with print_lock:
            log_error(f"Unexpected error | {type(e).__name__}: {str(e)}", index, total)

def run_threaded(address, total_threads):
    log_info(f"Starting {total_threads} concurrent requests to faucet")
    log_info(f"Target address: {Colors.YELLOW}{address}{Colors.RESET}")
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=total_threads) as executor:
        futures = [executor.submit(faucet_request, address, i, total_threads) for i in range(1, total_threads + 1)]
        for future in futures:
            future.result()
    
    elapsed = round(time.time() - start_time, 2)
    log_info(f"All requests completed in {elapsed}s")

def run_single(address):
    log_info("Starting single request to faucet")
    log_info(f"Target address: {Colors.YELLOW}{address}{Colors.RESET}")
    faucet_request(address)

def print_banner():
    banner = f"""
{Colors.CYAN}{'='*60}
{Colors.BOLD}         Modulr Testnet Faucet Request Tool{Colors.RESET}
{Colors.CYAN}{'='*60}{Colors.RESET}
"""
    print(banner)

def get_address():
    while True:
        address = input(f"\n{Colors.BOLD}Enter your wallet address:{Colors.RESET} ").strip()
        if address:
            return address
        else:
            log_error("Address cannot be empty")

def main():
    print_banner()
    
    address = get_address()
    
    while True:
        print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
        print(f"  {Colors.GREEN}[y]{Colors.RESET} Multi-threaded mode")
        print(f"  {Colors.YELLOW}[n]{Colors.RESET} Single request mode")
        print(f"  {Colors.MAGENTA}[c]{Colors.RESET} Change address")
        print(f"  {Colors.RED}[q]{Colors.RESET} Quit program")
        
        mode = input(f"\n{Colors.BOLD}Select mode:{Colors.RESET} ").strip().lower()

        if mode == "q":
            log_info("Exiting program")
            break

        elif mode == "c":
            address = get_address()

        elif mode == "y":
            try:
                total = int(input(f"{Colors.BOLD}Enter number of threads:{Colors.RESET} "))
                if total <= 0:
                    log_error("Thread count must be positive")
                    continue
                run_threaded(address, total)
            except ValueError:
                log_error("Invalid input, please enter a valid number")

        elif mode == "n":
            run_single(address)

        else:
            log_error("Invalid input, please select y, n, c, or q")

if __name__ == "__main__":
    main()