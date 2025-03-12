from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def click_element(self, locator):
        self.wait.until(
            EC.visibility_of_element_located(locator)
        ).click()

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    def wait_for_text(self, text):
        found = self.wait.until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text)
        )
        assert found, f"Текст {text} не найден на странице"
        print(f"Текст '{text}' найден на странице")


class MainPage(BasePage):
    contacts_link = (By.LINK_TEXT, "Контакты")

    def go_to_contacts(self):
        self.click_element(self.contacts_link)


class ContactsPage(BasePage):
    tensor_logo = (By.XPATH, "//img[@alt = 'Разработчик системы Saby — компания «Тензор»']")

    def go_to_tensor_page(self):
        self.click_element(self.tensor_logo)
        self.driver.switch_to.window(self.driver.window_handles[-1])


class TensorPage(BasePage):
    about_link = (By.XPATH, "//a[@href = '/about']")
    image_block = (By.CLASS_NAME, 'tensor_ru-About__block3-image-wrapper')

    def go_to_about(self):
        self.click_element(self.about_link)

    def verify_image_size(self):
        images = self.driver.find_elements(*self.image_block)
        assert images, "Нет искомых картинок на странице"
        first_image_size = images[0].size

        for i, image in enumerate(images):
            image_size = image.size
            assert image_size == first_image_size, f"Картинка {i + 1} имеет другой размер"
        print("Все картинки равны")


@pytest.fixture
def browser():
    driver = webdriver.Edge()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_1(browser):
    browser.get("https://saby.ru")

    main_page = MainPage(browser)
    main_page.go_to_contacts()

    contacts_page = ContactsPage(browser)
    contacts_page.go_to_tensor_page()

    tensor_page = TensorPage(browser)
    tensor_page.scroll_to_bottom()
    tensor_page.wait_for_text("Сила в людях")
    assert "Сила в людях", "Нет искомого текста"

    tensor_page.go_to_about()
    WebDriverWait(browser, 10).until(EC.url_to_be("https://tensor.ru/about"))

    tensor_page.scroll_to_bottom()
    tensor_page.wait_for_text("Работаем")

    tensor_page.verify_image_size()
