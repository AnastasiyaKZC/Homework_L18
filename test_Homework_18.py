import requests
import allure
from allure_commons._allure import step
from allure_commons.types import AttachmentType
from selene import Browser, Config
from selene.support.conditions import have
from selenium import webdriver

LOGIN = "example1200@example.com"
PASSWORD = "123456"
WEB_URL = "https://demowebshop.tricentis.com"
API_URL = "https://demowebshop.tricentis.com"

PRODUCT_ID = "14"  # Обновлено на ID товара 14
ADD_TO_CART_ENDPOINT = f"/addproducttocart/catalog/{PRODUCT_ID}/1/1"

@allure.title("Добавление товара в корзину через API и проверка через UI")
def test_add_product_to_cart_via_api_and_check_ui():
    driver = webdriver.Chrome()
    browser = Browser(Config(driver=driver, base_url=WEB_URL))

    with step("Логин через API"):
        result = requests.post(
            url=API_URL + "/login",
            data={"Email": LOGIN, "Password": PASSWORD, "RememberMe": False},
            allow_redirects=False
        )
        assert result.status_code == 302
        auth_cookie = result.cookies.get("NOPCOMMERCE.AUTH")
        allure.attach(result.text, name="Login Response", attachment_type=AttachmentType.TEXT)

    with step("Добавить товар в корзину через API"):
        response = requests.post(
            url=API_URL + ADD_TO_CART_ENDPOINT,
            cookies={"NOPCOMMERCE.AUTH": auth_cookie},
            data={"addtocart_14.EnteredQuantity": 1}
        )
        allure.attach(response.text, name="Add to cart response", attachment_type=AttachmentType.JSON)
        assert response.status_code == 200
        assert '"success":true' in response.text

    with step("Подставить куки и открыть корзину"):
        browser.open("/")
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": auth_cookie})
        browser.open("/cart")

    with step("Проверить, что товар отобразился в корзине"):
        browser.element(".cart-item-row").should(have.text("Black & White Diamond Heart"))

    browser.quit()