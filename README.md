# oesk_project_excel

**Descrição:** _projeto utilizado para rotinas mensais de empresas clientes_

-   [x] Interface GUI contemplando diversas funcionalidades
-   [x] "default" package com as seguintes funcionalidade que podem ser reutilizadas por outros sistemas

## "default" package

-   ### sets
    -   Criação automática de diretórios (pathmanager.py)
    -   Envio automático de emails (init_email.py)
-   ### webdriver_utilities
    -   selenium webdriver shortcuts (wbs.py)
    -   selenium webdriver chrome tipos de drivers diferentes "pré-configurados"
-   ### interact
    -   função press_key_b4: pausa o script até que o programa seja executado novamente

## "utilities" package

-   ### compt_utiles
    - compt = competencia

-   ### db
    - `DbAccessManager` gerencia o acesso à base de dados sql

## "repository" package

-   Gerencia operações no banco dados, com métodos reutilizáveis por todo o projeto

## "models" package

- Utilizando sqlalchemy orm