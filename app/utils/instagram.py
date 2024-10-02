import subprocess
import time
import os
import signal
from instaloader import Instaloader, Profile

# Укажите свой пароль
password = '0062'
instagram_username = 'gob2626'  # Укажите свой логин
instagram_password = '03079Gramm1986'  # Укажите свой пароль

def connect_vpn():
    print("Попытка подключения к VPN...")
    try:
        process = subprocess.Popen(['sudo', '-S', 'openvpn', '--config', 'Canada, Montreal ROUTERS.ovpn'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)  # Дождитесь подключения
        print("Подключение к VPN успешно!")
        return process
    except Exception as e:
        print(f"Ошибка при подключении к VPN: {e}")
        return None

def disconnect_vpn(process):
    print("Отключение VPN...")
    try:
        if process:
            os.kill(process.pid, signal.SIGTERM)  # Остановить процесс
            print("VPN отключен.")
        else:
            print("Нет активного процесса VPN.")
    except Exception as e:
        print(f"Ошибка при отключении VPN: {e}")

def get_latest_post(username):
    L = Instaloader()

    # Вход в Instagram
    try:
        L.login(instagram_username, instagram_password)
        print("Успешный вход в Instagram!")
    except Exception as e:
        print(f"Ошибка при входе в Instagram: {e}")
        return

    try:
        profile = Profile.from_username(L.context, username)
        posts = list(profile.get_posts())
        if posts:
            latest_post = posts[0]
            print(f"Последний пост {username}:")
            print(f"Заголовок: {latest_post.caption}")
            print(f"Дата: {latest_post.date}")
            print(f"Ссылка: https://www.instagram.com/p/{latest_post.shortcode}/")
        else:
            print("Посты не найдены.")
    except Exception as e:
        print(f"Ошибка при получении поста: {e}")

if __name__ == "__main__":
    vpn_process = connect_vpn()
    time.sleep(10)  # Ожидание для стабилизации подключения
    get_latest_post('anna_svetlichnaya')  # Убедитесь, что имя пользователя правильное
    time.sleep(1130)  # Ожидание перед отключением
    disconnect_vpn(vpn_process)
