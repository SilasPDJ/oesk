import tkinter as tk
from tkinter import filedialog
from typing import Union

import customtkinter as ctk
from PyPDF2 import PdfMerger
import os
from tkinter.filedialog import askdirectory, askopenfilenames


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.initial_dialog_dir = r"O:\OneDrive\Musicas encore Silas\netinho\NATAL2023\PAI"
        self.title("oesk")
        # self.geometry(f"{1200}x{600}")

        self.frame = ctk.CTkFrame(self, corner_radius=0, )
        self.frame.grid(row=0, column=0, sticky="nsew")

        bt_mergir_all = ctk.CTkButton(self.frame, text="Mergir todos PDFs no diretório",
                                      command=self.select_pdfs_location_by_dir,
                                      fg_color="darkblue")
        bt_mergir_specifics = ctk.CTkButton(self.frame, text="Mergir PDFs específicos",
                                            command=self.select_pdfs_location_by_selecting_files,
                                            fg_color="brown")
        self.arquivo_final_nome = tk.StringVar(value='arquivosJuntosPdf')

        arquivo_final_label = ctk.CTkLabel(self, text="Nome do arquivo que irá unir os PDFs: ")

        arquivo_final_entry = ctk.CTkEntry(self, textvariable=self.arquivo_final_nome)

        # Add padding (margin) between buttons
        bt_mergir_specifics.grid(row=0, column=0, pady=10, padx=10)
        bt_mergir_all.grid(row=0, column=1, pady=10, padx=10)
        # Center the label and entry widget vertically and horizontally
        arquivo_final_label.grid(row=1, column=0, sticky="nsew")
        arquivo_final_entry.grid(row=2, column=0, sticky="nsew")

    def select_pdfs_location_by_dir(self):
        dirpath = filedialog.askdirectory(initialdir=self.initial_dialog_dir, title='diretorio completo')
        if dirpath:
            self._mergir_pdfs(dirpath)

    def select_pdfs_location_by_selecting_files(self):
        paths = filedialog.askopenfilenames(initialdir=self.initial_dialog_dir, title='arquivos PDF específicos')
        if paths:
            self._mergir_pdfs(paths)

    def _mergir_pdfs(self, path: Union[os.PathLike, tuple]):
        if isinstance(path, tuple):
            # é uma tupla com o caminho completo ja
            files = [p for p in path]
            path = os.path.dirname(files[0])

        else:
            files = [(os.path.join(path, file)).replace('/', '\\')
                     for file in os.listdir(path) if file.upper().endswith('PDF')]

        files.sort(reverse=True)

        merger = PdfMerger()

        # pdfs = [for pdf in pdfs]
        pdfs = files

        for pdf in pdfs:
            merger.append(pdf)

        merger.write(os.path.join(path, self.arquivo_final_nome.get() + '.pdf'))
        merger.close()


if __name__ == "__main__":
    app = App()
    app.mainloop()
