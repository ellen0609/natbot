import os
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright

# 定義要爬取的網址和元素
URL = 'https://www.google.com.tw/'
ELEMENTS = [
    {'selector': 'a', 'attr': 'id'},
    {'selector': 'link', 'attr': 'id'},
    {'selector': 'img', 'attr': 'id'},
    {'selector': 'button', 'attr': 'id'},
    {'selector': 'text', 'attr': 'id'},
    {'selector': 'input', 'attr': 'id'}
]

# 定義要儲存的資料夾名稱
FOLDER_NAME = datetime.now().strftime('%Y-%m-%d')

# 如果資料夾已經存在，則加上後綴數字
folder_index = 1
if (os.path.exists(FOLDER_NAME)):
    while os.path.exists(FOLDER_NAME + '_' + str(folder_index)):
        folder_index += 1
    FOLDER_NAME = FOLDER_NAME + '_' + str(folder_index)

# 創建資料夾
os.makedirs(FOLDER_NAME)

# 使用 playwright 爬取網頁
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)

    # 抓取元素
    for index, element in enumerate(ELEMENTS):
        elements = page.query_selector_all(element['selector'])
        for el_index, el in enumerate(elements):
            print(index, element['selector'], el_index, el.as_element().inner_text())
            # el.as_element()
            # 標上 id
            # js_handle = el.evaluate_handle('el => el.setAttribute("id", arguments[0])', f"{index + 1}_{el_index}")
            # el = js_handle.as_element()
            # 標上內容
            # with open(f"{FOLDER_NAME}/element_{index + 1}_{el_index}.txt", 'w', encoding='utf-8') as f:
            #     f.write(el.inner_text())

    # 截圖
    screenshot_index = 1
    while os.path.exists(f"{FOLDER_NAME}/screenshot_{screenshot_index}.png"):
        screenshot_index += 1
    page.screenshot(path=f"{FOLDER_NAME}/screenshot_{screenshot_index}.png")

    browser.close()

        