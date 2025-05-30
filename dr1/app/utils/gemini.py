import httpx
import json
from app.config import settings

async def analyze_error_with_gemini(correct_answer: str, user_answer: str) -> dict:
    prompt = f"""You are a language learning assistant. The user submits a response to a language exercise.
Correct answer: {correct_answer}
User's answer: {user_answer}

Your task is to evaluate the response and return a JSON object with two parts:
{{
  \"error_analysis\": \"Type of error made by the user. Use ONLY ONE of the following categories: Grammar Error, Semantic Error, Lexical Choice Error, Spelling Error, Syntax Error, Idiom Error, Stylistic Error, Register Error, Partial Answer. If no error was made, write 'No errors.' Return only ONE main error type, not a list. Don't list error types separated by commas in a line — just write one main type of error.\",
  \"brief_explanation\": \"A short, concise explanation (1–2 sentences max) of what the specific mistake was and why it's incorrect. But don't just say that it's a wrong translation — explain why. Write the explanation in Ukrainian language. If no error, write 'Правильна відповідь.'\"
}}"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024,
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            if "candidates" not in result or not result["candidates"]:
                raise ValueError("Invalid response format from Gemini API")
            text_response = result["candidates"][0]["content"]["parts"][0]["text"]
            cleaned_text = text_response.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            analysis = json.loads(cleaned_text)
            return analysis
    except Exception:
        return {
            "error_analysis": "Lexical Choice Error",
            "brief_explanation": f"Відповідь '{user_answer}' відрізняється від правильної відповіді '{correct_answer}'."
        } 