from contextlib import redirect_stdout, redirect_stderr

if __name__ == "__main__":
    with open('sys_err.txt', 'w') as f:
        with redirect_stderr(f):
            from app.app import App
            App().run_app()
