import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Function to connect to VPN using OpenVPN
def connect_to_vpn(config_path):
    print(f"Connecting to VPN with config: {config_path}")
    disconnect_vpn()  # Disconnect any active VPN
    process = subprocess.Popen(
        ["sudo", "openvpn", "--config", config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(10)  # Allow time for the VPN to connect
    return process


# Function to disconnect VPN
def disconnect_vpn():
    subprocess.run(["sudo", "killall", "openvpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Disconnected from VPN.")


# Function to perform searches on DuckDuckGo
def search_duckduckgo(keywords):
    print("Launching browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://duckduckgo.com")

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for results to load

    driver.quit()
    print("Searches completed.")


if __name__ == "__main__":
    # Path to directory containing .ovpn files
    vpn_config_dir = "vpn_configs"  # Replace with the path to your .ovpn files

    # Keywords to search
    keywords_to_search = ["Python automation", "OpenVPN usage", "DuckDuckGo Selenium"]

    try:
        # List all .ovpn files in the directory
        vpn_configs = [os.path.join(vpn_config_dir, f) for f in os.listdir(vpn_config_dir) if f.endswith(".ovpn")]

        for config in vpn_configs:
            vpn_process = connect_to_vpn(config)  # Connect to VPN
            try:
                search_duckduckgo(keywords_to_search)  # Perform searches
            finally:
                disconnect_vpn()  # Disconnect VPN
                if vpn_process:
                    vpn_process.terminate()
            time.sleep(5)  # Wait before switching to the next VPN
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect_vpn()  # Ensure VPN is disconnected