from datetime import date, datetime

from .initial_set_files_location import InitialSetFilesLocation
from .pathmanager import Dirs
from .now import Now
import os
import glob


def trata_money_excel(faturado):
    # TODO: refaturar em _backend com foco em já definir os valores e pegar do bd se tem DAS pendentes ou não
    if faturado is None:
        faturado = 0
    faturado = float(faturado)
    faturado = str(faturado).lower().strip()
    if faturado == 'das_pend':
        return 'ATENÇÃO, HÁ BOLETO(S) DO PGDAS PENDENTE(S)'
    if 'nan' in faturado or 'zerou' in faturado or float(faturado) == 0:
        faturado = '0, 00. SEM MOVIMENTO NESTE MÊS.'
        return faturado
    faturado = f'{float(faturado):,.2f}'
    faturado = faturado.replace('.', 'v')
    faturado = faturado.replace(',', '.')
    faturado = faturado.replace('v', ',')
    return faturado


class FileOperations(Dirs, Now):
    files_location = InitialSetFilesLocation()

    def certifs_exist(self, main_path, startswith, at_least=2, endswith: bool = False):
        # if endswith is True, it will search for endswith instead
        arqs_search = self.files_get_anexos_v4(main_path, 'png')
        arqs_search += self.files_get_anexos_v4(main_path, 'pdf')
        # certificados gias são em PDF...
        arqs_search = [
            self.path_leaf(f, True) for f in arqs_search]
        if endswith is False:
            arqs_search = [f for f in arqs_search if f.startswith(startswith)]
        else:
            arqs_search = [f for f in arqs_search if f.endswith(startswith)]

        if len(arqs_search) >= at_least:
            return True
        return False

    @classmethod
    def files_pathit(cls, pasta_client, insyear, ano=None):
        from dateutil import relativedelta as du_rl

        """[summary]

        Args:
            pasta_client (str): client folder name
            insyear (str): inside year (competencia or whatever).
            ano (str,[optional]): year folder. Defaults to None.

        Returns:
            [type]: [description]
        """
        compt = insyear
        if ano is None:
            # ano = ''.join([insyear[e+1:] for e in range(len(insyear)) if insyear[e] not in '0123456789'])
            ill_split = ''.join([v for v in compt if v not in '0123456789'])
            mes, ano = compt.split(ill_split)
            try:
                int(ano)
            except ValueError:
                print(
                    f'if ano is None split ainda não encontrado,\n    ano = ano mês anterior')
                ano = date(cls.y(), cls.m(), 1) - du_rl.relativedelta(months=1)
                # Se ele não achar o ano vindo do split...

        __path = cls.files_location.getset_folderspath()
        path_final = [__path,
                      ano, insyear, pasta_client]
        salva_path = Dirs.pathit(*path_final)
        return salva_path

    @staticmethod
    def certif_feito(save_path, add=''):
        """
        certificado de que está feito
        :param save_path: nome da pasta
        :param add: um adicional no nome do arquivo
        :return: caminho+ nome_arquivo jpeg
        """
        try:
            save = os.path.join(save_path, f"{add}.png")
            print(save, '---------> SAVE')
            return save
        except FileNotFoundError:
            print('NÃO CONSEGUI RETORNAR SAVE')

    @staticmethod
    def convert_img2pdf(filepath_png: str, filepath_newpdf: str, mainpath=None, excluir_png=True):
        from PIL import Image
        # GiaScreenShoot.png
        # f'Recibo_{compt}.pdf'
        if mainpath is not None:
            filepath_png = os.path.join(mainpath, filepath_png)
            filepath_newpdf = os.path.join(mainpath, filepath_newpdf)
        image1 = Image.open(filepath_png)
        try:
            im1 = image1.convert('RGB')
        except ValueError:
            im1 = image1
        im1.save(filepath_newpdf)
        if excluir_png:
            os.remove(filepath_png)

    def files_get_anexos_v4(self, path, file_type='pdf', upload=True):
        """
        :param path: get anexos from the following path
        :param file_type: file annexed type
        :param upload: False -> email it! True: upload it!
        :return: pdf_files or whatever

        # _files_path
        """
        from email.mime.application import MIMEApplication
        pdf_files = list()
        # Lucas Restaurante

        dir_searched_now = path
        list_checked_returned = [os.path.join(dir_searched_now, fname)
                                 for fname in os.listdir(dir_searched_now) if fname.lower().endswith(file_type)]

        for fname in list_checked_returned:
            if not upload:
                file_opened = MIMEApplication(open(fname, 'rb').read())
                fname_title = self.path_leaf(fname)
                file_opened.add_header(
                    'Content-Disposition', 'attachment', filename=fname_title)
                pdf_files.append(file_opened)
            else:
                pdf_files.append(f'{fname}')
        return pdf_files

    @staticmethod
    def sort_files_by_most_recent(folderpath):
        return sorted([os.path.join(folderpath, f)
                       for f in os.listdir(folderpath)],
                      key=lambda x: os.path.getmtime(
                          os.path.join(folderpath, x)),
                      reverse=True)
