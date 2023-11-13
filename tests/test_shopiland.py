import time
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

@pytest.fixture(scope='session')
def chrome_driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument('executable_path=tests\\chromedriver.exe')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.implicitly_wait(10)

    # Open base page:
    driver.get('https://shopiland.ru/')
    # time.sleep(5)
    yield driver
    driver.quit()

def test_main_page_load(chrome_driver):
    """Проверка, что главная страница загружается в течение 5 сек.
    Тест успешен, если за это время загрузятся все картинки товаров - их 50"""

    wait = WebDriverWait(chrome_driver, 5)

    # Find all pictures which must be loaded in 5 sek.
    images = wait.until(EC.presence_of_all_elements_located(('xpath', '//picture')))

    # Checking that all 50 pictures are loaded
    assert len(images) == 50

def test_search(chrome_driver):
    """Проверка, что работает поиск"""

    # Find search field and type "утюг"
    field_search = chrome_driver.find_element('xpath', '//input[@class="MuiInputBase-input css-mnn31"]')
    field_search.clear()
    field_search.send_keys('утюг')
    # field_search.send_keys(Keys.ENTER) # Press Enter

    btn_search = chrome_driver.find_element('xpath', '//button[@type="submit" and @aria-label="search"]')
    btn_search.click()

    assert chrome_driver.current_url == 'https://shopiland.ru/search?q=%D1%83%D1%82%D1%8E%D0%B3'

def test_results_are_relevant(chrome_driver):
    """Проверка, что поиск выдаёт релевантные результаты"""

    wait = WebDriverWait(chrome_driver, 20)

    # Search for all item descriptions
    item_descriptions = wait.until(EC.presence_of_all_elements_located(('xpath', '//p[@class="css-99ww93"]')))

    elements_to_check = []  # A list of descriptions that do not contain "утюг"

    for item in item_descriptions:
        if 'Утюг' not in item.text and 'утюг' not in item.text:
            elements_to_check.append(item.text)  # Add description to the list
    if elements_to_check:
        print("Relevance is in question for:")
        for item in elements_to_check:
            print(item)
        assert False, 'No "утюг" in the description. Relevance should be checked manually'

def test_all_stores_have_results(chrome_driver):
    """Проверка, что товар найден во всех магазинах"""

    wait = WebDriverWait(chrome_driver, 20)

    # Store statistics
    elements = wait.until(EC.presence_of_all_elements_located(('class name', 'css-18woau7')))
    failed_stores = []  # A list of stores where item is not found

    for element in elements:
        text = element.text.split(' ')
        number = int(text[0])
        # print(number)

        try:
            assert number > 0
        except AssertionError:
            # A name of the store
            parent_element = element.find_element('xpath', '..')
            parent_text = parent_element.text
            failed_stores.append(parent_text)  # Add the store to the list

    if failed_stores:
        print("Stores where item is not found:")
        for store in failed_stores:
            print(store)
        raise Exception("The availability of products in the stores from the list should be checked manually")

def test_to_the_store(chrome_driver):
    """Проверка, что нажатие на товар и потом на кнопку - 'В магазин' открывает страницу продавца в соседней вкладке"""

    wait = WebDriverWait(chrome_driver, 20)

    # Search for all item descriptions
    item_descriptions = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//p[@class="css-99ww93"]')))

    first_item = item_descriptions[0]
    first_item.click()

    button_to_store = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="В магазин"]')))
    button_to_store.click()

    element_text = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[@class="css-gyxkao"]'))).text

    tabs = chrome_driver.window_handles
    chrome_driver.switch_to.window(tabs[-1])

    if 'Wildberries' in element_text:
        assert 'wildberries' in chrome_driver.current_url
    elif 'Ozon' in element_text:
        assert 'ozon' in chrome_driver.current_url
    elif 'AliExpress' in element_text:
        assert 'aliexpress' in chrome_driver.current_url
    elif 'Яндекс Маркет' in element_text:
        assert 'market.yandex' in chrome_driver.current_url
    elif 'СберМегамаркет' in element_text:
        assert 'megamarket' in chrome_driver.current_url
    elif 'KazanExpress' in element_text:
        assert 'kazanexpress' in chrome_driver.current_url
