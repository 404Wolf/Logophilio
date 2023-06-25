import base64
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--kiosk-printing")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=2000x2000")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")

webdriver_chrome = webdriver.Chrome(service=service, options=chrome_options)


def convert_to_pdf(filepath: str, out_dir: str):
    """
    Convert a svg on disk to a pdf using Selenium and Chromedriver.

    Args:
        filepath (str): The path to the svg on disk.
        out_dir (str): The path to the output pdf on disk.
    """
    filepath = os.path.abspath(filepath).replace('\\', '/')
    webdriver_chrome.get(f"file:///{filepath}")
    pdf = webdriver_chrome.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": False,
            "landscape": False,
            "displayHeaderFooter": False,
            "scale": 1.5,
            "paperWidth": 1.75,
            "paperHeight": 2.5,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
        },
    )
    webdriver_chrome.close()
    with open(out_dir, "wb") as f:
        f.write(base64.b64decode(pdf["data"]))
