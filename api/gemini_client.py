import json
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, llm_key: str, llm_model: str, llm_response_scheme: str, debug = False):
        self.__client = genai.Client(api_key=llm_key) # LLM API 클라이언트 초기화
        self.__llm_model = llm_model
        self.__llm_response_scheme = json.loads(llm_response_scheme) # LLM 응답 구조 초기화
        self.__debug = debug
    
    def generate_answer(self, prompt: str) -> str:
        """
        주어진 프롬프트를 기반으로 LLM(Large Language Model)을 사용하여 응답을 생성합니다.
        Args:
            prompt (str): LLM에 제공할 프롬프트 문자열.
        Returns:
            str: LLM이 생성한 유효한 JSON 문자열. 유효하지 않은 경우 기본 JSON을 반환합니다.
        """
        if self.__debug:
            print(f"GeminiClient: Sending prompt to LLM: {prompt}")

        try:
            response = self.__client.models.generate_content(
                model=self.__llm_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=self.__llm_response_scheme,
                )
            )

            ret = response.text

            # 응답이 빈 문자열인지 확인
            if not ret or ret.isspace():
                if self.__debug:
                    print("GeminiClient: Received empty response from LLM")
                return json.dumps({"action": "wait", "reason": "Empty response from LLM"})

            # JSON 형식인지 확인
            try:
                json.loads(ret)
            except json.JSONDecodeError as e:
                if self.__debug:
                    print(f"GeminiClient: Invalid JSON response from LLM: {ret}")
                    print(f"GeminiClient: JSON error: {str(e)}")
                
                # 응답 텍스트에서 JSON 부분을 추출하려고 시도
                import re
                json_match = re.search(r'(\{.*\})', ret, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        json.loads(json_str)
                        ret = json_str
                    except json.JSONDecodeError:
                        ret = json.dumps({"action": "wait", "reason": "Invalid JSON response from LLM"})
                else:
                    ret = json.dumps({"action": "wait", "reason": "Invalid JSON response from LLM"})

            if self.__debug:
                print(f"GeminiClient: Received response from LLM: {ret}")

            return ret
        except Exception as e:
            if self.__debug:
                print(f"GeminiClient: Error generating response: {str(e)}")
            return json.dumps({"action": "wait", "reason": f"Error: {str(e)}"})