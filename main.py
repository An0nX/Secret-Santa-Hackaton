import httpx
import translators as ts

API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"

def suggest_gift(preferences: str, budget: int = 10):
    response = httpx.post("https://api.promptjoy.com/api/jQGCwq", json={"interest": preferences, "budget": f"{budget}"}, headers={'Authorization': 'Bearer sk-17c4f2e94891fae6423fde005b9064d74372a564'}).json()
    translated = ts.translate_text(query_text=response["gift"], translator="google", from_language="en", to_language="ru", api_key=API_KEY, region='ru')
    print(translated)

if __name__ == "__main__":
    suggest_gift(input('Введите предпочтения: '))
