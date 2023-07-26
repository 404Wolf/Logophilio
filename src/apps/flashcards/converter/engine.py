import atexit

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service()

options = webdriver.ChromeOptions()
options.add_argument("--kiosk-printing")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")

webdriver_chrome = webdriver.Chrome(service=service, options=options)
atexit.register(webdriver_chrome.close)
