import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
import pytest
from selenium import webdriver

class BasePage:
    download_dir = os.path.join(os.getcwd())

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def click_element(self, locator):
        self.wait.until(
            EC.visibility_of_element_located(locator)
        ).click()

class MainPage(BasePage):
    download_page_link = (By.LINK_TEXT, "Скачать локальные версии")

    def go_to_download_page(self):
        self.click_element(self.download_page_link)

class DownloadPage(BasePage):
    download_link = (By.XPATH, "//a[@href = 'https://update.saby.ru/Sbis3Plugin/master/win32/sbisplugin-setup-web.exe']")

    def download_exe(self):
        self.wait.until(
            EC.element_to_be_clickable(self.download_link)
        )
        self.click_element(self.download_link)

    def site_size_exe(self):
        file_element = self.driver.find_element(*self.download_link)
        file_size_full = file_element.text.split("Exe")[-1].replace(")", "").strip()
        file_size = float(file_size_full.replace("МБ", "").strip())
        print(f"Размер файла на сайте: {file_size}")
        return file_size

    def down_size_exe(self, file_name):
        file_path = os.path.join(self.download_dir, file_name)
        size_in_bytes = os.path.getsize(file_path)
        size_in_mb = size_in_bytes/ (1024 * 1024)
        print(f"Размер скачанного файла: {round(size_in_mb, 2)} МБ")
        return round(size_in_mb, 2)

    def wait_for_download(self, file_name):
        file_path = os.path.join(self.download_dir, file_name)
        texp_extentions = ['.tmp']

        while True:
            temp_files = [f for f in os.listdir(self.download_dir)
                          if any(f.endswith(ext) for ext in texp_extentions)]

            if not temp_files and os.path.exists(file_path):
                if os.path.getsize(file_path) > 0:
                    break

            time.sleep(1)

        return True

@pytest.fixture
def browser():
    download_dir = os.path.join(os.getcwd())
    edge_options = EdgeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    edge_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Edge(options=edge_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_3(browser):
    browser.get("https://saby.ru")

    main_page = MainPage(browser)
    main_page.go_to_download_page()

    download_page = DownloadPage(browser)
    download_page.download_exe()

    download_page.wait_for_download("sbisplugin-setup-web.exe")

    site_size = download_page.site_size_exe()
    file_size = download_page.down_size_exe("sbisplugin-setup-web.exe")

    assert site_size == file_size, f"Размер файла {file_size} МБ не совпадает с указанным на сайте {site_size} МБ"
