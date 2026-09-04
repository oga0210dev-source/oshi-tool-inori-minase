import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiService:
    """
    Gemini APIとの連携を担当
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEYが設定されていません。"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model_name = "gemini-3.6-flash"

    def generate_json(
        self,
        system_instruction,
        prompt
    ):
        """
        GeminiからJSONレスポンスを取得
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )

        if not response.text:
            raise ValueError(
                "Geminiからレスポンスが返されませんでした。"
            )

        try:
            return json.loads(response.text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "GeminiのレスポンスをJSONとして解析できませんでした。"
            ) from error


gemini_service = GeminiService()
