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
class GissGui(GissUtils):

    def __init__(self, dados, compt, headless=True, pswd=None):
        from functools import partial
        self.__COMPT = compt
        # [print(s) for s in __senhas]
        __r_social, _giss_cnpj, self._logar = dados[:3]
        self._pswd = pswd
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
            first_compt = self.find_first_compt(indx=0)
        else:
            first_compt = self.find_first_compt(indx=1)
        for loop_compt in ate_atual_compt(self.compt_atual, first_compt):
            self.loop_compt = loop_compt
            # TODO: gerenciar por JSON, remover compt

            # driver.get(
            #     'https://www10.gissonline.com.br/interna/default.cfm')

            if is_construcao_civil:
                self.fechar_constr_civil()
                print(f"passando construção civil p/ {__r_social}")
            else:
                self.fechar_prestador()

        first_compt = self.find_first_compt(indx=1)
        for loop_compt in ate_atual_compt(self.compt_atual, first_compt):
            self.loop_compt = loop_compt
            self.fechar_tomador_para_ambas()

        print('GISS encerrado!')

    def fechar_constr_civil(self):
        def _get_func_compt(_func_compt=None) -> str:
            if _func_compt is None:
                return self.loop_compt
            if isinstance(_func_compt, date):
                return date_to_compt(_func_compt)

        def _ativa_constr_civil():
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(0)
            self.driver.find_element(By.ID, "7").click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(2)
            self.driver.find_element(
                By.CSS_SELECTOR, "table:nth-child(2) tr:nth-child(1) font").click()
            self.driver.switch_to.default_content()

        def encerrar_part_1(func_compt=None):
            _ativa_constr_civil()
            func_compt = _get_func_compt(func_compt)
            if func_compt > self.compt_atual:
                return
            self.driver.switch_to.default_content()
            self._inserir_mes_e_competencia(func_compt)

            self.driver.switch_to.frame(2)
            self.driver.find_element(
                By.LINK_TEXT, "Encerrar Competência").click()
            try:
                self.webdriverwait_el_by(
                    By.CSS_SELECTOR, "td:nth-child(3) span").click()
            except (TimeoutException, NoSuchElementException):
                # precisa encerrar a competencia anterior...
                encerrar_part_1(compt_to_date_obj(
                    func_compt) - relativedelta(months=1))

            except UnexpectedAlertPresentException as e:
                if 'Competência encerrada' in e.alert_text:
                    print(
                        f"Constr Civil pt1 {self.loop_compt} - já encerrado!")
                    try:
                        self.driver.switch_to.alert.accept()
                    except Exception as e:
                        pass
                    finally:
                        encerrar_part_1(compt_to_date_obj(
                            func_compt) + relativedelta(months=1))
            try:
                self.driver.switch_to.alert.accept()
            except Exception as e:
                pass

        # self.driver.find_element(By.CSS_SELECTOR, ".impressora:nth-child(1) > .bold").click()

        def encerrar_part_2(func_compt=None):
            _ativa_constr_civil()
            func_compt = _get_func_compt(func_compt)
            if func_compt > self.compt_atual:
                return
            self.driver.switch_to.default_content()
            self._inserir_mes_e_competencia(func_compt)

            self.driver.switch_to.frame(0)
            self.driver.find_element(By.ID, "7").click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(2)
            self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(2) > td > span > font").click()
            self.driver.find_element(
                By.LINK_TEXT, "Encerrar Escrituração").click()
            try:
                self.webdriverwait_el_by(
                    By.CSS_SELECTOR, ".txt_al_center:nth-child(12) > .txt_up").click()
                self.driver.find_element(By.CSS_SELECTOR, ".txt_up").click()
            except (TimeoutException, NoSuchElementException):
                encerrar_part_2(compt_to_date_obj(
                    func_compt) + relativedelta(months=1))
            except UnexpectedAlertPresentException as e:
                try:
                    self.driver.switch_to.alert.accept()
                except NoAlertPresentException:
                    pass
                finally:
                    encerrar_part_2(compt_to_date_obj(
                        func_compt) - relativedelta(months=1))

        def encerrar_part_3(func_compt=None):
            _ativa_constr_civil()
            func_compt = _get_func_compt(func_compt)
            if func_compt > self.compt_atual:
                return
            self.driver.switch_to.default_content()
            self._inserir_mes_e_competencia(func_compt)

            self.driver.switch_to.frame(0)
            self.driver.find_element(By.ID, "7").click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(2)
            self.driver.find_element(
                By.CSS_SELECTOR, "table:nth-child(4) span > font").click()
            self.driver.find_element(
                By.LINK_TEXT, "Encerrar Sem Movimento").click()
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, ".txt_al_center:nth-child(12) > .txt_up").click()
            except Exception as e:
                print("Parte 3 exception - falta completar da onde prosseguir")
                pass

        encerrar_part_1()
        encerrar_part_2()
        encerrar_part_3()
        # TODO: descobrir por que ta dando loop infinitido em constr civil

    def fechar_prestador(self):
        self.driver.switch_to.default_content()

        self.driver.switch_to.frame(0)
        self.driver.find_element(By.ID, "5").click()
        self.driver.switch_to.default_content()

        self._inserir_mes_e_competencia()

        self.driver.switch_to.frame(2)
        # Encerrar Prestador
        self.webdriverwait_el_by(By.LINK_TEXT, "Encerrar Escrituração").click()

        try:
            self.tag_with_text('a', 'Menu Principal', 7).click()
            print(f'Prestador {self.loop_compt} já encerrado!')
        except (TimeoutException, NoSuchElementException):
            self.driver.find_element(
                By.CSS_SELECTOR, ".txt_al_center:nth-child(12) > .txt_up").click()
            self.driver.find_element(By.CSS_SELECTOR, ".txt_up").click()
        finally:
            self.driver.switch_to.default_content()

    def fechar_tomador_para_ambas(self):
        self.driver.switch_to.default_content()
        # Encerrar Tomador
        self.driver.switch_to.frame(0)
        self.driver.find_element(By.ID, "6").click()
        self.driver.switch_to.default_content()

        self._inserir_mes_e_competencia()

        self.driver.switch_to.frame(2)

        self.driver.find_element(By.LINK_TEXT, "Encerrar Escrituração").click()
        nomovement = False
        try:
            # Clica OK
            el_ok = self.webdriverwait_el_by(By.CSS_SELECTOR, "font > b")
            el_ok.click()
            print(f"Tomador {self.loop_compt} - já encerrado!")
            return
        except (TimeoutException, NoSuchElementException):
            nomovement = True
        except UnexpectedAlertPresentException as e:
            try:
                if 'após encerrar o mês anterior' in e.alert_text.lower():
                    self.driver.switch_to.alert.accept()
                else:
                    print(f'\032[1;32m {e.alert_text} \033[m')
                    input(f"{nomovement} input, stopped: ")
            except Exception as e:
                pass
            # self.fechar_tomador_para_ambas()
            return
        if nomovement:
            self.webdriverwait_el_by(By.LINK_TEXT, "Menu Principal").click()
            self.driver.find_element(
                By.LINK_TEXT, "Encerrar Sem Movimento").click()
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, ".txt_al_center:nth-child(12) > .txt_up").click()
            self.driver.find_element(By.CSS_SELECTOR, ".txt_up").click()
        finally:
            self.driver.find_element(By.CSS_SELECTOR, "html").click()

    def find_first_compt(self, indx=0) -> str:
        _first_compt = compt_to_date_obj(
            self.__COMPT) - relativedelta(months=1)

        # 5: prestador, 6: tomador
        options_encerrar = (("5", "Encerrar Escrituração"),
                            ("6", "Encerrar Sem Movimento"))

        if indx >= len(options_encerrar):
            indx = 0
        bt_opt, escrituracao_link_text = options_encerrar[indx]

        while True:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(0)
            # self.driver.find_element(By.ID, "5").click()
            self.driver.find_element(By.ID, bt_opt).click()
            self.driver.switch_to.default_content()

            self._inserir_mes_e_competencia(date_to_compt(_first_compt))

            self.driver.switch_to.frame(2)
            # Encerrar Prestador
            try:
                self.driver.find_element(
                    By.LINK_TEXT, escrituracao_link_text).click()
                self.driver.find_element(
                    By.CSS_SELECTOR, ".txt_al_center:nth-child(12) > .txt_up").click()
                return date_to_compt(_first_compt)
            except NoSuchElementException as e:
                # Já foi declarada!
                return date_to_compt(_first_compt)

            except UnexpectedAlertPresentException:
                # procurando qual declarar!
                _first_compt -= relativedelta(months=1)

    def _inserir_mes_e_competencia(self, compt=None):
        super()._inserir_mes_e_competencia(self.loop_compt if compt is None else compt)


if __name__ == '__main__':
    # gissonline.json (mensal, pendentes)

    GissGui(['empresa', '13510432000194', '352254'], compt='07-2024', headless=False)
