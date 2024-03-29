import os
import json
import glob
from json import decoder
from shutil import move


class Dirs:
    @staticmethod
    def mkdir_pathit(*directories, sep="\\"):
        """ make dirs with directories args, example: pathit('path', 'to', 'dir')
            that will return and create "path/to/dir"
        :param directories: "without "/" please
        :param sep: the separator

        Returns:
            str: path/to/dir
        """
        import os
        pathit = directories[0]

        for directory in directories[1:]:
            pathit += f'\\{directory}'
        if not os.path.exists(pathit):
            os.makedirs(pathit)
        pathit = pathit.replace('/', sep)
        return pathit

    @staticmethod
    def walget_searpath(searched, initial_path, whatis: int = 0):
        """
        # walk get searched path
        :param str searched: any string
        :param initial_path: any path...
        :param whatis: 0 = dirpath (defult); 1 = searches in dirnames; 2 = searches in filenames
        from os.walk  
        :return: first found though searched in path
        """
        if whatis > 2 or whatis < 0:
            raise ValueError("Try values between 2 and 0")
        for (dirpath, dirnames, filenames) in os.walk(initial_path):
            if whatis == 0:
                if searched in dirpath:
                    return dirpath
            elif whatis == 1:
                listof = []
                for path_level_1 in dirnames:
                    for file in os.listdir(os.path.join(dirpath, path_level_1)):
                        if file.find(searched) > -1:
                            listof.append(os.path.join(
                                dirpath, path_level_1, file))
                return listof

            elif whatis == 2:
                try:
                    listof = []
                    for filename in filenames:
                        if searched in filename:
                            listof.append(os.path.join(dirpath, filename))
                    return listof
                except IndexError:
                    return False

    @staticmethod
    def path_leaf(path, only_file=False):
        """
        :param path: Any path
        :param only_file: returns only file name
        :return: opposite of os.path.dirname, so returns the file path
        ps: returns False if path has no file
        """
        if not os.path.isfile(path):
            return False
        head, tail = os.path.split(path)
        if only_file:
            return tail

        # else
        return tail or os.path.basename(head)

    @staticmethod
    def get_documents_folder_location():
        """
        :returns: user Documents folder location
        """
        from platform import system
        import win32com
        import pythoncom
        if system() == 'Windows':
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            my_documents = shell.SpecialFolders("MyDocuments")
            # print(my_documents)
        else:
            my_documents = os.path.expanduser("~/Documents")
        return my_documents

    def unzip_folder(self, full_path, rm_zip=True):
        """
        :param full_path: caminho
        :param rm_zip: True -> remove zip, False, não remove
        :return: arquivo extraído e excluído o zip.
        Ele faz isso com todos os zip
        """
        from time import sleep
        from os import chdir, remove, listdir
        from zipfile import ZipFile, BadZipFile
        chdir(full_path)
        ls = listdir()
        for file in ls:
            print('Descompactando, ZIPs e excluíndo-os')
            if file.endswith('.zip'):
                try:
                    zf = ZipFile(file, mode='r')
                    zf.extractall()
                    zf.close()
                except BadZipFile:
                    print('Não deszipei')
                finally:
                    if rm_zip:
                        sleep(5)
                        remove(file)

    @staticmethod
    def get_most_recent_files_in_dir(num_files, path=os.path.expanduser('~' + os.sep + 'Downloads')):
        # Get a list of all files in the specified directory
        list_of_files = glob.glob(path + '/*')

        # Sort the list of files by their creation time in descending order (most recent first)
        list_of_files.sort(key=os.path.getctime, reverse=True)

        # Get the top 'num_files' files
        most_recent_files = list_of_files[:num_files]

        return most_recent_files

    @staticmethod
    def move_file(where_from, destiny):
        """[File/folder moved from a place[where_from] to another[destiny]]
        Args:
            where_from (str):
            destiny (str):
        """
        move(where_from, destiny)

class HasJson:
    @staticmethod
    def load_json(file):
        """
        :param str file: file name
        :return: dict or list or tuple from json loaded
        """
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except (decoder.JSONDecodeError, FileNotFoundError) as e:
            # raise e
            return False

    @staticmethod
    def dump_json(objeto, file):
        """
        :param object objeto:
        :param file:
        # :param ensure_ascii: False -> utf-8, True -> ensure-it
        :return:

        # object engloba list, tuple, dict
        """
        with open(file, 'w', encoding='utf-8') as file:
            json.dump(objeto, file, ensure_ascii=False, indent=8)


if __name__ == "__main__":
    test = Dirs.walget_searpath(
        'emission_report', r'O:\OneDrive\_FISCAL-2021\2023\07-2023', 1)
    print(test)

    most_recent_Files = Dirs.get_most_recent_files_in_dir(num_files=4)
    print(most_recent_Files)
