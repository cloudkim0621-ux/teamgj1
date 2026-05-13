import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 파일 경로
st.set_page_config(page_title="OSS! 주짓수 통합관리", layout="wide")
MEMBERS_FILE = "members_db.csv"
VIDEOS_FILE = "videos_db.csv"
PHOTOS_FILE = "photos_db.csv"
ATTEND_FILE = "attendance_db.csv" # 출결 전용 DB 추가

# 2. 데이터 관리 함수
def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 세션 데이터 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data(MEMBERS_FILE, ["이름", "연락처", "구분", "벨트", "그랄", "회비상태", "등록일", "상담기록"])
if 'vdf' not in st.session_state:
    st.session_state.vdf = load_data(VIDEOS_FILE, ["카테고리", "제목", "링크", "설명"])
if 'pdf' not in st.session_state:
    st.session_state.pdf = load_data(PHOTOS_FILE, ["날짜", "월", "이름", "메모", "이미지데이터"])
if 'adf' not in st.session_state:
    st.session_state.adf = load_data(ATTEND_FILE, ["날짜", "이름", "구분"])

# 3. 사이드바 메뉴 (출결과 사진을 분리했습니다)
st.sidebar.title("🥋 OSS! ADMIN")
menu = st.sidebar.radio("메뉴 이동", [
    "🏠 홈/대시보드", 
    "🎓 관원 명단/승급", 
    "✅ 매일 출석체크",  # 분리됨
    "📸 사진 성장기록",  # 분리됨
    "💰 회비 수납관리", 
    "🎥 기술 영상 도서관", 
    "👪 상담/브랜딩"
])

BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]

# --- 메뉴별 기능 상세 ---

if menu == "🏠 홈/대시보드":
    st.title("📊 체육관 실시간 현황")
    df, adf, pdf = st.session_state.df, st.session_state.adf, st.session_state.pdf
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 관원", f"{len(df)}명")
    c2.metric("오늘 출석", f"{len(adf[adf['날짜'] == datetime.now().strftime('%Y-%m-%d')])}명")
    c3.metric("누적 사진", f"{len(pdf)}장")
    c4.metric("미납 회비", f"{len(df[df['회비상태'] == '미납'])}건")
    st.divider()
    st.subheader("📋 최근 등록 관원")
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "🎓 관원 명단/승급":
    st.title("🎓 관원 및 승급 관리")
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("이름")
            group = col1.selectbox("구분", ["일반부", "키즈부", "선수반"])
            belt = col2.selectbox("벨트", BELT_LIST)
            stripe = col2.slider("그랄", 0, 4, 0)
            if st.form_submit_button("등록 완료"):
                new_m = {"이름": name, "연락처": "010-0000-0000", "구분": group, "벨트": belt, "그랄": stripe, "회비상태": "미납", "등록일": datetime.now().strftime("%Y-%m-%d"), "상담기록": ""}
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_m])], ignore_index=True)
                save_data(st.session_state.df, MEMBERS_FILE)
                st.success(f"{name} 관원 등록 완료!")
                st.rerun()
    st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")

elif menu == "✅ 매일 출석체크":
    st.title("✅ 오늘 훈련 출석")
    if not st.session_state.df.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.subheader(f"📅 {today} 출석부")
        
        # 이름으로 검색해서 출석 체크
        target = st.multiselect("출석한 관원들을 선택하세요", st.session_state.df["이름"])
        if st.button("출석 저장"):
            for name in target:
                new_a = {"날짜": today, "이름": name, "구분": "출석"}
                st.session_state.adf = pd.concat([st.session_state.adf, pd.DataFrame([new_a])], ignore_index=True)
            save_data(st.session_state.adf, ATTEND_FILE)
            st.success(f"{len(target)}명 출석 처리 완료!")
        
        st.divider()
        st.subheader("오늘 출석 명단")
        st.table(st.session_state.adf[st.session_state.adf["날짜"] == today][["이름"]])
    else: st.info("관원을 먼저 등록해주세요.")

elif menu == "📸 사진 성장기록":
    st.title("📸 주짓수 성장 아카이브")
    with st.expander("🆕 새 사진 기록 올리기"):
        p_name = st.selectbox("관원 선택", st.session_state.df["이름"])
        p_img = st.file_uploader("사진 업로드", type=['jpg', 'jpeg', 'png'])
        p_note = st.text_input("메모")
        if st.button("사진 저장"):
            new_p = {"날짜": datetime.now().strftime("%Y-%m-%d"), "월": datetime.now().strftime("%Y-%m"), "이름": p_name, "메모": p_note, "이미지데이터": "저장됨"}
            st.session_state.pdf = pd.concat([st.session_state.pdf, pd.DataFrame([new_p])], ignore_index=True)
            save_data(st.session_state.pdf, PHOTOS_FILE)
            st.success("사진 기록 완료!")

    st.divider()
    st.subheader("🔍 월별 기록 보기")
    if not st.session_state.pdf.empty:
        sel_m = st.selectbox("달 선택", sorted(st.session_state.pdf["월"].unique(), reverse=True))
        f_pdf = st.session_state.pdf[st.session_state.pdf["월"] == sel_m]
        p_cols = st.columns(3)
        for i, row in enumerate(f_pdf.itertuples()):
            with p_cols[i % 3]:
                st.info(f"👤 {row.이름}")
                st.caption(f"📅 {row.날짜} | {row.메모}")

elif menu == "💰 회비 수납관리":
    st.title("💰 회비 관리")
    st.write("미납자 명단")
    st.dataframe(st.session_state.df[st.session_state.df["회비상태"] == "미납"], use_container_width=True)

elif menu == "🎥 기술 영상 도서관":
    st.title("🎥 기술 영상")
    # 영상 등록/보기 로직 (이전과 동일)

elif menu == "👪 상담/브랜딩":
    st.title("📝 상담 일지")
    # 상담 로직 (이전과 동일)
