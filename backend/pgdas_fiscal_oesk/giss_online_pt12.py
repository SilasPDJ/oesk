# dale
from bs4 import BeautifulSoup

from utilities.default import *
from utilities.compt_utils import *
from dotenv import load_dotenv

load_dotenv()

# from . import *
# qualquer coisa me devolve

weblink = 'https://portal.gissonline.com.br/login/index.html'

link = "ChromeDriver/chromedriver.exe"


# self.pyautogui
class GissGui(FileOperations, WDShorcuts):

    def __init__(self, dados, compt, headless=True):
        from functools import partial
        self.__COMPT = compt
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
            first_compt = self.find_first_compt(indx=0)
        else:
            first_compt = self.find_first_compt(indx=1)
        for loop_compt in ate_atual_compt(self.compt_atual, first_compt):
            self.loop_compt = loop_compt
            # TODO: gerenciar por JSON, remover compt

            # driver.get(
            #     'https://www10.gissonline.com.br/interna/default.cfm')

            if is_construcao_civil:
                self.fechar_tomador_para_ambas()
                self.fechar_constr_civil()
                print(f"passando construção civil p/ {__r_social}")
                pass
            else:
                self.fechar_tomador_para_ambas()
                self.fechar_prestador()

        print('GISS encerrado!')

    def _detect_if_is_construcao_civil(self) -> bool:
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(0)

        if self.driver.find_element(By.ID, "7").get_attribute('onclick'):
            self.driver.switch_to.default_content()
            return True
        self.driver.switch_to.default_content()
        return False

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

        # self._inserir_mes_e_competencia()

        self.driver.switch_to.frame(2)
        # Encerrar Prestador
        self.driver.find_element(By.LINK_TEXT, "Encerrar Escrituração").click()

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
        has_alert_then_nomovement = False
        try:
            # Clica OK
            el_ok = self.webdriverwait_el_by(By.CSS_SELECTOR, "font > b")
            el_ok.click()
            print(f"Tomador {self.loop_compt} - já encerrado!")
            return
        except (TimeoutException, NoSuchElementException):
            pass
        except UnexpectedAlertPresentException as e:
            try:
                self.driver.switch_to.alert.accept()
                has_alert_then_nomovement = True
            except Exception as e:
                pass
            self.find_first_compt(indx=1)
            self.fechar_tomador_para_ambas()
        if has_alert_then_nomovement:
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
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(2)
        compt_splitted = self.loop_compt if compt is None else compt

        mes, ano = compt_splitted.split('-')

        mes_input_el = self.driver.find_element(By.NAME, "mes")
        ano_input_el = self.driver.find_element(By.NAME, "ano")
        mes_input_el.clear()
        ano_input_el.clear()

        mes_input_el.send_keys(mes)
        ano_input_el.send_keys(ano)
        self.driver.switch_to.default_content()

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

    def __check_prestador_guias(self):
        def __download_prestador_guias():
            # ---- complementação out/2022
            t_get_years = self.webdriverwait_el_by(By.TAG_NAME, 'table')
            ttr_years = t_get_years.find_elements(By.TAG_NAME, 'tr')[1]
            el_years = ttr_years.find_elements(By.TAG_NAME, 'td')
            for e in el_years:
                # print(e, e.text)
                if e.text == self.__COMPT.split('-')[1]:
                    print("e click", e.text)
                    e.click()
            tb = self.driver.find_elements(By.TAG_NAME, 'table')[1]
            # ---- fim complementação
            # pois a primeira é com anos
            __meses_guias = tb.find_elements(By.TAG_NAME, 'a')
            MESES, GUIAS = (
                [mes for mes in __meses_guias if mes.text != ''],
                [guia for guia in __meses_guias if guia.text == '']
            )
            # TODO: Verificar (do código daqpbaixo) se irá ser downloadado boleto.pdf...
            # [print(mes.text) for mes in meses]
            # [print(guia) for guia in guias]

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
                __meses = []  # for naming certificate of existing guias file
                for indx in vals_pendentes:
                    try:
                        guia, mes = GUIAS[indx], MESES[indx].text
                    except IndexError:
                        try:
                            guia, mes = GUIAS[indx - 1], MESES[indx - 1].text
                        except IndexError:
                            mes = ""
                    __meses.append(mes)
                    # generate guia
                    # guia.click()
                __meses = "_".join(__meses)
            except ValueError:
                __meses = None
            self.driver.save_screenshot(
                f'{self.client_path}/{__meses}-GUIASpendentes-giss.png')
            try:
                GUIAS[-1].click()  # the last one
                # download...
                self.webdriverwait_el_by(By.TAG_NAME, 'a').click()
            except IndexError:  # THERE IS NO GUIA
                pass
            print('Downlaod da ultima guia funcional')
            print('~' * 10, f'meses abertos: {__meses}')

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
            table = self.driver.find_elements(By.TAG_NAME, 'table')[1]
            # -- old
            # iframe = table.find_element(By.XPATH, "//iframe[@name='conteudo']")
            # self.driver.switch_to.frame(iframe)
            # -- ---
            __download_prestador_guias()
            # driver.find_element(By.ID, )
            driver.switch_to.default_content()
        except NoSuchElementException as e:
            print("Erro na geração de boletos do GISS Online!")
            # raise e
        driver.switch_to.default_content()
        iframe = driver.find_element(By.XPATH, "//iframe[@name='header']")
        driver.switch_to.frame(iframe)
        driver.execute_script('javascript: clickPrestador(); ')
        driver.switch_to.default_content()

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


if __name__ == '__main__':
    GissGui(['GABRIEL PINHEIRO SAMPAIO', '40122869000123', '301245'], compt='03-2024', headless=False)
