from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
from datetime import datetime

class Colors:
    RESET, RED, GREEN, YELLOW, CYAN, GRAY = "\033[0m", "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[90m"

def log_msg(type_color, label, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{type_color}[{label}]{Colors.RESET} {Colors.GRAY}[{timestamp}]{Colors.RESET} {message}")

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def run_faucet(address, proxy=None):
    co = ChromiumOptions()
    
    # Proxy ရှိလျှင် ထည့်ရန်
    if proxy:
        co.set_proxy(proxy)
    
    # Browser ကို မမြင်ရအောင် run ချင်လျှင် အောက်က line ကို comment ဖြုတ်ပါ
    # co.headless() 

    page = ChromiumPage(co)
    try:
        log_msg(Colors.CYAN, "INFO", f"Processing: {address[:15]}...")
        page.get('https://testnet.explorer.modulr.cloud/faucet')
        
        # Input field ကို ရှာပြီး address ထည့်မည်
        # Selector ကို screenshot ပါ အတိုင်း label/placeholder ဖြင့် ရှာသည်
        input_field = page.ele('@placeholder=Enter your address')
        if not input_field:
            input_field = page.ele('tag:input')

        input_field.input(address)
        time.sleep(1)

        # Submit button ကို နှိပ်မည်
        btn = page.ele('tag:button@@text():Send')
        if btn:
            btn.click()
            log_msg(Colors.CYAN, "WAIT", "Button clicked, waiting for response...")
            time.sleep(5) # Response စောင့်ရန်

            # အောင်မြင်မှု ရှိမရှိ စစ်ဆေးခြင်း
            if "Successfully" in page.html or "ok" in page.html.lower():
                log_msg(Colors.GREEN, "SUCCESS", f"Sent to {address[:10]}...")
            else:
                log_msg(Colors.YELLOW, "STATUS", "Check browser for limit/error message.")
    except Exception as e:
        log_msg(Colors.RED, "ERROR", f"Failed: {str(e)[:50]}")
    finally:
        page.quit()

def main():
    wallets = load_file("wallets.txt")
    proxies = load_file("proxy.txt")

    if not wallets:
        print("wallets.txt is empty!")
        return

    print(f"Loaded {len(wallets)} wallets. Starting browser automation...")

    for i, addr in enumerate(wallets):
        proxy = proxies[i % len(proxies)] if proxies else None
        run_faucet(addr, proxy)
        # ဇောက်ထိုးမဖြစ်အောင် ခေတ္တနားမည်
        time.sleep(2)

if __name__ == "__main__":
    main()
