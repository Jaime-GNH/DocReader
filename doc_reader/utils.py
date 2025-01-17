from dotenv import load_dotenv, find_dotenv


def get_env_vars():
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path=dotenv_path)
