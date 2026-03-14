import base64
import logging
import httpx
from config import PROXYAPI_KEY

logger = logging.getLogger(__name__)

async def analyze_body_photo(image_bytes: bytes, user: dict) -> str:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    goal_map = {
        "lose": "похудеть",
        "gain": "набрать массу",
        "relief": "рельеф",
        "maintain": "поддержание формы"
    }
    goal = goal_map.get(user.get("goal", ""), "похудеть")
    age = user.get("age", "не указан")
    weight = user.get("weight", "не указан")
    height = user.get("height", "не указан")

    prompt = f"""Ты профессиональный фитнес-тренер и диетолог. Проанализируй фото тела человека.
Данные пользователя: возраст {age}, вес {weight}кг, рост {height}см, цель: {goal}.

Ответь СТРОГО в следующем формате на русском языке:

🏋️ АНАЛИЗ ТЕЛА
• Диапазон жировой массы: X-Y% (приблизительная визуальная оценка)
• Тип телосложения: [эктоморф/мезоморф/эндоморф]
• Мышечный тонус: [низкий/средний/выше среднего]
• Зоны для проработки: [перечислить]

🍽️ ПЛАН ПИТАНИЯ (под твою цель)
Суточная норма: ~X ккал | Белки: Xг | Жиры: Xг | Углеводы: Xг

Примерный день питания:
Завтрак: [блюдо + граммовка]
Перекус: [блюдо]
Обед: [блюдо + граммовка]
Перекус 2: [блюдо]
Ужин: [блюдо + граммовка]

💪 ПРОГРАММА ТРЕНИРОВОК (4 недели)
[3-4 дня в неделю, расписать по дням с упражнениями, подходами, повторениями]

⚡ ЧЕРЕЗ 3 МЕСЯЦА при правильном подходе:
[мотивирующий прогноз что изменится]

⚠️ ВАЖНО: Это приблизительная оценка на основе визуального анализа. Для точных результатов обратитесь к специалисту."""

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            "https://api.proxyapi.ru/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {PROXYAPI_KEY}"},
            json={
                "model": "gpt-4o",
                "max_tokens": 1500,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "high"
                        }}
                    ]
                }]
            }
        )
        data = resp.json()
        if "error" in data:
            logger.error(f"OpenAI error: {data['error']}")
            raise Exception(data["error"].get("message", "Ошибка API"))
        return data["choices"][0]["message"]["content"]
