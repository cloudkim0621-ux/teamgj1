import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="OSS! 주짓수 통합관리", layout="wide", initial_sidebar_state="expanded")

# 2. 데이터 초기화 (세션 상태 활용 - 실제 운영 시 DB 연동 추천)
if 'members' not in st.session_state:
    st.session_state.members = pd.DataFrame([
        {"이름": "김주짓", "벨트": "블루", "그랄": 2, "회비": "완납", "구분": "일반부", "연락처": "010-1234-5678"},
        {"이름": "이체크", "벨트": "화이트", "그랄": 4, "회비": "미납", "구분": "선수반", "연락처": "010-9876-5432"}
    ])

if 'logs' not in st.session_state:
    st.session_state.logs = [] # 출결 및 상담 기록용

# 3. 사이드바 내비게이션
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3253/3253773.png", width=100)
    st.title("OSS! GYM ADMIN")
    menu = st.radio("메뉴 이동", [
        "🏠 대시보드", 
        "🎓 승급/관원 관리", 
        "📅 출결/성장기록", 
        "💰 회비/미납 관리", 
        "👪 학부모 소통/상담", 
        "🏆 대회/선수반 관리", 
        "🎥 영상공유/브랜딩"
    ])
    st.info("로그아웃 하시려면 브라우저를 닫으세요.")

# --- 메뉴별 기능 구현 ---

# [1] 대시보드 (홈/통계)
if menu == "🏠 대시보드":
    st.title("📊 체육관 운영 현황")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 관원", f"{len(st.session_state.members)}명")
    c2.metric("미납 회비", f"{len(st.session_state.members[st.session_state.members['회비'] == '미납'])}건")
    c3.metric("오늘 출석", "15명") # 가상 데이터
    c4.metric("대회 준비인원", "4명")

    st.divider()
    st.subheader("🔔 주요 알림")
    st.warning("이체크 관원의 회비가 3일 지났습니다.")
    st.info("이번 주 금요일 승급 심사가 예정되어 있습니다.")

# [2] 승급/관원 관리 (띠 관리 포함)
elif menu == "🎓 승급/관원 관리":
    st.title("🎓 관원 명단 및 승급 관리")
    
    # 관원 추가 기능
    with st.expander("➕ 신규 관원 등록"):
        with st.form("new_member"):
            name = st.text_input("이름")
            belt = st.selectbox("벨트", ["화이트", "블루", "퍼플", "브라운", "블랙"])
            stripe = st.slider("그랄", 0, 4, 0)
            group = st.selectbox("구분", ["일반부", "선수반", "키즈부"])
            contact = st.text_input("연락처")
            if st.form_submit_button("등록 완료"):
                new_entry = {"이름": name, "벨트": belt, "그랄": stripe, "회비": "미납", "구분": group, "연락처": contact}
                st.session_state.members = pd.concat([st.session_state.members, pd.DataFrame([new_entry])], ignore_index=True)
                st.success(f"{name} 관원이 등록되었습니다.")
                st.rerun()

    # 명단 편집 (승급 처리)
    st.subheader("👥 명단 편집 (그랄/띠 변경)")
    edited_df = st.data_editor(st.session_state.members, use_container_width=True, num_rows="dynamic")
    if st.button("💾 변경사항 저장"):
        st.session_state.members = edited_df
        st.success("정보가 업데이트되었습니다.")

# [3] 출결/성장기록
elif menu == "📅 출결/성장기록":
    st.title("📅 출결 및 성장 기록")
    
    tab1, tab2 = st.tabs(["출석 체크", "성장 기록(기술 습득)"])
    
    with tab1:
        name = st.selectbox("출석 관원 선택", st.session_state.members["이름"])
        if st.button("출석 확인"):
            log = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {name} - 출석 완료"
            st.session_state.logs.append(log)
            st.success(log)
            
    with tab2:
        target = st.selectbox("기록할 관원", st.session_state.members["이름"], key="growth")
        skill = st.text_input("오늘 배운 기술 (ex. 데라히바 가드)")
        rating = st.select_slider("이해도", options=["미숙", "보통", "우수", "완벽"])
        if st.button("기록 저장"):
            st.info(f"{target} 관원의 {skill} 이해도가 '{rating}'로 기록되었습니다.")

# [4] 회비/미납 관리
elif menu == "💰 회비/미납 관리":
    st.title("💰 회비 수납 관리")
    unpaid = st.session_state.members[st.session_state.members["회비"] == "미납"]
    
    st.subheader(f"⚠️ 미납자 현황 ({len(unpaid)}명)")
    st.dataframe(unpaid[["이름", "연락처", "구분"]], use_container_width=True)
    
    if st.button("📢 미납자 전체 알림톡 전송(가상)"):
        st.success("미납 관원들에게 안내 메시지가 발송되었습니다.")

# [5] 학부모 소통/상담
elif menu == "👪 학부모 소통/상담":
    st.title("👪 학부모 상담 및 소통")
    parent_target = st.selectbox("대상 관원(아이)", st.session_state.members[st.session_state.members["구분"]=="키즈부"]["이름"] if not st.session_state.members[st.session_state.members["구분"]=="키즈부"].empty else ["대상 없음"])
    counsel_note = st.text_area("상담 내용 기록")
    if st.button("상담 일지 저장"):
        st.success(f"{parent_target} 상담 내용이 저장되었습니다.")
        st.write("---")
        st.info("알림: 저장된 내용은 나중에 '학부모 전용 앱'으로 연동할 수 있습니다.")

# [6] 대회/선수반 관리
elif menu == "🏆 대회/선수반 관리":
    st.title("🏆 대회 출전 및 선수반 특별 관리")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🥇 대회 출전 명단")
        st.write("- 24년 6월 서울 오픈: 김주짓(-76kg)")
        st.write("- 24년 7월 지역 대회: 이체크(-82kg)")
        
    with col_b:
        st.subheader("🏋️ 선수반 훈련 강도")
        st.progress(85, text="이번 주 훈련 강도 85%")
        st.write("중점 사항: 스파링 디테일 및 체력 훈련")

# [7] 영상공유/브랜딩
elif menu == "🎥 영상공유/브랜딩":
    st.title("🎥 기술 영상 및 체육관 브랜딩")
    
    st.subheader("🔗 오늘의 복습 영상")
    video_url = st.text_input("유튜브 기술 영상 링크", "https://www.youtube.com/watch?v=your_video_id")
    st.video(video_url)
    
    st.divider()
    st.subheader("📢 브랜딩/마케팅 도구")
    if st.button("📱 인스타그램 홍보 문구 생성"):
        st.code(f"오늘도 뜨거운 열기의 {st.session_state.members.iloc[0]['구분']}! 🥋\n함께 땀 흘릴 파트너를 기다립니다. #주짓수 #운동 #오운완", language="text")
