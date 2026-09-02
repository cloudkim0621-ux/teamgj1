import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 파일 경로
st.set_page_config(page_title="OSS! 주짓수 통합관리", layout="wide")
MEMBERS_FILE = "members_db.csv"
VIDEOS_FILE = "videos_db.csv"
PHOTOS_FILE = "photos_db.csv"
ATTEND_FILE = "attendance_db.csv"

# 2. 데이터 관리 함수
def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 세션 데이터 초기화
MEMBER_COLS = ["이름", "연락처", "구분", "벨트", "그랄", "최근승급일", "회비상태", "등록일", "상담기록"]

if 'df' not in st.session_state:
    st.session_state.df = load_data(MEMBERS_FILE, MEMBER_COLS)
    if "최근승급일" not in st.session_state.df.columns:
        st.session_state.df["최근승급일"] = datetime.now().strftime("%Y-%m-%d")

if 'vdf' not in st.session_state:
    st.session_state.vdf = load_data(VIDEOS_FILE, ["카테고리", "제목", "링크", "설명"])
if 'pdf' not in st.session_state:
    st.session_state.pdf = load_data(PHOTOS_FILE, ["날짜", "월", "이름", "메모", "이미지데이터"])
if 'adf' not in st.session_state:
    st.session_state.adf = load_data(ATTEND_FILE, ["날짜", "이름", "구분"])

# 3. 사이드바 메뉴
st.sidebar.title("🥋 OSS! ADMIN")
menu = st.sidebar.radio("메뉴 이동", [
    "🏠 홈/대시보드", 
    "🎓 관원 명단/승급", 
    "✅ 매일 출석체크",
    "📸 사진 성장기록",
    "💰 회비 수납관리", 
    "🎥 기술 영상 도서관", 
    "👪 상담/브랜딩"
])

# 선택지 목록
BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]
STRIPE_LIST = ["0그랄", "1그랄", "2그랄", "3그랄", "4그랄"]

BELT_COLORS = {
    "화이트": "#FFFFFF", "그레이": "#808080", "옐로우": "#FFD700", 
    "오렌지": "#FFA500", "블루": "#1E90FF", "퍼플": "#8A2BE2", 
    "브라운": "#8B4513", "블랙": "#000000"
}

# --- 메뉴별 기능 상세 ---

if menu == "🏠 홈/대시보드":
    st.title("📊 체육관 실시간 현황")
    df, adf, pdf, vdf = st.session_state.df, st.session_state.adf, st.session_state.pdf, st.session_state.vdf
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 관원", f"{len(df)}명")
    c2.metric("오늘 출석", f"{len(adf[adf['날짜'] == datetime.now().strftime('%Y-%m-%d')])}명")
    c3.metric("누적 사진", f"{len(pdf)}장")
    c4.metric("기술 영상", f"{len(vdf)}개")
    st.divider()
    st.subheader("📋 최근 등록 관원")
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "🎓 관원 명단/승급":
    st.title("🎓 관원 및 승급 관리")
    
    # 신규 관원 등록
    with st.expander("➕ 신규 관원 등록"):
        with st.form("add_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            name = col1.text_input("이름")
            contact = col2.text_input("연락처", "010-0000-0000")
            group = col3.selectbox("구분", ["일반부", "키즈부", "선수반"])
            
            belt = col1.selectbox("벨트 선택", BELT_LIST)
            stripe = col2.selectbox("그랄 선택", STRIPE_LIST)
            promo_date = col3.date_input("승급일자", datetime.now())
            
            if st.form_submit_button("등록 완료"):
                new_m = {
                    "이름": name, "연락처": contact, "구분": group, 
                    "벨트": belt, "그랄": stripe, 
                    "최근승급일": promo_date.strftime("%Y-%m-%d"),
                    "회비상태": "미납", "등록일": datetime.now().strftime("%Y-%m-%d"), "상담기록": ""
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_m])], ignore_index=True)
                save_data(st.session_state.df, MEMBERS_FILE)
                st.success(f"{name} 관원 등록 완료!")
                st.rerun()

    st.divider()
    
    # 카드 형식 전환 스위치
    card_view = st.toggle("카드 형식 전환", value=False)
    
    if card_view:
        # 카드 디자인 모드
        st.subheader("🥋 관원 프로필")
        if not st.session_state.df.empty:
            cols = st.columns(3)
            for idx, row in enumerate(st.session_state.df.itertuples()):
                b_color = BELT_COLORS.get(row.벨트, "#000000")
                t_color = "#FFFFFF" if row.벨트 in ["블랙", "브라운", "블루", "퍼플"] else "#000000"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div style="border: 2px solid #E0E0E0; border-radius: 12px; padding: 15px; margin-bottom: 15px; background-color: #FAFAFA; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin:0; color:#111;">{row.이름} <span style="font-size:14px; color:#666;">({row.구분})</span></h3>
                                <span style="background-color:{b_color}; color:{t_color}; padding:4px 12px; border-radius:20px; font-weight:bold; font-size:13px; border:1px solid #CCC;">
                                    {row.벨트} {row.그랄}
                                </span>
                            </div>
                            <hr style="margin: 10px 0;">
                            <p style="margin: 4px 0; font-size: 14px;"><b>📅 최근 승급일:</b> {row.최근승급일}</p>
                            <p style="margin: 4px 0; font-size: 14px;"><b>📞 연락처:</b> {row.연락처}</p>
                            <p style="margin: 4px 0; font-size: 14px;"><b>💳 회비:</b> <span style="color:{'red' if row.회비상태=='미납' else 'green'};"><b>{row.회비상태}</b></span></p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("등록된 관원이 없습니다.")
            
    else:
        # 기본 데이터 표 모드
        st.subheader("✏️ 관원 정보 빠른 편집")
        edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 변경사항 저장"):
            st.session_state.df = edited_df
            save_data(edited_df, MEMBERS_FILE)
            st.success("관원 명단 및 승급 정보가 저장되었습니다.")

elif menu == "✅ 매일 출석체크":
    st.title("✅ 오늘 훈련 출석")
    if not st.session_state.df.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        target = st.multiselect("출석한 관원들을 선택하세요", st.session_state.df["이름"])
        if st.button("출석 저장"):
            for name in target:
                new_a = {"날짜": today, "이름": name, "구분": "출석"}
                st.session_state.adf = pd.concat([st.session_state.adf, pd.DataFrame([new_a])], ignore_index=True)
            save_data(st.session_state.adf, ATTEND_FILE)
            st.success(f"{len(target)}명 출석 완료!")
        st.divider()
        st.subheader(f"📅 {today} 출석 명단")
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
    if not st.session_state.pdf.empty:
        sel_m = st.selectbox("달 선택", sorted(st.session_state.pdf["월"].unique(), reverse=True))
        f_pdf = st.session_state.pdf[st.session_state.pdf["월"] == sel_m]
        p_cols = st.columns(3)
        for i, row in enumerate(f_pdf.itertuples()):
            with p_cols[i % 3]:
                st.info(f"👤 {row.이름}")
                st.caption(f"📅 {row.날짜} | {row.메모}")

elif menu == "💰 회비 수납관리":
    st.title("💰 회비 수납 현황")
    st.write("미납자 명단")
    st.dataframe(st.session_state.df[st.session_state.df["회비상태"] == "미납"], use_container_width=True)

elif menu == "🎥 기술 영상 도서관":
    st.title("🎥 기술 영상 저장소")
    
    # 사이드바 영상 등록 창
    with st.sidebar:
        st.divider()
        st.subheader("📹 새 영상 등록")
        v_cat = st.selectbox("분류 선택", ["가드", "패스", "서브미션", "테이크다운", "기타"])
        v_name = st.text_input("기술명 (예: 니컷 패스)")
        v_link = st.text_input("유튜브 링크")
        if st.button("기술 영상 저장"):
            if v_name and v_link:
                new_v = {"카테고리": v_cat, "제목": v_name, "링크": v_link, "설명": ""}
                st.session_state.vdf = pd.concat([st.session_state.vdf, pd.DataFrame([new_v])], ignore_index=True)
                save_data(st.session_state.vdf, VIDEOS_FILE)
                st.success(f"'{v_name}' 영상이 저장되었습니다!")
                st.rerun()
            else:
                st.warning("기술명과 링크를 모두 입력해주세요.")

    vdf = st.session_state.vdf
    if not vdf.empty:
        # 카테고리 필터 (버그 해결)
        categories = ["전체"] + list(vdf["카테고리"].unique())
        selected_cat = st.radio("카테고리 필터", categories, horizontal=True)
        st.divider()

        if selected_cat == "전체":
            filtered_vdf = vdf
        else:
            filtered_vdf = vdf[vdf["카테고리"] == selected_cat]

        if not filtered_vdf.empty:
            v_cols = st.columns(2)
            for v_idx, v_row in enumerate(filtered_vdf.itertuples()):
                with v_cols[v_idx % 2]:
                    st.subheader(f"[{v_row.카테고리}] {v_row.제목}")
                    st.video(v_row.링크)
        else:
            st.info(f"'{selected_cat}' 카테고리에 등록된 영상이 없습니다.")
    else:
        st.info("등록된 기술 영상이 없습니다. 왼쪽 사이드바에서 영상 링크를 추가해보세요!")

elif menu == "👪 상담/브랜딩":
    st.title("📝 학부모 상담 기록")
    if not st.session_state.df.empty:
        s_target = st.selectbox("관원 선택", st.session_state.df["이름"])
        s_note = st.text_area("상담 내용 입력", height=300)
        if st.button("상담 일지 저장"):
            idx = st.session_state.df[st.session_state.df["이름"] == s_target].index[0]
            st.session_state.df.at[idx, "상담기록"] = s_note
            save_data(st.session_state.df, MEMBERS_FILE)
            st.success(f"{s_target} 관원의 상담 내용이 저장되었습니다.")
