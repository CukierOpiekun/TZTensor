from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from selenium import webdriver


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.current_url = driver.current_url
        self.title = driver.title

    def click_element(self, locator):
        self.wait.until(
            EC.visibility_of_element_located(locator)
        ).click()

    def wait_for_text(self, texts):

        if isinstance(texts, str):
            texts = (texts,)
        all_found = True

        for text in texts:
            try:
                self.wait.until(
                    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text)
                )
            except Exception as e:
                print(f"Контакт '{text}' не найден: {e}")
                all_found = False

        assert all_found, "Не все контакты были найдены, или же они полностью отсутствуют"
        print("Все искомые контакты найдены")


class MainPage(BasePage):
    contacts_link = (By.LINK_TEXT, "Контакты")

    def go_to_contacts(self):
        self.click_element(self.contacts_link)


class ContactsPage(BasePage):
    place = (By.XPATH, "//span[@class = 'sbis_ru-Region-Chooser__text sbis_ru-link']")
    another_place = (By.XPATH, "//span[@title = 'Камчатский край']")

    def yaobl(self):
        self.wait.until(
            EC.text_to_be_present_in_element(self.place, "Ярославская обл.")
        )
        current_region = self.driver.find_element(*self.place).text
        assert current_region == "Ярославская обл."

        try:
            self.click_element(self.place)
            self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@class='sbis_ru-Region-Panel sbis_ru-Region-Panel-l']"))
            )
        except Exception as e:
            print(f"Не получается перейти: {e}")
            assert e

    def kkobl(self):
        #Без двух неявных ожиданий тест не срабатывает. Возможно не успевает перейти. С явными ожиданиями не работает
        sleep(1)
        self.click_element(self.another_place)
        sleep(1)
        current_region = self.driver.find_element(*self.place).text
        assert current_region == "Камчатский край", "Не тот регион"


class ContactsPageKK(BasePage):
    place = (By.XPATH, "//span[@class = 'sbis_ru-Region-Chooser__text sbis_ru-link']")
    correct_url = "https://saby.ru/contacts/41-kamchatskij-kraj?tab=clients"

    def check(self):
        current_region = self.driver.find_element(*self.place).text
        assert current_region == "Камчатский край", f"Ожидался Камчатский край, получено: {current_region}"
        assert self.current_url == self.correct_url, f"Ожидался URL: {self.correct_url}, получен URL: {self.current_url}"

    def check_title(self):
        current_title = self.title
        assert current_title == "Saby Контакты — Камчатский край", (f"Ожидалось: 'Saby Контакты — Камчатский край', "
                                                                    f"полученно: {current_title}")
        print(f"Название страницы: {current_title}")


@pytest.fixture
def browser():
    driver = webdriver.Edge()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_2(browser):
    browser.get("https://saby.ru")

    main_page = MainPage(browser)
    main_page.go_to_contacts()

    contacts_page_yo = ContactsPage(browser)
    contacts_page_yo.wait_for_text(("Saby - Ярославль", "Компания «Изомер»", "ДИФАЙН"))
    contacts_page_yo.yaobl()
    contacts_page_yo.kkobl()

    contacts_page_kk = ContactsPageKK(browser)
    contacts_page_kk.check()
    contacts_page_kk.wait_for_text("Saby - Камчатка")
    contacts_page_kk.check_title()
