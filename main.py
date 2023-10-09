import os
from interface.oesk import App
from dotenv import load_dotenv

def execute_app():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    load_dotenv()
    execute_app()

