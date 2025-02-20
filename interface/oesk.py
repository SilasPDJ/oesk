from os import path
import tkinter as tk

from CTkListbox import *
from CTkTable import *

import customtkinter as ctk
from interface.settings import AppSettings
from interface.actions import RoutinesCallings, BindingActions

from backend.repository import OeClientComptsRepository as ClientComptsRepository

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

from backend.utilities.compt_utils import get_compt, ate_atual_compt
from interface.autocomplete_listbox import AutoCompleteListbox


class App(ctk.CTk, AppSettings):
    def __init__(self):
        super().__init__()
        self.compt = get_compt(-1)

        self.compts_repository = ClientComptsRepository(self.compt)
        # Inicializa o DataFrame com dados do repositório para controle
        self.client_compts_df = self.compts_repository.get_interface_df()
        # mantendo a persistencia através de uma cópia inalterável (constante)
        self._clients_compts_df_constant = self.client_compts_df

        self.allowed_clients = 'razao_social'

        self.venc_das = f"20-{get_compt(0)}"
        self.ba = BindingActions(self)
        self.rc = RoutinesCallings(self)

        self.var_selected_compt_field = ctk.StringVar(value='cnpj')

        self.display_clients()
        self.create_funcoes_principais_routine_calls()
        self.display_categoria_clientes('razao_social')
        self.set_key_bindings()

        # configure window
        self.title("oesk")
        self.geometry(f"{1200}x{600}")

        self.searching_entry_is_focused = False

    def set_key_bindings(self):
        self.bind("<F4>", lambda x: self.ba.copy_data_to_clipboard(self.var_selected_compt_field.get()))
        self.bind("<F1>", lambda x: self.ba.f1_abre_pasta('razao_social'))
        self.bind("<F2>", lambda x: self.ba.f2_copy_path('razao_social'))
        self.bind_all("<Control-F5>", lambda x: self.ba.create_new_isntance())
        self.bind_all("<Control-Key-w>", lambda x: self.quit())

    def _set_button_data(self, function: callable, text: str, text_color=None, fg_color=None, hover_color=None) -> dict:
        button_info = {
            'text': text,
            'function': function,
            'text_color': text_color,
            'fg_color': fg_color,
            'hover_color': hover_color
        }
        return button_info

    def create_funcoes_principais_routine_calls(self):
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        label_1 = ctk.CTkLabel(main_frame, text="Funções Principais",
                               font=ctk.CTkFont(size=16, weight="bold"))
        label_1.grid(row=0, column=0, rowspan=1, columnspan=4, pady=10)

        funcoes_frame = ctk.CTkFrame(main_frame, corner_radius=0)
        funcoes_frame.grid(row=1, column=0, rowspan=4, sticky="nsew")

        button_data_0 = [
            self._set_button_data(self.rc.call_ginfess, 'Fazer Ginfess'
                                  ),

            self._set_button_data(self.rc.call_g5, 'Fazer G5',
                                  '#fff', '#F0AA03', '#FFD700'),

            self._set_button_data(self.rc.call_giss, 'Fazer Giss'
                                  ),

            self._set_button_data(self.rc.call_giss_pendentes, 'Fazer Giss Pendentes',
                                  fg_color='#BA8E23'
                                  ),

            self._set_button_data(lambda: print("DESATIVADO POR ENQT"), 'Rotina Dívidas - DSTV',
                                  '#fff', 'darkgray', 'gray'),

            self._set_button_data(lambda: self.rc.call_func_v3('dividasmail'), 'Enviar Dívidas',
                                  '#fff', 'red', '#FF5733')
        ]

        button_data_1 = [
            self._set_button_data(self.rc.call_pgdas_declaracao, 'PGDAS pdf FULL',
                                  ),

            self._set_button_data(self.rc.call_jr, 'Fazer JR',
                                  '#fff', '#556353', '#4CAF50'),

            self._set_button_data(self.rc.call_send_pgdas_email, 'Enviar PGDAS',
                                  '#fff', 'red', '#FF5733'),
            self._set_button_data(self.rc.call_gias, 'Fazer GIAS',
                                  ),
            self._set_button_data(self.rc.run_oesk_project_excel, 'Run REACT Website',
                                  ),

        ]

        for row, button_info in enumerate(button_data_0):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = ctk.CTkButton(funcoes_frame, text=text, command=function,
                                   fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=row, column=0, padx=20, pady=10)

        for row, button_info in enumerate(button_data_1):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = ctk.CTkButton(funcoes_frame, text=text, command=function,
                                   fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=row, column=1, padx=20, pady=10)

        # Selecionar Vencimento do DAS
        label_venc_das = ctk.CTkLabel(main_frame, text="Selecione a data de vencimento do DAS",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        label_venc_das.grid()
        compt_frame = ctk.CTkFrame(main_frame)
        compt_frame.grid()
        venc_das = ctk.CTkEntry(compt_frame, textvariable=self.venc_das)
        venc_das.grid()

        ctk.CTkButton(compt_frame, text="Atualizar")

        self._create_dicas(main_frame)

    def _create_dicas(self, main_frame: ctk.CTkFrame):
        # Dicas...
        tips_frame = ctk.CTkFrame(main_frame)
        tips_frame.grid(pady=(10, 20))

        tips = [
            # f'Vencimento DAS: {VENC_DAS}',
            ['Atalhos', 'Comandos'],
            ['Ctrl + F5', 'Cria Nova Instância'],
            ['F1', 'Abrir Pasta Cliente'],
            ['F2', 'Copia Pasta Cliente'],
            ['F4', 'Copia Campo Cliente'],
            ['F12', 'GShopee Emission_Reports'],
        ]
        CTkTable(tips_frame,
                 values=tips,
                 header_color="#989798").grid()

    def display_categoria_clientes(self, df_col):
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=2, padx=(10, 10), pady=(5, 10), sticky="nsew")

        options = ["ISS", "ICMS", "SEM_MOV", "LP"]

        scrollable_frame = ctk.CTkScrollableFrame(main_frame, label_text="Categoria cliente",
                                                  label_font=ctk.CTkFont(size=16, weight="bold"))
        scrollable_frame.grid(sticky="nsew", pady=10)

        def _update_allow_list():
            """
            Atualiza a lista permitida com base nas opções selecionadas.
            Função para atualizar a lista com base nos switches
            """
            selected_options = [v.cget("text") for v in switches if v.get()]
            self.client_compts_df = self.compts_repository.get_interface_df(allowing_impostos_list=selected_options)
            self.allowed_clients.set(self.client_compts_df[df_col].to_list())

        only_one_selection = tk.BooleanVar(value=True)
        switches = []

        def change_switch_options_selection(current_switch):
            """
            Verifica e desmarca os outros switches se a opção "Selecionar somente um" estiver marcada.
            Selecione somente um switch se a opção "Selecionar somente um" estiver marcada
            """
            if only_one_selection.get():
                for s in switches:
                    if s != current_switch:
                        s.deselect()
            _update_allow_list()

        for i, option in enumerate(options):
            switch = ctk.CTkSwitch(master=scrollable_frame, text=option)
            switch.configure(command=lambda s=switch: change_switch_options_selection(s))
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            switches.append(switch)

        alow_one_only = ctk.CTkCheckBox(scrollable_frame, text="Permitir somente um por vez",
                                        variable=only_one_selection)
        alow_one_only.grid()

        fields_radio_frame = ctk.CTkScrollableFrame(main_frame, label_text="Selecione o campo",
                                                    label_font=ctk.CTkFont(size=16, weight="bold"), width=250)
        fields_radio_frame.grid(sticky="nsew", pady=10)

        for i, text in enumerate(self.copiable_fields):
            row = i
            column = 0
            field_radio = ctk.CTkRadioButton(fields_radio_frame, variable=self.var_selected_compt_field, value=text,
                                             text=text)
            field_radio.grid(row=row, column=column, sticky="w")

    def _on_keyup_keydown(self, widget, direction):
        try:
            current_index = eval(widget.listvariable.get()).index(widget.get())
        except ValueError:
            current_index = widget.curselection()
        if isinstance(current_index, int):
            next_index = current_index + direction
            if 0 <= next_index <= widget.size():
                try:
                    widget.activate(next_index)
                except IndexError:
                    widget.activate(0)
        else:
            widget.activate(0)
            # raise IndexError("erro, current_index não é int`")

    def display_clients(self):
        main_frame = ctk.CTkFrame(self, width=180)
        main_frame.grid(row=0, column=3, columnspan=2, sticky="nsew")
        # Rótulo para seleção do cliente
        label = ctk.CTkLabel(main_frame, text="Selecione o cliente",
                             font=ctk.CTkFont(size=16, weight="bold"))
        label.grid()
        # Mostra os clientes permitidos
        current_client_selection = CTkListbox(main_frame,
                                              text_color="#000",
                                              listvariable=self.allowed_clients,
                                              width=470, height=450, fg_color="#fbfbfb")

        current_client_selection.configure(
            command=lambda x: setattr(self, 'current_client_index', current_client_selection.curselection()))
        current_client_selection.grid()

        select_client_listbox = AutoCompleteListbox(main_frame,
                                                    current_client_selection,
                                                    self.client_compts_df[self.main_df_col].to_list(),
                                                    self._update_df_before_filtering_listbox)

        current_client_selection.bind("<KeyRelease-Up>",
                                      lambda x: self._on_keyup_keydown(current_client_selection, -1))
        current_client_selection.bind("<KeyRelease-Down>",
                                      lambda x: self._on_keyup_keydown(current_client_selection, 1))
        # current_client_selection.bind("<Down>", lambda event: self._on_keyup_keydown(current_client_selection, 1))
        # current_client_selection.bind("<Up>", lambda event: self._on_keyup_keydown(current_client_selection, -1))

    def _update_df_before_filtering_listbox(self, event: tk.Event):
        entry = event.widget

        filter_text = entry.get().lower()
        if filter_text.strip() == "":
            return
        # Pois o `self.clients_compts_df` é variável por razões lógicas de funcionalidades da listbox
        df = self._clients_compts_df_constant.copy()
        filtered_df = df[df[self.main_df_col].apply(
            lambda x: any(word in x.lower() for word in filter_text.split())
        )]
        # update allow list
        self.client_compts_df = filtered_df
        self.allowed_clients.set(self.client_compts_df[self.main_df_col].to_list())


if __name__ == "__main__":
    app = App()
    app.mainloop()
