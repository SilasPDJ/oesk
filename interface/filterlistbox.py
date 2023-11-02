import tkinter as tk


def filter_listbox(event):
    filter_text = entry.get().lower()

    current_client_selection.delete(0, tk.END)  # Limpar a lista

    for item in allowed_clients:
        item = item.lower()
        if filter_text in item:
            current_client_selection.insert(tk.END, item)
        elif all(char in item for char in set(filter_text)):
            current_client_selection.insert(tk.END, item)
        # elif filter_text in item:
        #     current_client_selection.insert(tk.END, item)
        elif filter_text in item or filter_text in item:
            current_client_selection.insert(tk.END, item)




# Crie a janela principal
root = tk.Tk()
root.title("Filtrar Listbox")

# Crie a caixa de entrada para o filtro
entry = tk.Entry(root, width=50)
entry.pack()

# Crie a Listbox
current_client_selection = tk.Listbox(root, width=40, height=10)
current_client_selection.pack()

# Preencha a Listbox com alguns itens de exemplo
allowed_clients = ["Apple", "Banana", "Cherry", "Grapes", "Orange"]
for item in allowed_clients:
    current_client_selection.insert(tk.END, item)

# Associe a função de filtro à caixa de entrada
entry.bind("<KeyRelease>", filter_listbox)

# Inicie a interface gráfica
root.mainloop()
