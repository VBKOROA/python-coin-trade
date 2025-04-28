import json
from google import genai
from google.genai import types
import re # 정규 표현식 모듈 추가

class GeminiClient:
    # 매직 문자열을 상수로 정의
    ACTION_KEY = "action"
    REASON_KEY = "reason"
    WAIT_ACTION = "wait"

    def __init__(self, llm_key: str, llm_model: str, llm_response_scheme: str, debug = False):
        self.__client = genai.Client(api_key=llm_key) # LLM API 클라이언트 초기화
        self.__llm_model = llm_model
        self.__llm_response_scheme = json.loads(llm_response_scheme) # LLM 응답 구조 초기화
        self.__debug = debug

    def _create_error_response(self, reason: str) -> str:
        """지정된 이유로 기본 오류 JSON 응답을 생성합니다."""
        # 상수를 사용하여 오류 응답 생성
        return json.dumps({self.ACTION_KEY: self.WAIT_ACTION, self.REASON_KEY: reason})

    def _validate_and_parse_response(self, response_text: str) -> str:
        """
        LLM 응답 텍스트의 유효성을 검사하고 JSON으로 파싱합니다.
        Args:
            response_text (str): LLM에서 받은 원시 응답 텍스트.
        Returns:
            str: 유효한 JSON 문자열. 유효하지 않거나 오류 발생 시 기본 JSON을 반환합니다.
        """
        # 응답이 빈 문자열인지 확인
        if not response_text or response_text.isspace():
            if self.__debug:
                print("GeminiClient: Received empty response from LLM")
            return self._create_error_response("Empty response from LLM") # 헬퍼 사용

        # JSON 형식인지 확인
        try:
            json.loads(response_text)
            return response_text # 이미 유효한 JSON이면 그대로 반환
        except json.JSONDecodeError as e:
            if self.__debug:
                print(f"GeminiClient: Invalid JSON response from LLM: {response_text}")
                print(f"GeminiClient: JSON error: {str(e)}")

            # 응답 텍스트에서 JSON 부분을 추출하려고 시도
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    json.loads(json_str)
                    if self.__debug:
                        print(f"GeminiClient: Extracted valid JSON: {json_str}")
                    return json_str # 추출된 유효한 JSON 반환
                except json.JSONDecodeError:
                    if self.__debug:
                        print(f"GeminiClient: Extracted text is still not valid JSON: {json_str}")
                    # 헬퍼 사용
                    return self._create_error_response("Invalid JSON response from LLM after extraction")
            else:
                if self.__debug:
                    print("GeminiClient: Could not find JSON structure in the response.")
                # 헬퍼 사용
                return self._create_error_response("Invalid JSON response from LLM")

    def generate_answer(self, prompt: str) -> str:
        """
        주어진 프롬프트를 기반으로 LLM(Large Language Model)을 사용하여 응답을 생성합니다.
        Args:
            prompt (str): LLM에 제공할 프롬프트 문자열.
        Returns:
            str: LLM이 생성하고 검증한 유효한 JSON 문자열. 오류 발생 시 기본 JSON을 반환합니다.
        """
        if self.__debug:
            print(f"GeminiClient: Sending prompt to LLM: {prompt}")

        try:
            response = self.__client.models.generate_content(
                model=self.__llm_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=self.__llm_response_scheme,
                )
            )

            raw_response_text = response.text

            if self.__debug:
                print(f"GeminiClient: Received raw response from LLM: {raw_response_text}")

            # 응답 유효성 검사 및 파싱 위임
            parsed_response = self._validate_and_parse_response(raw_response_text)

            if self.__debug:
                print(f"GeminiClient: Parsed response: {parsed_response}")

            return parsed_response
        except Exception as e: # 기타 예외 처리
            if self.__debug:
                print(f"GeminiClient: Unexpected error during LLM API call: {str(e)}")
            # 예기치 않은 오류 발생 시 - 헬퍼 사용
            return self._create_error_response(f"Unexpected Error: {str(e)}")