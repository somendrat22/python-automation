import os
import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager

# Function to connect to VPN using OpenVPN
def connect_to_vpn(config_path):
    print(f"Connecting to VPN with config: {config_path}")
    disconnect_vpn()  # Disconnect any active VPN
    process = subprocess.Popen(
        ["sudo", "openvpn", "--config", config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(10)  # Allow time for the VPN to connect (can be replaced with a check)
    return process

# Function to disconnect VPN
def disconnect_vpn():
    subprocess.run(["sudo", "killall", "openvpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Disconnected from VPN.")

@contextmanager
def vpn_connection(config_path):
    process = connect_to_vpn(config_path)
    try:
        yield
    finally:
        disconnect_vpn()
        if process:
            process.terminate()

# Function to get the current public IP address
def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text  # You can also use 'https://checkip.amazonaws.com'
        return ip
    except requests.RequestException as e:
        print(f"Error getting IP address: {e}")
        return None

# Function to initialize WebDriver with retries
def initialize_webdriver():
    retries = 3
    for attempt in range(retries):
        try:
            print(f"Initializing WebDriver (Attempt {attempt + 1}/{retries})...")
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Do not use headless mode for troubleshooting
            # options.add_argument("--headless=new")  # Uncomment this to run headlessly

            # Automatically download the correct chromedriver version based on installed Chrome
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),  # Automatically handles version matching
                options=options
            )
            return driver
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(5)  # Wait before retrying

# Function to perform searches on DuckDuckGo
def search_duckduckgo(keywords):
    driver = None
    try:
        driver = initialize_webdriver()
        driver.get("https://duckduckgo.com")

        # Get and display current public IP before searching
        current_ip = get_public_ip()
        if current_ip:
            print(f"Current public IP address: {current_ip}")
        else:
            print("Could not determine public IP address.")

        for keyword in keywords:
            print(f"Searching for: {keyword}")
            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)

            # Explicit wait for results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#links"))
            )
            time.sleep(2)  # Pause between searches for user simulation

        print("Searches completed.")
    except Exception as e:
        print(f"Error during browser initialization or search: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Path to directory containing .ovpn files
    vpn_config_dir = "vpn_configs"  # Replace with the path to your .ovpn files

    # Keywords to search
    keywords_to_search = ["Python automation", "OpenVPN usage", "DuckDuckGo Selenium"]

    try:
        # List all .ovpn files in the directory
        vpn_configs = [os.path.join(vpn_config_dir, f) for f in os.listdir(vpn_config_dir) if f.endswith(".ovpn")]

        for config in vpn_configs:
            print(f"Using VPN config: {config}")
            with vpn_connection(config):
                search_duckduckgo(keywords_to_search)
            time.sleep(5)  # Wait before switching to the next VPN
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect_vpn()  # Ensure VPN is disconnected