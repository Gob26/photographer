import httpx
import asyncio

# Прокси данные
proxy_ip = '94.131.54.128'
proxy_port = 9885
proxy_user = 'kYgFvq'
proxy_password = 'svQ58N'

# Заголовки для эмуляции мобильного устройства
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36'
}

# Функция для тестирования подключения
async def test_connection(client, url, timeout=60):
    try:
        print(f'Тестирование подключения к {url}...')
        response = await client.get(url, headers=headers, timeout=timeout)
        print(f'Прокси работает для {url}, статус кода: {response.status_code}')
    except Exception as e:
        print(f'Ошибка при подключении к {url} через прокси: {e}')

# Запуск тестирования для Instagram, Google и Facebook
async def main():
    urls = ['https://www.instagram.com', 'https://www.google.com', 'https://www.facebook.com']
    async with httpx.AsyncClient(proxies=f'socks5://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
                                 timeout=60) as client:
        for url in urls:
            await test_connection(client, url)

if __name__ == "__main__":
    asyncio.run(main())
