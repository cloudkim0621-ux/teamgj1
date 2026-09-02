import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 파일 경로
st.set_page_config(page_title="OSS! 주짓수 통합관리 & AI 마스터", layout="wide")
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
    "🤖 주짓수 AI 마스터",
    "🎓 관원 명단/승급", 
    "✅ 매일 출석체크",
    "📸 사진 성장기록",
    "💰 회비 수납관리", 
    "🎥 기술 영상 도서관", 
    "👪 상담/브랜딩"
])

# 선택지 목록 및 상수
BELT_LIST = ["화이트", "그레이", "옐로우", "오렌지", "블루", "퍼플", "브라운", "블랙"]
STRIPE_LIST = ["0그랄", "1그랄", "2그랄", "3그랄", "4그랄"]
BELT_COLORS = {
    "화이트": "#FFFFFF", "그레이": "#808080", "옐로우": "#FFD700", 
    "오렌지": "#FFA500", "블루": "#1E90FF", "퍼플": "#8A2BE2", 
    "브라운": "#8B4513", "블랙": "#000000"
}

# --- 주짓수 AI 전문 지식 DB (AI 마스터용) ---
BJJ_KNOWLEDGE_BASE = {
    "삼각초크": {
        "카테고리": "서브미션 (가드)",
        "핵심 디테일": "1. 상대의 한 손은 안으로, 한 손은 밖으로 제어합니다.\n2. 골반을 틀어 상대 목 뒤로 다리를 세게 감아 잠급니다.\n3. 상대 머리를 당기면서 골반을 올려 압박을 극대화합니다.",
        "추천 연계기": "삼각초크 방어 시 ➡️ 암바(Armbar) 또는 옴플라타(Omoplata) 전환",
        "카운터/방어법": "상체를 곧게 세우고(Posture) 상대 골반을 눌러 다리 잠금을 풀고 패스시도"
    },
    "암바": {
        "카테고리": "서브미션 (공통)",
        "핵심 디테일": "1. 상대 팔꿈치가 내 엄지손가락 방향(하늘)을 향하도록 당깁니다.\n2. 내 골반을 상대 어깨에 바짝 밀착시킵니다.\n3. 무릎을 조이고 골반을 위로 천천히 들어올립니다.",
        "추천 연계기": "상대가 팔을 당겨 방어할 때 ➡️ 삼각초크 또는 옴플라타",
        "카운터/방어법": "양손을 잡고(Grip) 상대 다리 밑으로 몸을 파고들어 스태킹(Stack) 후 패스"
    },
    "니컷 패스": {
        "카테고리": "가드 패스",
        "핵심 디테일": "1. 상대의 깃과 팔꿈치 안쪽(Underhook)을 확실히 잡습니다.\n2. 무릎을 상대 허벅지 위로 대각선 방향으로 가르며 슬라이드합니다.\n3. 머리를 낮춰 상대의 상체를 제압합니다.",
        "추천 연계기": "상대가 무릎을 밀어낼 때 ➡️ 스핀 패스 또는 마운트 전환",
        "카운터/방어법": "언더훅을 빼앗기지 않고 언더훅을 먼저 파거나 K-가드/셰일드 가드 설정"
    },
    "클로즈드 가드": {
        "카테고리": "가드",
        "핵심 디테일": "1. 발목을 다잡아 상대 허리를 단단히 감쌉니다.\n2. 상대의 상체 자세(Posture)를 무너뜨리기 위해 깃과 소매를 당깁니다.\n3. 골반 움직임을 지속적으로 줍니다.",
        "추천 연계기": "크로스 깃 초크 ➡️ 삼각초크 ➡️ 펜듈럼 스위프",
        "카운터/방어법": "허리를 세우고 상대 라펠을 잡아 골반을 누르며 일어서서 패스"
    },
    "기요틴 초크": {
        "카테고리": "서브미션",
        "핵심 디테일": "1. 상대 머리를 목 안쪽으로 깊숙이 파고듭니다.\n2. 턱을 가슴에 붙이고 손목을 상대 목젖 밑으로 밀어 넣습니다.\n3. 가드를 잠그고 상체를 접어 압박합니다.",
        "추천 연계기": "기요틴 시도 중 상대가 머리를 뺄 때 ➡️ 안스라 초크 또는 범프 스위프",
        "카운터/방어법": "상대 머리가 있는 쪽 어깨 위로 손을 넘겨 몸을 회전(Von Flue Choke 각도)"
    }
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

elif menu == "🤖 주짓수 AI 마스터":
    st.title("🤖 주짓수 AI 전문 코치")
    st.caption("주짓수 기술 디테일, 추천 콤비네이션, 방어법을 즉시 답변해 드립니다.")
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🔍 기술 및 궁금한 질문 분석")
        user_query = st.text_input("질문 입력 (예: 삼각초크, 니컷 패스, 초보자 추천 서브미션)", "삼각초크")
        
        st.markdown("#### 💡 AI 추천 프리셋 질문")
        btn1, btn2, btn3 = st.columns(3)
        if btn1.button("🥋 가드 세팅 팁"): user_query = "클로즈드 가드"
        if btn2.button("⚡ 니컷 패스 팁"): user_query = "니컷 패스"
        if btn3.button("💥 초크 디테일"): user_query = "기요틴 초크"

    with col2:
        st.subheader("📋 AI 코칭 결과")
        found = False
        for key, info in BJJ_KNOWLEDGE_BASE.items():
            if key in user_query or user_query in key:
                found = True
                st.success(f"### [{info['카테고리']}] {key}")
                st.markdown(f"**🎯 핵심 디테일:**\n{info['핵심 디테일']}")
                st.info(f"**🔄 추천 연계기 (Combination):**\n{info['추천 연계기']}")
                st.warning(f"**🛡️ 카운터 및 방어법 (Defense):**\n{info['카운터/방어법']}")
                break
        
        if not found:
            st.info(f"💡 '{user_query}'에 대한 맞춤 AI 코칭:")
            st.write("• **포지션 우선:** 항상 가드 세팅 후 서브미션을 노리세요.")
            st.write("• **기본기 강조:** 상체의 포스처(Posture)를 무너뜨리는 것이 첫 번째입니다.")
            st.write("• **자세한 검색:** '삼각초크', '암바', '니컷 패스', '기요틴 초크' 등의 단어로 검색하시면 세부 디테일을 확인할 수 있습니다.")

elif menu == "🎓 관원 명단/승급":
    st.title("🎓 관원 및 승급 관리")
    
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
    card_view = st.toggle("카드 형식 전환", value=False)
    
    if card_view:
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
