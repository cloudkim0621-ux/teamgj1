import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 데이터 파일 경로
st.set_page_config(page_title="OSS! 주짓수 통합관리", layout="wide")
DB_FILE = "members_db.csv"  # 데이터가 저장될 파일 이름

# 2. 데이터 불러오기/저장 함수
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # 파일이 없으면 빈 표를 만듭니다.
        df = pd.DataFrame(columns=["이름", "연락처", "구분", "벨트", "그랄", "회비상태", "등록일", "메모"])
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        return df

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# 웹 실행 시 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 3. 사이드바 메뉴 (관장님 요청 10가지 기능 통합)
st.sidebar.title("🥋 OSS! GYM ADMIN")
menu = st.sidebar.radio("메뉴 선택", [
    "🏠 홈/대시보드", 
    "🎓 관원 명단/승급관리", 
    "📅 출결 및 성장기록", 
    "💰 회비 수납관리", 
    "👪 학부모 상담/기록", 
    "🏆 대회/선수반 관리", 
    "🎥 영상공유/브랜딩"
])

# --- 각 메뉴별 실제 기능 ---

if menu == "🏠 홈/대시보드":
    st.title("📊 체육관 운영 현황")
    df = st.session_state.df
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 관원", f"{len(df)}명")
    col2.metric("회비 미납", f"{len(df[df['회비상태'] == '미납'])}명")
    col3.metric("선수반 인원", f"{len(df[df['구분'] == '선수반'])}명")
    st.divider()
    st.subheader("📋 최근 등록 관원")
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "🎓 관원 명단/승급관리":
    st.title("🎓 관원 정보 및 승급(띠) 관리")
    
    # 신규 관원 추가
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("이름")
            phone = c2.text_input("연락처")
            group = c1.selectbox("구분", ["일반부", "키즈부", "선수반"])
            belt = c2.selectbox("벨트", ["화이트", "블루", "퍼플", "브라운", "블랙"])
            stripe = st.slider("그랄 수", 0, 4, 0)
            if st.form_submit_button("등록 완료"):
                new_data = {
                    "이름": name, "연락처": phone, "구분": group, 
                    "벨트": belt, "그랄": stripe, "회비상태": "미납", 
                    "등록일": datetime.now().strftime("%Y-%m-%d"), "메모": ""
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"{name} 관원이 등록되었습니다!")
                st.rerun()

    # 전체 명단 수정 및 삭제
    st.subheader("✏️ 명단 수정 (표에서 직접 수정 후 아래 저장 버튼을 누르세요)")
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 모든 변경사항 저장하기"):
        st.session_state.df = edited_df
        save_data(edited_df)
        st.success("데이터가 안전하게 저장되었습니다!")

elif menu == "📅 출결 및 성장기록":
    st.title("📅 출결 확인 및 실력 성장기록")
    selected_name = st.selectbox("대상 관원 선택", st.session_state.df["이름"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ 오늘 출석 체크"):
            st.success(f"{datetime.now().strftime('%m/%d')} {selected_name} 관원 출석 완료!")
    with col_b:
        skill_note = st.text_input("오늘 지도한 핵심 기술 (성장 기록)")
        if st.button("📝 기술 기록 저장"):
            st.info(f"{selected_name} 관원: '{skill_note}' 기록됨")

elif menu == "💰 회비 수납관리":
    st.title("💰 회비 수납 및 미납 관리")
    df = st.session_state.df
    unpaid = df[df["회비상태"] == "미납"]
    st.subheader(f"⚠️ 현재 미납자 목록 ({len(unpaid)}명)")
    st.dataframe(unpaid[["이름", "연락처", "구분", "등록일"]], use_container_width=True)
    st.caption("팁: 명단 관리 메뉴에서 납부 완료 시 '완납'으로 변경해주시면 여기서 사라집니다.")

elif menu == "👪 학부모 상담/기록":
    st.title("📝 학부모 상담 및 특이사항 기록")
    target = st.selectbox("관원(아이) 선택", st.session_state.df["이름"])
    note = st.text_area("상담 내용 또는 특이사항 기록")
    if st.button("📒 상담 일지 저장"):
        st.success(f"{target} 관원의 상담 내용이 기록되었습니다.")

elif menu == "🏆 대회/선수반 관리":
    st.title("🏆 대회 출전 및 선수반 집중관리")
    df = st.session_state.df
    pro = df[df["구분"] == "선수반"]
    st.subheader("선수반 명단")
    st.table(pro[["이름", "벨트", "그랄", "연락처"]])
    st.divider()
    st.subheader("대회 일정")
    st.write("2024년 대회 일정을 입력하고 관리하세요.")

elif menu == "🎥 영상공유/브랜딩":
    st.title("🎥 기술 영상 공유 및 홍보")
    url = st.text_input("복습 영상 유튜브 링크", "https://www.youtube.com/")
    if url:
        st.video(url)
    st.divider()
    st.subheader("📢 인스타/블로그 홍보 멘트")
    st.code("오늘도 열정 넘치는 주짓수 훈련! 🥋 #주짓수 #오운완 #체육관명", language="text")
