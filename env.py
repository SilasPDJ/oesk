from os.path import isfile
from dotenv import dotenv_values


class Util:
    def __init__(self, filename=".env"):
        if not isfile(filename):
            raise FileNotFoundError(f'Arquivo {filename} não encontrado')
        self.env_vars = dotenv_values(filename)

    def get(self, key, default=None):
        return self.env_vars.get(key, default)


class DotEnv(Util):
    def __init__(self, filename=".env"):
        super().__init__(filename)
        self.MAIN_PATH = self.get('MAIN_PATH')
        self.CONTIMATIC_LOGIN = self.get('CONTMATIC_LOGIN')
        self.CONTIMATIC_PASSWORD = self.get('CONTMATIC_PASSWORD')
        self.GISS_PASSWORDS = self.get('GISS_PASSWORDS').split(',')

if __name__ == '__main__':
    env = DotEnv()
    a = env.GISS_PASSWORDS
    print(a)