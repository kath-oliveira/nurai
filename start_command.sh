"""
Arquivo de configuração para deploy no Render.com
Contém instruções para start do aplicativo
"""

# start_command.sh
# Este arquivo contém o comando de start para o Render.com
# Inicia o aplicativo usando gunicorn

gunicorn app:app
