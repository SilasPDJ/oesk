import tkinter as tk
import tkinter.messagebox
import customtkinter
from actions import call_g5, call_gias, call_giss, call_ginfess, call_func_v3
from actions import call_simples_nacional, copy_data_to_clipboard, call_send_pgdas_email, abre_pasta

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{1100}x{600}")

        self.create_sidebar__routine_calls()
        self.crate_helpy_methods_frame()

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

        main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        label = customtkinter.CTkLabel(main_frame, text="Funções Principais",
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=1, rowspan=1, columnspan=4, pady=10)

        cols = 2
        frames = []
        for col in range(1, cols):
            frame = customtkinter.CTkFrame(main_frame, corner_radius=0)
            frame.grid(row=1, column=col, rowspan=4, sticky="nsew")
            frames.append(frame)

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

        for col, button_info in enumerate(button_data_0):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = customtkinter.CTkButton(frames[0], text=text, command=function,
                                             fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=col, column=0, padx=20, pady=10)

        for col, button_info in enumerate(button_data_1):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']

            button = customtkinter.CTkButton(frames[0], text=text, command=function,
                                             fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=col, column=1, padx=20, pady=10)

    def crate_helpy_methods_frame(self):
        scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Selecione as opções", label_font=('sans-serif',16))
        scrollable_frame.grid(row=0, column=2, padx=(10, 10), pady=(5, 10), sticky="nsew")

        options = ["ISS", "ICMS", "SEM_MOV", "LP"]

        for i in range(len(options)):
            switch = customtkinter.CTkSwitch(master=scrollable_frame, text=options[i])
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))

            # set default value
            if options[i] != options[-1]:
                switch.select()


        # funcoes pt1
        frame = customtkinter.CTkFrame(self, width=180, corner_radius=0)
        frame.grid(row=0, column=3, rowspan=4, sticky="nsew")
        button_data = [
            self._set_button_data(abre_pasta, 'Abre/copia pasta [F1]'
                                  ),
            self._set_button_data(copy_data_to_clipboard, 'Copia Campo [F4]',
                                  ),
        ]
        for i, button_info in enumerate(button_data):
            text = button_info['text']
            function = button_info['function']
            text_color = button_info['text_color']
            fg_color = button_info['fg_color']
            hover_color = button_info['hover_color']
            button = customtkinter.CTkButton(frame, text=text, command=function,
                                             fg_color=fg_color, text_color=text_color, hover_color=hover_color)

            button.grid(row=i, column=0, padx=20, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
