import cx_Freeze
from setuptools import find_packages
import sys
sys.setrecursionlimit(20000)
executables = [cx_Freeze.Executable("run.py", base="Win32GUI")]  # The main script
build_exe_options = {
    "packages": find_packages(exclude=["reporting", "resources", "scripts", "venv", ".git", ".idea"]),
    "includes": ["TTS", "nicegui",
                 "fitz", "num2words"],
    "include_files": [
        "app",
        "../resources/speakers", "../resources/text_conversions.json"],
    'build_exe': r'..\build'
}

cx_Freeze.setup(
    name="text2audio",  # The name of the exe
    options={"build_exe": build_exe_options},
    executables=executables
)
