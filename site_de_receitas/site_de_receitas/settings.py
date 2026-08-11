"""Configurações do projeto Site de Receitas."""

from pathlib import Path

# Caminhos internos do projeto.
DIRETORIO_BASE = Path(__file__).resolve().parent.parent


# Configurações iniciais de desenvolvimento. Revise-as antes da produção.

# Segurança: mantenha a chave secreta de produção protegida.
SECRET_KEY = 'django-insecure-q0we%7xay-i7r0uus&*rle@w$du)dr@q080&#+ecciq1n57905'

# Segurança: não use o modo de depuração em produção.
DEBUG = True

ALLOWED_HOSTS = []


# Aplicativos instalados.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'receitas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'site_de_receitas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'site_de_receitas.wsgi.application'


# Banco de dados.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DIRETORIO_BASE / 'db.sqlite3',
    }
}


# Validação de senhas.

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# As páginas protegidas retornam ao modal de login em vez do endpoint padrão
# inexistente /accounts/login/ do Django.
LOGIN_URL = '/?autenticacao=entrar'


# Internacionalização.

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Arquivos estáticos (CSS, JavaScript e imagens).

STATIC_URL = 'static/'
