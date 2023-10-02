import tkinter as tk
import tkinter.messagebox
from CTkListbox import CTkListbox

import customtkinter as ctk
from actions import call_g5, call_gias, call_giss, call_ginfess, call_func_v3
from actions import call_simples_nacional, copy_data_to_clipboard, call_send_pgdas_email, abre_pasta

from repository import MainEmpresasRepository, ClientComptsRepository

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # TODO passar a competencia por variavel atualizavel
        self.client_repository = ClientComptsRepository('08-2023')

        # configure window
        self.title("ctk complex_example.py")
        self.geometry(f"{1100}x{600}")

        self.create_sidebar__routine_calls()
        self.crate_helpy_methods_frame()
        self.display_clientes()

    def _set_button_data(self, function: callable, text: str, text_color=None, fg_color=None, hover_color=None) -> dict:
        button_info = {
            'text': text,
            'function': function,
            'text_color': text_color,
            'fg_color': fg_color,
            'hover_color': hover_color
        }
        return button_info

    def create_sidebar__routine_calls(self):

        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        label_1 = ctk.CTkLabel(main_frame, text="Funções Principais",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        label_1.grid(row=0, column=0, rowspan=1, columnspan=4, pady=10)

        label_2 = ctk.CTkLabel(main_frame, text="Funções Principais",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        label_2.grid(row=0, column=0, rowspan=1, columnspan=4, pady=10)

        frame = ctk.CTkFrame(main_frame, corner_radius=0)
        frame.grid(row=1, column=0, rowspan=4, sticky="nsew")

        button_data_0 = [
            self._set_button_data(call_ginfess, 'Fazer Ginfess'
                                  ),

            self._set_button_data(call_g5, 'Fazer G5',
                                  '#fff', '#F0AA03', '#FFD700'),

            self._set_button_data(call_giss, 'Fazer Giss'
                                  ),

            self._set_button_data(lambda: print("DESATIVADO POR ENQT"), 'Rotina Dívidas - DSTV',
                                  '#fff', 'darkgray', 'gray'),

            self._set_button_data(lambda: call_func_v3('dividasmail'), 'Enviar Dívidas',
                                  '#fff', 'red', '#FF5733')
        ]

        button_data_1 = [
            self._set_button_data(call_simples_nacional, 'PGDAS pdf FULL',
                                  ),

            self._set_button_data(lambda: call_func_v3('jr'), 'Fazer JR',
                                  '#fff', '#556353', '#4CAF50'),

            self._set_button_data(call_send_pgdas_email, 'Enviar PGDAS',
                                  '#fff', 'red', '#FF5733'),
            self._set_button_data(call_gias, 'Fazer GIAS',
                                  ),

        ]

        for row, button_info in enumerate(button_data_0):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = ctk.CTkButton(frame, text=text, command=function,
                                             fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=row, column=0, padx=20, pady=10)

        for row, button_info in enumerate(button_data_1):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = ctk.CTkButton(frame, text=text, command=function,
                                             fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=row, column=1, padx=20, pady=10)

    def crate_helpy_methods_frame(self):
        # TODO: create a main frame for both
        main_frame = ctk.CTkFrame(self, width=180)
        main_frame.grid(row=0, column=2,padx=(20, 10), pady=(5, 0), sticky="nsew")

        scrollable_frame = ctk.CTkScrollableFrame(main_frame, label_text="Selecione as opções", label_font=('sans-serif',16))
        scrollable_frame.grid()

        options = ["ISS", "ICMS", "SEM_MOV", "LP"]

        for i in range(len(options)):
            switch = ctk.CTkSwitch(master=scrollable_frame, text=options[i])
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))

            # set default value
            if options[i] != options[-1]:
                switch.select()

    def display_clientes(self):
        listbox_frame = ctk.CTkFrame(self, width=200)
        listbox_frame.grid(row=0, column=3, padx=(10, 10), pady=(5, 10), sticky="nsew")
        label = ctk.CTkLabel(listbox_frame, text="Selecione clientes",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, rowspan=1, columnspan=2, pady=10)

        df = self.client_repository.get_interface_df()

        listvariable = df['razao_social'].to_list()
        listvariable = tk.StringVar(value=listvariable)

        listbox = CTkListbox(listbox_frame, command=lambda x: print(x), text_color="#000", listvariable=listvariable,
                             width=300, height=275)
        listbox.bind("<Down>", lambda event: self._on_keyup_keydown(listbox, 1))
        listbox.bind("<Up>", lambda event: self._on_keyup_keydown(listbox, -1))
        listbox.grid(row=1, column=0)

    def _on_keyup_keydown(self, widget, direction):
        current_index = widget.curselection()
        next_index = (current_index + direction) % widget.size()
        widget.activate(next_index)


if __name__ == "__main__":
    app = App()
    app.mainloop()
