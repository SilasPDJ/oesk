import os


class InitialSetFilesLocation:
    __main_path = os.path.dirname(os.path.realpath(__file__))
    __main_path = os.path.join(__main_path, 'with_titlePATH.txt')

    @classmethod
    def getset_folderspath(cls, folder_path_only=True):
        """Seleciona onde estão as pastas e planihas

        Returns:
            [type]: [description]
        """
        # filepath = os.path.realpath(__file__)
        # os.path.dirname(filepath)
        mainpath = False
        try:

            with open(cls.__main_path) as f:
                mainpath = f.read()
        # except FileNotFoundError:
        except (OSError, FileNotFoundError) as e:
            # e('WITH TITLE PATH NOT EXISTENTE ')
            mainpath = cls.__select_path_if_not_exists()

        if mainpath and folder_path_only:
            return mainpath
        else:
            return os.path.join(mainpath, "__EXCEL POR COMPETENCIAS__", "NOVA_FORMA_DE_DADOS.xlsm")

    @staticmethod
    def __select_path_if_not_exists(some_message="SELECIONE ONDE ESTÁ SUA PASTA PRINCIPAL", savit=__main_path):
        """[summary]
        Args:
            some_message (str, optional): []. Defaults to "SELECIONE ONDE ESTÁ SUA PASTA PRINCIPAL".
            savit (str, optional): customizable, where to save the info
        Returns:
            [type]: [description]
        """
        from tkinter import Tk, filedialog, messagebox
        # sh_management = SheetPathManager(file_with_name)
        way = None
        while way is None:
            way = filedialog.askdirectory(title=some_message)
            if len(way) <= 0:
                way = None
                resp = messagebox.askokcancel(
                    'ATENÇÃO!', message='Favor, selecione uma pasta ou clique em CANCELAR.')
                if not resp:
                    return False
            else:
                wf = open(savit, 'w')
                wf.write(way)
                return way
