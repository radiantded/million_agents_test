# Парсер онлайн-магазина METRO
### Конфигурация
```
CATEGORY_NAME - название категории для парсинга
SHOW_MORE_COUNT - количество нажатий кнопки "Показать ещё" в списке товаров (1 нажатие - плюс 30 товаров)
HEADLESS - режим работы браузера (True - безоконный)
```
### Запуск (Windows)
```
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python metro.py
```
