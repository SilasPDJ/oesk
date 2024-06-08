# dale
from bs4 import BeautifulSoup

from pgdas_fiscal_oesk.giss_online_utils import GissUtils
from utilities.default import *
from utilities.compt_utils import *
from dotenv import load_dotenv

load_dotenv()


# from . import *
# qualquer coisa me devolve


# self.pyautogui
class GissISSQN(GissUtils):
    def __init__(self, dados, compt, headless=True):
        from functools import partial
        self._COMPT = compt
        # [print(s) for s in __senhas]
        __r_social, _giss_cnpj, self._logar = dados[:3]
        self.compt_atual = compt
        print('~' * 30)
        print(self.compt_atual)
        print(f"{__r_social}: Giss")

        self.client_path = self.files_pathit(
            __r_social.strip(), compt)

        if headless:
            self.driver = driver = ginfess_driver(self.client_path)
        else:
            self.driver = driver = pgdas_driver(self.client_path)
        # self.driver.set_window_position(2000, 0)
        super().__init__(self.driver)
        self.logar_giss()

        is_construcao_civil = self._detect_if_is_construcao_civil()

        if not is_construcao_civil:
            self.driver.switch_to.default_content()

            self.driver.switch_to.frame(0)
            self.driver.find_element(By.ID, "5").click()
            self.driver.switch_to.default_content()

            self._inserir_mes_e_competencia(self.compt_atual)
            self._check_prestador_guias()
            print('test+')

    def __notas_recebidas(self):
        driver = self.driver
        driver.execute_script(
            "if(verificaCompetencia())window.location = '/recebidas/listaNotas.cfm?modalidade=T';")
        # raise UnexpectedAlertPresentException
        driver.switch_to.default_content()
        iframe = self.webdriverwait_el_by(
            By.XPATH, "//iframe[@name='principal']")
        driver.switch_to.frame(iframe)
        driver.find_element(By.ID, "marcar").click()
        self.click_ac_elementors(
            driver.find_element(By.ID, "aceita2"))
        driver.implicitly_wait(10)
        self.webdriverwait_el_by(By.NAME, "form01")
        driver.execute_script("validarFormObra();")
        try:
            driver.switch_to.alert.accept()
        except Exception as e:
            pass
        driver.switch_to.default_content()

    def _check_prestador_guias(self):

        driver = self.driver

        # driver.find_element(By.XPATH,
        #     '//img[contains(@src,"bt_menu__05_off.jpg")]').click()
        driver.switch_to.default_content()
        iframe = driver.find_element(By.XPATH, "//iframe[@name='principal']")
        driver.switch_to.frame(iframe)
        try:
            el = self.tag_with_text('a', 'Conta Corrente')

            el.click()
            # year_selected = self.tag_with_text('font', self.compt_atual.split('-')[-1])
            # self.click_ac_elementors(year_selected)
            self.click_elements_by_tt(self.compt_atual.split('-')[-1])

            # tabela com as guias
            table = self.driver.find_elements(By.TAG_NAME, 'table')
            # -- old

            # -- ---
            # driver.switch_to.default_content()
            self._download_prestador_guias(table)
            # driver.find_element(By.ID, )
        except NoSuchElementException as e:
            print("Erro na geração de boletos do GISS Online!")
            # raise e
        driver.switch_to.default_content()
        iframe = driver.find_element(By.XPATH, "//iframe[@name='header']")
        driver.switch_to.frame(iframe)
        driver.execute_script('javascript: clickPrestador(); ')
        driver.switch_to.default_content()

    def _download_prestador_guias(self, tables):
        # ---- complementação out/2022
        # self.driver.switch_to.default_content()
        table1 = tables[1]
        t_get_years = tables[0]

        # ttr_years = table1.find_elements(By.TAG_NAME, 'tr')[1]
        # el_years = table1.find_elements(By.TAG_NAME, 'td')
        #
        # year = self._COMPT.split('-')[1]
        # self.webdriverwait_el_by(By.XPATH, f"//a[contains(@href, \"javascript:AlteraFrame('{year}', 'C','C')\")]")
        tb = table1

        # ---- fim complementação
        # pois a primeira é com anos

        __meses_guias = tb.find_elements(By.TAG_NAME, 'a')
        MESES, GUIAS = (
            [mes for mes in __meses_guias if mes.text != ''],
            [guia for guia in __meses_guias if guia.text == '']
        )
        # TODO: Verificar (do código daqpbaixo) se irá ser downloadado boleto.pdf...
        # [print(mes.text) for mes in MESES]
        # [print(guia) for guia in GUIAS]

        # SOUP to compare values part
        soup = BeautifulSoup(tb.get_attribute('innerHTML'), 'html.parser')
        rows = soup.find_all('tr')
        vals_pagos, vals_abertos = [], []
        # pois, alguns são diferentes...
        try:
            for row in rows[1:]:
                def trata_val(v):
                    try:
                        return float(v.replace(',', '.'))
                    except ValueError:
                        print('value error')
                        return v

                _vcobs, _vrecs = [r for r in row.find_all('td')[5:7]]
                vals_pagos.append(trata_val(_vcobs.text))
                vals_abertos.append(trata_val(_vrecs.text))

            # get indexes for GUIAS
            vals_pendentes = []
            for cont, (val_pago, val_em_aberto) in enumerate(zip(vals_pagos, vals_abertos)):
                if val_em_aberto != 0:
                    # print(val_em_aberto)
                    vals_pendentes.append(cont)
            # gera guias a pagar
            _meses_name = []  # for naming certificate of existing guias file
            for indx in vals_pendentes:
                try:
                    guia, mes = GUIAS[indx], MESES[indx].text
                except IndexError:
                    try:
                        guia, mes = GUIAS[indx - 1], MESES[indx - 1].text
                    except IndexError:
                        mes = ""
                _meses_name.append(mes)
                # generate guia
                # guia.click()
            _meses_name = "_".join(_meses_name)
        except ValueError:
            _meses_name = None
        self.driver.save_screenshot(
            f'{self.client_path}/{_meses_name}-GUIASpendentes-giss.png')
        try:
            GUIAS[-1].click()  # the last one
            # download...
            self.webdriverwait_el_by(By.TAG_NAME, 'a').click()
        except IndexError:  # THERE IS NO GUIA
            pass
        print('Downlaod da ultima guia funcional')
        print('~' * 10, f'meses abertos: {_meses_name}')


if __name__ == '__main__':
    GissISSQN(['Oesk Contabil', '19470379000121', '258967'], compt='03-2024', headless=False)
