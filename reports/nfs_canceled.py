import os

path = "O:\\OneDrive\\_FISCAL-2021\\2024\\03-2024"
for root, dirs, files in os.walk(path):
    for directory in dirs:
        # Concatenar o caminho do diretório raiz com o diretório atual
        dir_path = os.path.join(root, directory)

        # Caminho para o arquivo NF_canceladas.txt dentro do subdiretório
        file_path = os.path.join(dir_path, 'NF_canceladas.txt')

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                conteudo = file.read()

                if conteudo.strip() != '':
                    print(f'Conteúdo do arquivo {file_path}:')
                    print(conteudo, '\n', directory)
                    print()
                    print()
