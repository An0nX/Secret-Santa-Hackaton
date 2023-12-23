import httpx
import translators as ts

ts.get_region_of_server('google.com', 'ru')

API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"


def suggest_gift(preferences: str, budget: int = 10):
    """
    Generate a gift suggestion based on the user's preferences and budget.

    Parameters:
    - preferences (str): The user's preferences for the gift.
    - budget (int, optional): The budget for the gift. Defaults to 10.

    Returns:
    - None
    """
    response = httpx.post("https://api.promptjoy.com/api/jQGCwq", json={"interest": preferences, "budget": f"{budget}"}, headers={'Authorization': 'Bearer sk-17c4f2e94891fae6423fde005b9064d74372a564'}).json()
    try:
        translated = ts.translate_text(query_text=response["gift"], translator="google", from_language="en", to_language="ru", api_key=API_KEY, region='ru')
    except KeyError:
        return {'error': 'Сервер временно недоступен, повторите попытку позже'}
    return {'gift': translated}

if __name__ == "__main__":
    suggest_gift(input('Введите предпочтения: '))
