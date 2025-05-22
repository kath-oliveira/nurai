# Automação Financeira para CFO as a Service

Este projeto é uma aplicação web Flask desenvolvida para automatizar tarefas de diagnóstico financeiro e cálculo de valuation para Pequenas e Médias Empresas (PMEs), auxiliando consultores que atuam como CFO as a Service.

## Funcionalidades Principais

*   **Autenticação de Usuários:** Cadastro, login, recuperação de senha e exclusão de conta seguros.
*   **Gerenciamento de Empresas:** Adição e visualização de múltiplas empresas clientes.
*   **Questionário Financeiro:** Coleta de informações detalhadas sobre a situação financeira da empresa através de um questionário estruturado.
*   **Upload de Documentos:** Permite o envio de documentos financeiros (extratos, DRE, balanços, etc.) para análise (processamento detalhado na Fase 2).
*   **Diagnóstico Financeiro:** Geração de um diagnóstico preliminar baseado nas respostas do questionário, com indicadores chave e recomendações (análise aprofundada na Fase 2).
*   **Cálculo de Valuation:** Estimativa preliminar do valor da empresa baseada nas respostas do questionário (cálculos detalhados na Fase 2).
*   **Interface Responsiva:** Design adaptável para desktops, tablets e smartphones com barra lateral colapsável.

## Tecnologias Utilizadas

*   **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Mail, Werkzeug (segurança), Gunicorn
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap 5, Chart.js
*   **Banco de Dados:** PostgreSQL (recomendado para produção no Heroku), SQLite (para desenvolvimento local)
*   **Segurança:** Hash de senhas (bcrypt), tokens CSRF, tokens JWT para reset de senha, headers de segurança.

## Configuração e Execução Local

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd automacao_financeira_github
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (ajuste conforme necessário):
    ```
    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=\'sua_chave_secreta_super_segura\'
    # Configurações do Banco de Dados (Exemplo SQLite)
    DATABASE_URL=sqlite:///instance/local_database.db
    # Configurações de Email (para reset de senha - use Mailtrap, SendGrid, etc.)
    MAIL_SERVER=smtp.mailtrap.io
    MAIL_PORT=2525
    MAIL_USERNAME=seu_usuario_mailtrap
    MAIL_PASSWORD=sua_senha_mailtrap
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_DEFAULT_SENDER=(\'CFO Service\', \'noreply@example.com\')
    ```
    *Nota: Para produção no Heroku, estas variáveis serão configuradas diretamente no painel do Heroku.*

5.  **Crie o banco de dados inicial:**
    ```bash
    flask db init  # Se for a primeira vez e usando Flask-Migrate (não incluído neste pacote básico)
    flask db migrate -m "Initial migration." # Se usando Flask-Migrate
    flask db upgrade # Se usando Flask-Migrate
    # Ou, para a configuração básica sem Flask-Migrate:
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
    ```
    *Certifique-se de que a pasta `instance` existe se estiver usando SQLite.*

6.  **Execute a aplicação:**
    ```bash
    flask run
    ```
    A aplicação estará disponível em `http://127.0.0.1:5000`.

## Implantação no Heroku

Siga as instruções detalhadas no arquivo `HEROKU_DEPLOYMENT.md` (incluído neste pacote) para implantar a aplicação no Heroku.

## Próximos Passos (Fase 2)

*   Implementação completa do processamento de documentos financeiros (extração de dados de PDFs, etc.).
*   Desenvolvimento de algoritmos detalhados para diagnóstico financeiro e cálculo de valuation.
*   Integração com APIs externas (se necessário).
*   Melhorias na interface e experiência do usuário.

