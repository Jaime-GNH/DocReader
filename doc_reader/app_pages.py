import streamlit as st


class Page:
    """
    Page for using text to speech
    """
    @classmethod
    def run_page(cls):
        cls.page()

    @classmethod
    def page(cls):
        raise NotImplementedError("This class must be implemented.")


class ConvertPage(Page):
    """
    Page for using text to speech
    """
    @classmethod
    def page(cls):
        st.write("Converter page")
        return


class ClonePage(Page):
    """
    Page for cloning voice.
    """
    @classmethod
    def page(cls):
        st.write("Cloning page")
        return
