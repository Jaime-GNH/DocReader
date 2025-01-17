import streamlit as st
from app_components import start_page, set_sidebar


class App:
    @classmethod
    def run_app(cls):
        start_page()
        set_sidebar()
