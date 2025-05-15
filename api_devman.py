import requests

REQUEST_TIMEOUT_SECONDS = 100


def get_devman_review_with_polling(api_url, token, current_timestamp, timeout_val=REQUEST_TIMEOUT_SECONDS):
    """
    Отправляет запрос к API Девмана для получения списка проверок.
     Args:
        api_url (str): URL API эндпоинта.
        token (str): Персональный токен авторизации Девмана.

    Returns:
        dict or None: Словарь с данными ответа API или None в случае ошибки.
    """
    request_headers = {
        'Authorization': f'Token {token}'
    }
    params = {}
    if current_timestamp:
        params['timestump'] = current_timestamp
    response = requests.get(api_url, headers=request_headers, params=params, timeout=timeout_val)
    response.raise_for_status()
    review_payload = response.json()
    return review_payload
