import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
from PyPDF2 import PdfFileMerger
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

        self.path_stringvar = tk.StringVar()

        # Add padding (margin) between buttons
        bt_mergir_specifics.grid(row=0, column=0, pady=10, padx=10)
        bt_mergir_all.grid(row=0, column=1, pady=10, padx=10)

    def select_pdfs_location_by_dir(self):
        dirpath = filedialog.askdirectory(initialdir=self.initial_dialog_dir, title='diretorio completo')
        if dirpath:
            self.path_stringvar.set(dirpath)
            self._mergir_pdfs()

    def select_pdfs_location_by_selecting_files(self):
        paths = filedialog.askopenfilenames(initialdir=self.initial_dialog_dir, title='arquivos PDF específicos')
        if paths:
            self.path_stringvar.set("\n".join(paths))  # Convert to a string
            print(self.path_stringvar.get())
            self._mergir_pdfs()
    def _mergir_pdfs(self):
        path = self.path_stringvar.get()
        try:
            files = eval(path)
        except (SyntaxError, Exception):
            files = [os.path.join(path, file)
                     for file in os.listdir(path) if file.upper().endswith('')]

        files.sort(reverse=True)

        input(files)
        merger = PdfFileMerger()

        # pdfs = [for pdf in pdfs]
        pdfs = files

        for pdf in pdfs:
            merger.append(pdf)

        merger.write(os.path.join(path, "ArquivosJuntos.pdf"))
        merger.close()


if __name__ == "__main__":
    app = App()
    app.mainloop()
