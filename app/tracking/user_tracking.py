from flask import request
from user_agents import parse
from mixpanel import Mixpanel

# Инициализация Mixpanel
mixpanel_token = '1d9c73711de40d382e2f3d0ba7997609'  # Замените на свой токен
mixpanel = Mixpanel(mixpanel_token)

def track_user():
    ip_address = request.remote_addr  # Получение IP-адреса

    user_agent_string = request.headers.get('User-Agent')
    user_agent = parse(user_agent_string)

    # Сбор данных для Mixpanel
    mixpanel.track(ip_address, 'User Visit', {
        'browser': user_agent.browser.family if user_agent.browser else 'Unknown',
        'device': user_agent.device.family if user_agent.device else 'Unknown',
        'os': user_agent.os.family if user_agent.os else 'Unknown',
    })

    print(
        f'IP: {ip_address}, Browser: {user_agent.browser.family if user_agent.browser else "Unknown"}, Device: {user_agent.device.family if user_agent.device else "Unknown"}, OS: {user_agent.os.family if user_agent.os else "Unknown"}'
    )
