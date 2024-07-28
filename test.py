from flask import Flask, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(2)  # Đợi trang web tải xong
    screenshot = 'screenshot.png'
    driver.save_screenshot(screenshot)
    driver.quit()
    return screenshot

@app.route('/')
def index():
    url = 'https://linkbio.co/trumriviu'  # URL của trang web bạn muốn hiển thị
    screenshot = take_screenshot(url)
    return send_file(screenshot, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
