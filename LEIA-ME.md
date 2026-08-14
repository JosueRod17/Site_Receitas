# Sobrevivência na Cozinha

Projeto web feito com Django e SQLite.

## O que é necessário

- Python 3.12 ou superior
- Git (para clonar o repositório)

## Como executar em uma máquina nova

No terminal, clone o repositório e entre na pasta do projeto:

```powershell
git clone https://github.com/JosueRod17/Site_Receitas
cd sobrevivencia_na_cozinha
```

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação, execute uma vez no terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Instale as dependências e entre na pasta Django:

```powershell
pip install -r dependencias.txt
cd site_de_receitas
```

Prepare o banco de dados e inicie o servidor:

```powershell
python manage.py migrate
python manage.py runserver
```

Depois, acesse `http://127.0.0.1:8000/` no navegador.

## Conta de administrador

Se o banco de dados não vier junto no repositório ou você quiser criar uma conta administrativa nova, execute:

```powershell
python manage.py createsuperuser
```

Em seguida, faça login pela página inicial usando o nome de usuário ou e-mail e a senha cadastrada. O superusuário será enviado para o painel de gestão.

## Antes de enviar ao repositório

O arquivo `.gitignore` já impede que as pastas `.venv`, `.venv1`, `venv` e `env` sejam enviadas. Envie o código, as migrations, os arquivos estáticos e `dependencias.txt`; não envie a virtualenv.
