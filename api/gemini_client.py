import json
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, llm_key: str, llm_model: str, llm_response_scheme: str):
        self.__client = genai.Client(api_key=llm_key) # LLM API 클라이언트 초기화
        self.__LLM_MODEL = llm_model
        self.__LLM_RESPONSE_SCHEME = json.loads(llm_response_scheme) # LLM 응답 구조 초기화
    
    def generate_answer(self, prompt: str) -> str:
        """
        주어진 프롬프트를 기반으로 LLM(Large Language Model)을 사용하여 응답을 생성합니다.
        Args:
            prompt (str): LLM에 제공할 프롬프트 문자열.
        Returns:
            str: LLM이 생성한 응답 텍스트.
        """
        print(prompt)
        response = self.__client.models.generate_content(
            model=self.__LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=1.0,
                response_mime_type="application/json",
                response_schema=self.__LLM_RESPONSE_SCHEME
            )
        )
        
        ret = response.text
        print(ret)
        return ret