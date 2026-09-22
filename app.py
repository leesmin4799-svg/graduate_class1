import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import openpyxl
import pandas as pd

# OpenAI 클라이언트 설정 (실제 API 키로 교체하세요)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 비파법사 페르소나 부여 (AI에게 역할을 지시하는 시스템 프롬프트)
biwa_hoshi_prompt = """
당신은 12~13세기 일본 가마쿠라 시대를 떠돌며 비파를 뜯고 '헤이케 모노가타리(평가물어)'를 불렀던 시각장애인 유랑 예인, '비파법사(琵琶法師)'입니다. 
학생들이 이 이야기가 '문자'가 아닌 '소리'로 전승되었을 때의 특징이나 당시 시대상에 대해 질문할 것입니다. 
답변 규칙:
1. 옛스러운 하오체, 하게체 등을 사용하고, 눈이 보이지 않는 대신 귀로 듣고 마음으로 느낀 감각을 묘사하시오.
2. 가끔 비파 치는 소리(예: "비롱~", "비로롱~")를 의성어로 섞어 이야기의 운율감을 살리시오.
3. 기온정사(祇園精舎)의 종소리, 제행무상(諸行無常)의 세계관을 넌지시 언급하며 핵심을 찌르는 철학적인 대답을 주시오.
"""

# 모델 설정 (시스템 프롬프트 적용)
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=biwa_hoshi_prompt
)

# ----------------- 관리자 모드 (사이드바) -----------------
with st.sidebar:
    st.header("⚙️ 관리자 모드")
    admin_pw = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    # 임시 비밀번호는 1234로 설정했습니다. (원하시는 대로 변경 가능합니다)
    if admin_pw == "1234":
        st.success("관리자 인증 성공")
        excel_file = "heike_data.xlsx"
        
        if os.path.isfile(excel_file):
            # 엑셀 파일을 읽어서 다운로드 버튼 생성
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="📥 학생 제출 데이터 다운로드 (Excel)",
                    data=f,
                    file_name="heike_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("아직 제출된 학생 데이터가 없습니다.")

# ----------------- 메인 화면 구성 -----------------
st.title("일본고전문학의 이해: 헤이케 모노가타리")
st.markdown("> **祇園精舎の鐘の声、諸行無常の響きあり。**\n> (기온정사의 종소리, 제행무상의 울림이 있나니.)")
st.write("기온정사로 시작하는 『헤이케 모노가타리』는 눈으로 '읽히기'보다 비파법사들의 입을 통해 귀로 '들려진' 이야기입니다. 그 사실이 이 이야기를 어떻게 바꿔 놓았을까요?")

st.divider()

# 1차: 초기 의견 수집
st.header("1차: 나의 첫 번째 생각")
opinion_1 = st.text_area("이야기가 '문자'가 아닌 '음성'으로 전달되었을 때의 특징이나 효과에 대한 첫인상을 자유롭게 적어주세요.", height=150)

st.divider()

# 2차: AI 비파법사와의 대화
st.header("2차: 비파법사와의 대화")
st.write("의견을 적다 생긴 궁금증을 당시 시대를 살았던 '비파법사'에게 직접 물어보세요.")

# 채팅 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 채팅 입력창
if prompt := st.chat_input("예: 글을 모르던 백성들에게 이 이야기는 어떻게 들렸소?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini에 보낼 대화 기록 구성
    gemini_history = []
    for m in st.session_state.messages[:-1]: 
        role = "model" if m["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [m["content"]]})

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(prompt)
    ai_reply = response.text
    
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

st.divider()

# 3차: 최종 의견 제출
st.header("3차: 나의 최종 의견")
opinion_2 = st.text_area("비파법사와의 문답을 통해 깨달은 점을 바탕으로, 처음에 적었던 나의 생각을 어떻게 발전시켰는지 최종적으로 정리해 주세요.", height=150)

# 학번/이름 입력 및 제출
st.write("---")
st.subheader("과제 제출")
student_name = st.text_input("학번과 이름을 정확히 적어주세요 (예: 20261234 비단이)")

if st.button("제출하기"):
    if opinion_1 and opinion_2 and student_name:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        excel_file = "heike_data.xlsx"
        
        # 엑셀 파일이 없으면 새로 생성, 있으면 불러오기
        if not os.path.isfile(excel_file):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "헤이케모노가타리_제출"
            ws.append(["제출시간", "이름/학번", "1차 초기 의견", "3차 최종 의견"])
        else:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            
        # 데이터 추가 및 저장
        ws.append([now, student_name, opinion_1, opinion_2])
        wb.save(excel_file)
            
        st.success(f"{student_name} 학생의 과제가 성공적으로 제출되었습니다!")
    else:
        st.error("이름, 1차 의견, 3차 의견을 모두 작성해야 제출할 수 있습니다.")
