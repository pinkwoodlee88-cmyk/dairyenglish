import streamlit as st
from google import genai
import textwrap

# --- 1. 페이지 설정 및 제목 ---
st.set_page_config(page_title="일일 영어 공부 앱 (Gemini API)", layout="centered")
st.title("🎬 일일 생활 영어 학습 앱")
st.markdown("---")

# --- 2. Gemini API 키 입력 및 클라이언트 초기화 ---

def setup_gemini_client():
    """사용자가 입력한 API 키로 Gemini 클라이언트를 초기화하고 세션 상태에 저장합니다."""
    
    # 2-1. st.secrets에 키가 설정되어 있는지 먼저 확인 (배포 환경 고려)
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.info("API 키가 Streamlit Secrets에서 로드되었습니다.")
        # 입력 필드를 비활성화
        key_input_disabled = True
    else:
        # 2-2. st.session_state에 키가 없으면 사용자에게 직접 입력받음
        api_key = st.text_input(
            "🔑 Gemini API Key를 입력하세요:",
            type="password",  # 키가 보이지 않도록 'password' 타입 사용
            key="api_key_input" # 위젯의 고유 키
        )
        key_input_disabled = False

    # 키가 입력되었거나 로드되었다면 클라이언트 설정 시도
    if api_key:
        try:
            # Gemini 클라이언트 초기화
            client = genai.Client(api_key=api_key)
            # 초기화된 클라이언트를 세션 상태에 저장하여 앱 전체에서 사용
            st.session_state["gemini_client"] = client
            # 키가 성공적으로 설정되었음을 사용자에게 알림
            if not key_input_disabled:
                 st.success("API 클라이언트 설정 완료! 이제 '새 문장 받기'를 눌러보세요.")
            return True
        except Exception as e:
            st.error("⚠️ API 키 설정 오류가 발생했습니다. 키를 다시 확인해 주세요.")
            st.session_state["gemini_client"] = None
            return False
    
    return False

# --- 3. 대화문 생성 및 표시 함수 ---

def generate_english_dialogue():
    """Gemini API를 호출하여 대화문과 설명을 생성하고 Markdown으로 표시합니다."""
    
    # 세션 상태에서 클라이언트 객체 가져오기
    client = st.session_state.get("gemini_client")
    
    if not client:
        # 클라이언트가 설정되지 않았다면 함수 종료
        st.warning("먼저 API Key를 입력하여 클라이언트를 설정해 주세요.")
        return

    # Gemini에게 전달할 구체적인 프롬프트 설정
    prompt = """
    다음 형식에 맞춰 영화나 드라마에서 나올 법한 자연스러운 일상 영어 대화문(A, B 두 인물의 2-3 문장)을 랜덤하게 생성하고, 이 문장들의 문맥 및 핵심 표현에 대한 해설을 자세히 한국어로 제공해 줘.

    ---
    🎬 대화:
    A: [대화 내용]
    B: [대화 내용]

    📝 해설:
    **문맥**: [한국어 설명]
    **핵심 표현**: [핵심 영어 표현] - [한국어 뜻과 용법]
    ---
    """
    
    with st.spinner('새로운 생활 영어 문장을 생성하는 중입니다...'):
        try:
            # Gemini API 호출
            response = client.models.generate_content(
                model='gemini-2.5-flash', # 빠르고 효율적인 모델 사용
                contents=prompt,
                config={
                    "temperature": 0.8 # 창의적인 결과 유도
                }
            )
            
            # 생성된 텍스트를 앱에 표시
            st.markdown("## ✨ 오늘의 학습 문장")
            
            # 텍스트를 깔끔하게 표시 (불필요한 공백 제거)
            formatted_text = textwrap.dedent(response.text).strip()
            
            # Markdown 형식으로 출력
            st.markdown(formatted_text)
            
        except Exception as e:
            st.error(f"❌ Gemini API 호출 중 오류가 발생했습니다: {e}")
            st.info("API 키가 올바른지, 사용량이 초과되지 않았는지 확인해 주세요.")

# --- 4. 메인 실행 로직 ---

# 클라이언트 설정 함수 실행
is_client_configured = setup_gemini_client()

# 클라이언트가 설정되었다면 버튼 표시
if is_client_configured:
    st.markdown("---")
    
    # 버튼 클릭 시 대화문 생성 함수 호출
    if st.button("새로운 일일 영어 문장 받기", type="primary"):
        # 기존 내용 제거 및 새로운 내용 표시 (선택 사항)
        # st.empty() # 이전에 표시된 모든 위젯을 지우려면 사용
        generate_english_dialogue()
