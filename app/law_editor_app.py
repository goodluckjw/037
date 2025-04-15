import streamlit as st
from processing.law_processor import get_law_list_from_api, get_highlighted_articles

st.set_page_config(page_title="검색어를 포함하는 법률 목록")

st.title("🔍 검색어를 포함하는 법률 목록")
st.caption("📄 본문 중에 검색어를 포함하는 법률의 목록을 반환합니다.")

if "stop_search" not in st.session_state:
    st.session_state.stop_search = False
if "last_search" not in st.session_state:
    st.session_state.last_search = ""
if "law_details" not in st.session_state:
    st.session_state.law_details = {}

search_word = st.text_input("검색어 입력")

col1, col2, col3 = st.columns(3)
with col1:
    start = st.button("🚀 시작하기")
with col2:
    if st.button("🛑 멈춤"):
        st.session_state.stop_search = True
with col3:
    if st.button("🔄 초기화"):
        st.session_state.stop_search = False
        st.session_state.last_search = ""
        st.session_state.law_details = {}
        st.rerun()

if start:
    if not search_word:
        st.warning("검색어를 입력해주세요.")
    else:
        if search_word != st.session_state.last_search:
            st.session_state.law_details = {}
            st.session_state.stop_search = False
        st.session_state.last_search = search_word
        st.session_state.stop_search = False

        with st.spinner("법령 검색 중..."):
            laws = get_law_list_from_api(search_word)
            st.success(f"✅ 총 {len(laws)}개의 법령을 찾았습니다.")

            for idx, law in enumerate(laws, 1):
                if st.session_state.stop_search:
                    st.warning("⛔ 검색이 중단되었습니다.")
                    break

                key = law['MST']
                with st.expander(f"{idx:02d}. {law['법령명']}"):
                    st.markdown(f"[🔗 원문 보기]({law['URL']})", unsafe_allow_html=True)
                    if key not in st.session_state.law_details:
                        result = get_highlighted_articles(key, search_word)
                        st.session_state.law_details[key] = result
                    st.markdown(st.session_state.law_details[key], unsafe_allow_html=True)
