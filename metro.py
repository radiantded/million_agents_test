import json
import time

from config import CATEGORY_NAME, SHOW_MORE_COUNT, SITE, HEADLESS
from loguru import logger
from playwright._impl._browser import Browser
from playwright._impl._page import Page
from playwright.sync_api import BrowserContext, sync_playwright
from playwright.sync_api._generated import Playwright


def init_browser(pw: Playwright) -> tuple[Browser, BrowserContext]:
    logger.info('Инициализация браузера')
    browser = pw.chromium.launch(headless=HEADLESS) 
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
    )
    return browser, context


def open_site(context: BrowserContext) -> Page:
    logger.info('Открытие сайта')
    page = context.new_page()
    try:
        page.goto(SITE, timeout=60000)
    except Exception as ex:
        logger.error(ex)
    return page


def unblock_page(page: Page) -> None:
    logger.info('Разблокировка страницы')
    page.locator('#__layout > div > div > div.modal-root').click()


def show_more(page: Page, count: int) -> None:
    logger.info(f'Кнопка "Показать ещё" - нажатий: {count}')
    for _ in range(count):
        try:
            page.get_by_role('button').get_by_text('Показать ещё').click()
            time.sleep(5)
        except Exception:
            logger.warning('Больше товаров нет')


def parse_goods(page: Page) -> dict[str, dict]:
    logger.info('Парсинг товаров')
    goods = {}
    for item in page.locator('#products-inner > div').all():
        good = {}
        good['id'] = item.get_attribute('data-sku')
        good['price'] = item.locator(
            'span.product-price.nowrap.product-card-prices__actual').locator(
                'span.product-price__sum-rubles').inner_text(
                    ).replace(u'\xa0', '')
        good['name'] = item.locator(
            'div.product-card__top > a').get_attribute('title')
        good['link'] = SITE + item.locator(
            'div.product-card__top > a').get_attribute('href')
        goods[good['id']] = good
        
        try:
            good['old_price'] = item.locator(
                'span.product-price.nowrap.product-card-prices__old').locator(
                    'span.product-price__sum-rubles').inner_text(
                        timeout=1000).replace(u'\xa0', '')
        except Exception:
            logger.warning(f"Товар {good['id']}: Нет прежней цены")
            good['old_price'] = None
        
        
    
    return goods


def parse_category(page: Page) -> dict[str, dict]:
    logger.info(f'Парсинг категории "{CATEGORY_NAME}"')
    try:
        page.get_by_role('button').get_by_text('Покупать онлайн').click()
    except Exception as ex:
        logger.error(ex)
    
    unblock_page(page)

    page.locator(
        'div.header-categories.header-main__categories > ul > li',
        has_text=CATEGORY_NAME
    ).click()
    page.wait_for_load_state()
    
    show_more(page, SHOW_MORE_COUNT)
    goods = parse_goods(page)
    
    return goods
        

def export_to_json(data: dict) -> None:
    logger.info('Экспорт в JSON')
    with open('goods.json', 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main() -> None:
    with sync_playwright() as pw:
        browser, context = init_browser(pw)
        index_page = open_site(context)
        goods = parse_category(index_page)
        browser.close()
        export_to_json(goods)


if __name__ == '__main__':
    main()
