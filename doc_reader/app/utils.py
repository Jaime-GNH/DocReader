import winreg

import torch


def get_download_folder() -> str:
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
    winreg.CloseKey(reg_key)
    return downloads_path


def get_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'
