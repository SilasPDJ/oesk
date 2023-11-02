import tkinter as tk
from typing import Union

import customtkinter as ctk
from CTkListbox import *


class AutoCompleteListbox:
    def __init__(self, frame: tk.Frame, listbox_client_selection: Union[tk.Listbox, CTkListbox], allowed_clients:list,
                 grid_elements=True):
        self.listbox_client_selection = listbox_client_selection
        self.allowed_clients = allowed_clients
        self.original_items = self.allowed_clients  # cópia dos elementos originais

        for item in self.allowed_clients:
            self.listbox_client_selection.insert(tk.END, item)

        self.entry = ctk.CTkEntry(frame)
        self.entry.bind("<KeyRelease>", self.filter_listbox)
        if grid_elements:
            self.entry.grid()

    def filter_listbox(self, event):
        filter_text = self.entry.get().lower()
        try:
            self.listbox_client_selection.delete(0, tk.END)  # Limpar a lista
        except IndexError:
            pass
        else:
            if not filter_text:  # Se o filtro estiver vazio, restaure a lista original
                for item in self.original_items:
                    self.listbox_client_selection.insert(tk.END, item)
            else:
                for looping_item in self.original_items:
                    _item = looping_item.lower()
                    if any(word in _item for word in filter_text.split()):
                        self.listbox_client_selection.insert(tk.END, looping_item)
        # self.listbox_client_selection.activate(0)
