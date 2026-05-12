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
        try:
            return pd.read_csv(file)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = load_data(MEMBERS_FILE, ["이름", "연락처", "구분", "벨트", "그랄", "회비상태", "등록일", "상담기록"])
if 'vdf' not in st.session_state:
    st.session_state.vdf = load_data(VIDEOS_FILE, ["카테고리", "제목", "링크", "설명"])

# 3. 사이드바 메뉴
st.sidebar.title("🥋 OSS! GYM MASTER")
menu = st.sidebar.radio("메뉴 이동", [
    "🏠 홈/대시보드", 
    "🎓 관원 명단/승급", 
    "📅 출결/성장기록", 
    "💰 회비 관리", 
    "🎥 기술 영상 도서관", 
    "👪 상담/브랜딩"
])

# 벨트 리스트 (관장님 요청 반영)
BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]

# --- 메뉴별 기능 ---

if menu == "🏠 홈/대시보드":
    st.title("📊 체육관 실시간 현황")
    df, vdf = st.session_state.df, st.session_state.vdf
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 관원", f"{len(df)}명")
    c2.metric("저장된 영상", f"{len(vdf)}개")
    c3.metric("미납 회비", f"{len(df[df['회비상태'] == '미납'])}건")
    st.divider()
    st.subheader("📋 최근 등록 관원")
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "🎓 관원 명단/승급":
    st.title("🎓 관원 및 승급 관리")
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_member", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("이름")
            contact = col2.text_input("연락처")
            group = col1.selectbox("구분", ["일반부", "키즈부", "선수반"])
            belt = col2.selectbox("벨트", BELT_LIST)
            stripe = st.slider("그랄", 0, 4, 0)
            if st.form_submit_button("등록"):
                new_m = {"이름": name, "연락처": contact, "구분": group, "벨트": belt, "그랄": stripe, "회비상태": "미납", "등록일": datetime.now().strftime("%Y-%m-%d"), "상담기록": ""}
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_m])], ignore_index=True)
                save_data(st.session_state.df, MEMBERS_FILE)
                st.rerun()
    
    st.subheader("✏️ 관원 정보 편집 (수정 후 저장 버튼 클릭)")
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 모든 변경사항 저장"):
        st.session_state.df = edited_df
        save_data(edited_df, MEMBERS_FILE)
        st.success("관원 명단이 업데이트되었습니다.")

elif menu == "📅 출결/성장기록":
    st.title("📅 출결 및 기술 성장")
    if not st.session_state.df.empty:
        target = st.selectbox("관원 선택", st.session_state.df["이름"])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 오늘 출석 완료"):
                st.success(f"{datetime.now().strftime('%m/%d')} {target} 관원 출석!")
        with c2:
            skill = st.text_input("오늘 배운 기술")
            if st.button("📝 성장기록 저장"):
                st.info(f"{target}: {skill} 기록됨")
    else:
        st.warning("먼저 관원을 등록해주세요.")

elif menu == "💰 회비 관리":
    st.title("💰 회비 수납 현황")
    unpaid = st.session_state.df[st.session_state.df["회비상태"] == "미납"]
    st.subheader(f"⚠️ 현재 미납자 ({len(unpaid)}명)")
    st.dataframe(unpaid[["이름", "연락처", "구분", "등록일"]], use_container_width=True)

elif menu == "🎥 기술 영상 도서관":
    st.title("🎥 기술 영상 저장소")
    with st.sidebar:
        st.subheader("📹 영상 추가")
        cat = st.selectbox("카테고리", ["가드", "패스", "서브미션", "테이크다운", "기타"])
        v_title = st.text_input("영상 제목")
        v_url = st.text_input("유튜브 링크")
        v_desc = st.text_area("설명")
        if st.button("영상 저장"):
            new_v = {"카테고리": cat, "제목": v_title, "링크": v_url, "설명": v_desc}
            st.session_state.vdf = pd.concat([st.session_state.vdf, pd.DataFrame([new_v])], ignore_index=True)
            save_data(st.session_state.vdf, VIDEOS_FILE)
            st.rerun()

    vdf = st.session_state.vdf
    if not vdf.empty:
        tabs = st.tabs(["전체"] + list(vdf["카테고리"].unique()))
        for i, tab in enumerate(tabs):
            with tab:
                f_vdf = vdf if i == 0 else vdf[vdf["카테고리"] == tab.label]
                for idx, row in f_vdf.iterrows():
                    with st.container():
                        c_a, c_b = st.columns([1, 2])
                        c_a.video(row["링크"])
                        c_b.subheader(row["제목"])
                        c_b.write(row["설명"])
                        st.divider()
    else:
        st.info("사이드바에서 기술 영상을 등록해 보세요!")

elif menu == "👪 상담/브랜딩":
    st.title("📝 상담 및 브랜딩")
    target_c = st.selectbox("관원 선택", st.session_state.df["이름"])
    note = st.text_area("상담 내용 입력")
    if st.button("상담 내용 저장"):
        idx = st.session_state.df[st.session_state.df["이름"] == target_c].index[0]
        st.session_state.df.at[idx, "상담기록"] = note
        save_data(st.session_state.df, MEMBERS_FILE)
        st.success("상담 일지가 저장되었습니다.")
