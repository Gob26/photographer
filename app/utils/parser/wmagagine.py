import requests
from bs4 import BeautifulSoup
import time

from app.utils.telegram_bot.post_to_socials import send_photosession_to_telegram

# URL главной страницы
BASE_URL = "https://www.wmagazine.com/fashion"

# Функция для извлечения ссылок из главной страницы
def fetch_article_links():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Проверка успешного запроса
        print("Успешно подключились к главной странице.")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к главной странице: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Найти все элементы <a class="ZXH Wni"> и извлечь ссылки
    links = []
    for a_tag in soup.find_all('a', class_='ZXH Wni'):
        href = a_tag.get('href')
        if href:
            # Привести ссылки к полному URL, если они относительные
            full_url = href if href.startswith('http') else "https://www.wmagazine.com" + href
            links.append(full_url)
            print(f"Найдена ссылка: {full_url}")
    
    if not links:
        print("Ссылки не найдены.")
    return links

# Функция для извлечения изображений с каждой статьи
def fetch_images_from_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка успешного запроса
        print(f"Успешно подключились к статье: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к статье {url}: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Найти все изображения и собрать атрибуты `alt` и `src`
    images = []
    for img_tag in soup.find_all('img', alt=True, src=True):
        img_data = {
            "alt": img_tag.get('alt'),
            "src": img_tag.get('src')
        }
        images.append(img_data)
        send_photosession_to_telegram(img_data['alt'], img_data['src'])
        print(f"Найдено изображение: alt='{img_data['alt']}', src='{img_data['src']}'")
        time.sleep(10)
    if not images:
        print("Изображения не найдены.")
    return images

# Основной код для выполнения парсинга
if __name__ == "__main__":
    article_links = fetch_article_links()
    all_images = []
    
    if article_links:
        for link in article_links:
            print(f"Собираем изображения с: {link}")
            images = fetch_images_from_article(link)
            all_images.append({link: images})
            time.sleep(1)
    else:
        print("Нет ссылок для обработки.")

    # Выводим результаты
    for article in all_images:
        print(article)
