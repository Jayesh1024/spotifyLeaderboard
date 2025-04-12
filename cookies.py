import time
import json
from selenium import webdriver
service = webdriver.ChromeService(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
url = "https://accounts.spotify.com/en-GB/login?continue=https%3A%2F%2Fopen.spotify.com%2F"
driver.get(url)
time.sleep(30)
cookies = driver.get_cookies()
with open('cookies.json', 'w') as f:
    json.dump(obj=cookies, fp=f, indent=2)
driver.quit()