import streamlit as st
import pandas as pd

st.set_page_config(page_title="주짓수 관리", layout="wide")
st.title("🥋 주짓수 관원 관리 시스템")

if 'list' not in st.session_state:
    st.session_state.list = pd.DataFrame(columns=["이름", "벨트"])

with st.sidebar:
    name = st.text_input("관원 이름")
    belt = st.selectbox("벨트", ["화이트", "블루", "퍼플", "브라운", "블랙"])
    if st.button("등록하기"):
        new_data = pd.DataFrame([{"이름": name, "벨트": belt}])
        st.session_state.list = pd.concat([st.session_state.list, new_data], ignore_index=True)
        st.rerun()

st.table(st.session_state.list)
