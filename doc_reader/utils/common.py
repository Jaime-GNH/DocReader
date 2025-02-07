from dotenv import load_dotenv, find_dotenv
import torch


def get_env_vars():
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path=dotenv_path)


def get_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'

