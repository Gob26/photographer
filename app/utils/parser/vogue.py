import requests
from bs4 import BeautifulSoup

# URL страницы с фотографиями
url = "https://www.vogue.com/photovogue/photos"

# Отправляем запрос к странице
response = requests.get(url)

# Проверяем, успешен ли запрос
if response.status_code == 200:
    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Ищем все теги <picture> с классом
    pictures = soup.find_all('picture', class_=True)

    # Проходим по найденным тегам
    for picture in pictures:
        # Находим тег <img> внутри <picture>
        img_tag = picture.find('img')
        
        # Извлекаем атрибуты 'alt' и 'src'
        if img_tag:
            alt_text = img_tag.get('alt', 'No alt text')
            image_src = img_tag.get('src', 'No image source')
            
            # Выводим результат
            print(f"Alt: {alt_text}")
            print(f"Image URL: {image_src}")
            print("-" * 40)
else:
    print(f"Ошибка при подключении к странице: {response.status_code}")
