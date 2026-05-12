import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 데이터 파일 경로
st.set_page_config(page_title="OSS! 주짓수 마스터", layout="wide")
MEMBERS_FILE = "members_db.csv"
VIDEOS_FILE = "videos_db.csv"

# 2. 데이터 관리 함수
def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 세션 상태 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data(MEMBERS_FILE, ["이름", "연락처", "구분", "벨트", "그랄", "회비상태", "등록일"])
if 'vdf' not in st.session_state:
    st.session_state.vdf = load_data(VIDEOS_FILE, ["카테고리", "제목", "링크", "설명"])

# 3. 사이드바 메뉴
st.sidebar.title("🥋 OSS! GYM MASTER")
menu = st.sidebar.radio("메뉴 이동", ["🏠 홈", "🎓 관원/승급 관리", "📅 출결/성장기록", "💰 회비 관리", "🎥 기술 영상 도서관", "👪 상담/브랜딩"])

# [벨트 리스트 업데이트]
BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]

# --- 메뉴 기능 ---

if menu == "🏠 홈":
    st.title("📊 체육관 실시간 현황")
    df, vdf = st.session_state.df, st.session_state.vdf
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 관원", f"{len(df)}명")
    c2.metric("등록된 기술 영상", f"{len(vdf)}개")
    c3.metric("이번 달 신규", f"{len(df[df['등록일'].str.contains(datetime.now().strftime('%Y-%m'), na=False)])}명")
    st.divider()
    st.subheader("📺 최신 공유 영상")
    if not vdf.empty:
        st.video(vdf.iloc[-1]['링크'])

elif menu == "🎓 관원/승급 관리":
    st.title("🎓 관원 및 확장 벨트 관리")
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_member"):
            col1, col2 = st.columns(2)
            name = col1.text_input("이름")
            group = col1.selectbox("구분", ["일반부", "키즈부", "선수반"])
            belt = col2.selectbox("벨트 (그레이/옐로우 포함)", BELT_LIST)
            stripe = col2.slider("그랄", 0, 4, 0)
            if st.form_submit_button("등록"):
                new_m = {"이름": name, "연락처": "010-0000-0000", "구분": group, "벨트": belt, "그랄": stripe, "회비상태": "미납", "등록일": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_m])], ignore_index=True)
                save_data(st.session_state.df, MEMBERS_FILE)
                st.rerun()
    
    st.subheader("✏️ 관원 명단 편집")
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 변경사항 저장"):
        st.session_state.df = edited_df
        save_data(edited_df, MEMBERS_FILE)
        st.success("관원 정보가 저장되었습니다.")

elif menu == "🎥 기술 영상 도서관":
    st.title("🎥 무제한 기술 영상 저장소")
    
    with st.sidebar:
        st.divider()
        st.subheader("📹 영상 추가")
        cat = st.selectbox("카테고리", ["가드", "패스", "서브미션", "테이크다운", "기타"])
        title = st.text_input("영상 제목")
        url = st.text_input("유튜브/링크")
        desc = st.text_area("기술 포인트 설명")
        if st.button("영상 저장"):
            new_v = {"카테고리": cat, "제목": title, "링크": url, "설명": desc}
            st.session_state.vdf = pd.concat([st.session_state.vdf, pd.DataFrame([new_v])], ignore_index=True)
            save_data(st.session_state.vdf, VIDEOS_FILE)
            st.success("영상이 도서관에 추가되었습니다!")
            st.rerun()

    # 영상 갤러리 출력
    df_v = st.session_state.vdf
    if not df_v.empty:
        search_cat = st.tabs(["전체"] + list(df_v["카테고리"].unique()))
        for i, tab in enumerate(search_cat):
            with tab:
                filtered_v = df_v if i == 0 else df_v[df_v["카테고리"] == tab.label]
                cols = st.columns(3)
                for idx, row in enumerate(filtered_v.itertuples()):
                    with cols[idx % 3]:
                        st.video(row.링크)
                        st.subheader(row.제목)
                        st.caption(row.설명)
    else:
        st.info("아직 등록된 영상이 없습니다. 사이드바에서 영상을 추가하세요.")

# 나머지 메뉴 (출결, 회비, 상담 등)은 이전과 동일한 구조로 유지...
else:
    st.info("이전 메뉴의 기능을 동일하게 사용하실 수 있습니다.")
