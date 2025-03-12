# Данный файл содержит логику сбора новостей с издания коммерсант https://www.kommersant.ru/
# Парсинг выполняется через playwright
from playwright.sync_api import sync_playwright
from datetime import datetime


def get_kommersant_links(base_url, header, target_date=None):
    # Если дата не передана, используем текущую
    if target_date is None:
        target_date = datetime.today().strftime("%Y-%m-%d")
    else:
        # Преобразуем дату в формат YYYY-MM-DD
        try:
            target_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Дата должна быть в формате YYYY-MM-DD")

    # Формируем полный URL с указанной датой
    full_url = f"{base_url}/{target_date}"

    with sync_playwright() as p:
        # Отключение доступа к камере
        browser = p.chromium.launch(
            headless=True,
            args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"]
        )
        page = browser.new_page()
        if header:
            page.set_extra_http_headers(header)

        # Переход на начальную страницу
        page.goto(full_url)

        article_links = set()

        while True:
            # Извлечение ссылок на статьи
            articles = page.locator('article.js-article')
            for i in range(articles.count()):
                article_url = articles.nth(i).get_attribute("data-article-url")
                if article_url:
                    article_links.add(article_url)

            # Попытка найти кнопку "Показать ещё"
            show_more_button = page.locator('button.js-archive-more-button')
            if show_more_button.is_visible():
                # Нажатие на кнопку и ожидание загрузки
                show_more_button.click()
                page.wait_for_timeout(2000)  # Ожидание подгрузки данных
            else:
                # Если кнопка недоступна, выходим из цикла
                break

        # Закрываем браузер
        browser.close()

        return list(article_links)
