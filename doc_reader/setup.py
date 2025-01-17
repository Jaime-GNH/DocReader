from setuptools import setup

setup(
    name="doc_reader",
    version="0.0.0.1",
    packages=["doc_reader"],
    install_requires=["python>=3.12",
                      "coqui-tts>=0.25",
                      "streamlit>=1.4",
                      "python-dotenv>=1.0.1"],
    description="App for converting text files to audio (Spanish)."
)
