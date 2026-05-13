import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 파일 경로
st.set_page_config(page_title="OSS! 주짓수 통합관리", layout="wide")
MEMBERS_FILE = "members_db.csv"
VIDEOS_FILE = "videos_db.csv"
PHOTOS_FILE = "photos_db.csv" # 사진 기록용 데이터베이스

# 2. 데이터 관리 함수
def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 데이터 세션 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data(MEMBERS_FILE, ["이름", "연락처", "구분", "벨트", "그랄", "회비상태", "등록일", "상담기록"])
if 'vdf' not in st.session_state:
    st.session_state.vdf = load_data(VIDEOS_FILE, ["카테고리", "제목", "링크", "설명"])
if 'pdf' not in st.session_state:
    st.session_state.pdf = load_data(PHOTOS_FILE, ["날짜", "월", "이름", "메모", "이미지데이터"])

# 3. 사이드바 메뉴
st.sidebar.title("🥋 OSS! GYM ADMIN")
menu = st.sidebar.radio("메뉴 이동", [
    "🏠 홈/대시보드", 
    "🎓 관원 명단/승급", 
    "📅 출결/사진기록", 
    "💰 회비 수납관리", 
    "🎥 기술 영상 도서관", 
    "👪 상담/브랜딩"
])

BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]

# --- 메뉴별 기능 상세 ---

if menu == "🏠 홈/대시보드":
    st.title("📊 체육관 실시간 현황")
    df, vdf, pdf = st.session_state.df, st.session_state.vdf, st.session_state.pdf
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 관원", f"{len(df)}명")
    c2.metric("기술 영상", f"{len(vdf)}개")
    c3.metric("누적 사진기록", f"{len(pdf)}장")
    st.divider()
    st.subheader("📋 최근 등록 관원")
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "🎓 관원 명단/승급":
    st.title("🎓 관원 및 승급 관리")
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("이름")
            contact = col2.text_input("연락처")
            group = col1.selectbox("구분", ["일반부", "키즈부", "선수반"])
            belt = col2.selectbox("벨트", BELT_LIST)
            stripe = st.slider("그랄", 0, 4, 0)
            if st.form_submit_button("등록 완료"):
                new_m = {"이름": name, "연락처": contact, "구분": group, "벨트": belt, "그랄": stripe, "회비상태": "미납", "등록일": datetime.now().strftime("%Y-%m-%d"), "상담기록": ""}
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_m])], ignore_index=True)
                save_data(st.session_state.df, MEMBERS_FILE)
                st.success(f"{name} 관원이 등록되었습니다!")
                st.rerun()
    
    st.subheader("✏️ 관원 정보 편집")
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 변경사항 저장"):
        st.session_state.df = edited_df
        save_data(edited_df, MEMBERS_FILE)
        st.success("데이터가 안전하게 저장되었습니다!")

elif menu == "📅 출결/사진기록":
    st.title("📅 월별 사진 성장 기록")
    
    # 1. 사진 업로드 섹션
    with st.expander("📸 오늘의 훈련 사진 올리기"):
        if not st.session_state.df.empty:
            c1, c2 = st.columns(2)
            p_name = c1.selectbox("관원 선택", st.session_state.df["이름"])
            p_date = c2.date_input("날짜 선택", datetime.now())
            p_month = p_date.strftime("%Y-%m")
            p_img = st.file_uploader("사진 찍기 또는 선택", type=['jpg', 'jpeg', 'png'])
            p_note = st.text_input("짧은 메모 (예: 오늘 스파링 최고!)")
            
            if st.button("기록 저장"):
                if p_img:
                    # 사진 기록 저장 로직 (메타데이터 위주)
                    new_p = {"날짜": p_date, "월": p_month, "이름": p_name, "메모": p_note, "이미지데이터": "저장됨"}
                    st.session_state.pdf = pd.concat([st.session_state.pdf, pd.DataFrame([new_p])], ignore_index=True)
                    save_data(st.session_state.pdf, PHOTOS_FILE)
                    st.success(f"{p_name} 관원 사진 기록 완료!")
                else: st.warning("사진을 올려주세요.")
        else: st.info("관원을 먼저 등록해주세요.")

    st.divider()
    
    # 2. 월별 사진 조회 (수천 장 관리용)
    st.subheader("🔍 월별 기록 찾아보기")
    if not st.session_state.pdf.empty:
        all_months = sorted(st.session_state.pdf["월"].unique(), reverse=True)
        sel_month = st.selectbox("보고 싶은 달 선택", all_months)
        
        filtered_pdf = st.session_state.pdf[st.session_state.pdf["월"] == sel_month]
        cols = st.columns(3)
        for idx, row in enumerate(filtered_pdf.itertuples()):
            with cols[idx % 3]:
                st.info(f"👤 {row.이름}")
                st.caption(f"📅 {row.날짜} | 📝 {row.메모}")
    else:
        st.info("아직 등록된 사진 기록이 없습니다.")

elif menu == "💰 회비 수납관리":
    st.title("💰 회비 미납자 목록")
    unpaid = st.session_state.df[st.session_state.df["회비상태"] == "미납"]
    st.dataframe(unpaid[["이름", "연락처", "구분", "등록일"]], use_container_width=True)

elif menu == "🎥 기술 영상 도서관":
    st.title("🎥 무제한 기술 영상 저장소")
    with st.sidebar:
        st.divider()
        st.subheader("📹 영상 추가")
        v_cat = st.selectbox("분류", ["가드", "패스", "서브미션", "테이크다운", "기타"])
        v_name = st.text_input("기술명")
        v_link = st.text_input("유튜브 링크")
        if st.button("기술 저장"):
            new_v = {"카테고리": v_cat, "제목": v_name, "링크": v_link, "설명": ""}
            st.session_state.vdf = pd.concat([st.session_state.vdf, pd.DataFrame([new_v])], ignore_index=True)
            save_data(st.session_state.vdf, VIDEOS_FILE)
            st.rerun()

    vdf = st.session_state.vdf
    if not vdf.empty:
        v_tabs = st.tabs(["전체"] + list(vdf["카테고리"].unique()))
        for i, tab in enumerate(v_tabs):
            with tab:
                f_vdf = vdf if i == 0 else vdf[vdf["카테고리"] == tab.label]
                v_cols = st.columns(2)
                for v_idx, v_row in enumerate(f_vdf.itertuples()):
                    with v_cols[v_idx % 2]:
                        st.video(v_row.링크)
                        st.subheader(v_row.제목)
    else: st.info("영상을 등록해주세요.")

elif menu == "👪 상담/브랜딩":
    st.title("📝 학부모 상담 및 특이사항")
    if not st.session_state.df.empty:
        s_target = st.selectbox("관원 선택", st.session_state.df["이름"], key="s_target")
        s_note = st.text_area("상담 내용 기록", height=200)
        if st.button("상담 일지 저장"):
            idx = st.session_state.df[st.session_state.df["이름"] == s_target].index[0]
            st.session_state.df.at[idx, "상담기록"] = s_note
            save_data(st.session_state.df, MEMBERS_FILE)
            st.success(f"{s_target} 관원의 상담 내용이 저장되었습니다.")
    else: st.info("관원을 먼저 등록해주세요.")
