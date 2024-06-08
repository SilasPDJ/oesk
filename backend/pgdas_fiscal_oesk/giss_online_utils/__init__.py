from utilities.default import *
from utilities.compt_utils import *

weblink = 'https://portal.gissonline.com.br/login/index.html'
link = "ChromeDriver/chromedriver.exe"


class GissUtils(FileOperations, WDShorcuts):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def logar_giss(self):
        __senhas = os.getenv('GISS_PASSWORDS').split(',')

        driver = self.driver
        cont_senha = 0
        while True:
            # sometimes it's required to refresh...
            self.driver.get(weblink)
            driver.find_element(By.XPATH,
                                '//input[@name="TxtIdent"]').send_keys(self._logar)
            driver.find_element(By.XPATH,
                                '//input[@name="TxtSenha"]').send_keys(__senhas[cont_senha])
            # print(f'Senha: {__senhas[cont_senha]}', end=' ')
            senha = __senhas[cont_senha]

            self.__logar_giss_preenche_captcha()

            cont_senha += 1
            driver.find_element(By.LINK_TEXT, "Acessar").click()
            try:
                WebDriverWait(driver, 5).until(expected_conditions.alert_is_present(),
                                               'Timed out waiting for PA creation ' +
                                               'confirmation popup to appear.')
                alert = driver.switch_to.alert
                alert.accept()
                # print("estou no try")
                driver.execute_script("window.history.go(-1)")
            except TimeoutException:
                print("no alert, sem alerta, exceptado")
                break

    def __logar_giss_preenche_captcha(self):
        # from pgdas_fiscal_oesk.sbfconverter import SbFConverter

        def generate_autentic_list() -> list:
            autentic_list = list()
            iframe = self.webdriverwait_el_by(By.ID, 'frmDiv')
            self.driver.switch_to.frame(iframe)
            # vNumero > img:nth-child(5)
            for i in range(1, 5):
                query = f"body > table > tbody > tr > td:nth-child({i}) > img"
                img_name = f'giss.png'
                img = self.driver.find_element(By.CSS_SELECTOR, query)
                src = img.get_attribute("src")

                autentic_list.append(src.split("/images/autentic_")[-1][0])
                # print(autentic_list)
                # print('~'*30)
            print(autentic_list)
            return autentic_list

        autentic_list = generate_autentic_list()
        self.driver.switch_to.default_content()
        # get numbers =
        autenticate = {}

        query = f"#vNumero > img"
        img_nums = self.driver.find_elements(By.CSS_SELECTOR, query)
        for el in img_nums:
            src = el.get_attribute("src")
            tec = src.split("tec_")[-1][0]
            autenticate[tec] = el
        #     query = f"#vNumero > img:nth-child({i})"
        #     el = self.driver.find_element(By.CSS_SELECTOR, query)
        #     autenticate[tec] = el
        # print("~~Gerando giss cpt~~", src)
        print("~~Gerando giss cpt~~")
        # print(autenticate)
        self.webdriverwait_el_by(By.NAME, "accept").click()
        for v in autentic_list:
            sleep(.5)
            autenticate[v].click()

    def _detect_if_is_construcao_civil(self) -> bool:
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(0)

        if self.driver.find_element(By.ID, "7").get_attribute('onclick'):
            self.driver.switch_to.default_content()
            return True
        self.driver.switch_to.default_content()
        return False

    def _inserir_mes_e_competencia(self, compt_str: str):
        """
        :param compt_str: mm-yyyy
        :return: inserir mês e competência no portal do giss online
        """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(2)
        mes, ano = compt_str.split('-')

        mes_input_el = self.driver.find_element(By.NAME, "mes")
        ano_input_el = self.driver.find_element(By.NAME, "ano")
        mes_input_el.clear()
        ano_input_el.clear()

        mes_input_el.send_keys(mes)
        ano_input_el.send_keys(ano)
        self.driver.switch_to.default_content()
