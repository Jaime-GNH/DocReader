from typing import Dict
from collections.abc import Callable
import streamlit as st
from app_pages import ConvertPage, ClonePage
from utils import get_env_vars


def start_page():
    st.set_page_config(page_title="Doc Reader", page_icon="📜",
                       layout="wide", initial_sidebar_state="expanded")
    if st.session_state.get('first_run', True):
        get_env_vars()
        st.session_state['first_run'] = False


def get_pages() -> Dict[str, Callable]:
    return {"📜 Convert": ConvertPage.run_page,
            "🎙️ Clone": ClonePage.run_page}


def set_sidebar():
    st.sidebar.subheader("""
    Navigation
    """)
    pages = get_pages()
    return pages[st.sidebar.selectbox(label="Navigator",
                                      label_visibility="hidden",
                                      options=pages,
                                      index=0)]()
