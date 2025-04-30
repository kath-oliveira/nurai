"""
Configuração do aplicativo Flask para implantação no Render.com (Modo Demo).
Este módulo contém as configurações necessárias para executar o aplicativo
de automação financeira no ambiente de produção do Render.com.
"""

import os
import logging
import json
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import inspect # Import inspect

# Importar módulos de segurança
from security_measures import SecurityManager, configure_heroku_security, csrf_protected

# Configuração do aplicativo
app = Flask(__name__)

# Configurar o aplicativo para funcionar atrás de proxies (Render usa proxies)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Configurações do banco de dados PostgreSQL (Render) - Mantido para estrutura
database_url = os.environ.get("DATABASE_URL", "")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///local_dev.db" # Fallback para SQLite localmente
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "uma-chave-secreta-muito-forte-padrao") # Chave secreta

# Configurações de upload de arquivos
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "png", "jpg", "jpeg", "xls", "xlsx", "csv", "txt"}

# Garantir que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Inicializar banco de dados (ainda necessário para modelos e outras rotas)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Inicializar gerenciador de segurança
security_manager = SecurityManager(app)
app.security_manager = security_manager  # Tornar acessível globalmente

# Aplicar configurações de segurança (pode precisar de ajustes para Render)
# configure_heroku_security(app) # Comentado - revisar se necessário para Render

# Configurar logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Aplicativo CFO as a Service iniciado (Modo Demo Login)")

# Modelos de banco de dados (mantidos para estrutura)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    companies = db.relationship("Company", backref="user", lazy=True, cascade="all, delete-orphan")

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), nullable=True)
    segment = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    documents = db.relationship("Document", backref="company", lazy=True, cascade="all, delete-orphan")
    questionnaires = db.relationship("Questionnaire", backref="company", lazy=True, cascade="all, delete-orphan")

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    extracted_data = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pendente")
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Questionnaire(db.Model):
    __tablename__ = "questionnaires"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    responses = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

# Funções auxiliares
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Importar módulos de processamento
try:
    from questionnaire_storage import QuestionnaireTemplate
    from document_processor import DocumentProcessor, FinancialDiagnostic, ValuationCalculator
except ImportError as e:
    app.logger.error(f"Erro ao importar módulos de processamento: {e}")
    # Definir classes dummy para evitar erros de inicialização (SINTAXE CORRIGIDA)
    class QuestionnaireTemplate:
        @staticmethod
        def get_template():
            return {"sections": []}

    class DocumentProcessor:
        def __init__(self, *args, **kwargs):
            pass
        def process_document(self, *args, **kwargs):
            return None

    class FinancialDiagnostic:
        def generate_diagnostic(self, *args, **kwargs):
            return None

    class ValuationCalculator:
        def calculate_valuation(self, *args, **kwargs):
            return None

# Inicializar classes de processamento (usando as reais ou as dummy)
document_processor = DocumentProcessor(app.config["UPLOAD_FOLDER"])
financial_diagnostic = FinancialDiagnostic()
valuation_calculator = ValuationCalculator()

# Decorator para verificar se o usuário está logado (Modo Demo)
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for("login"))
        # Em modo demo, não precisamos verificar o usuário no DB
        return f(*args, **kwargs)
    return decorated_function

# Rotas para autenticação
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Sanitizar entrada
        email = security_manager.sanitize_input(email)

        # --- Início: Login Estático (Modo Demo) ---
        DEMO_EMAIL = "demo@cfoasaservice.com"
        DEMO_PASSWORD = "demo123"

        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            # Definir dados de sessão fixos para o usuário demo
            session["user_id"] = 999 # ID Fixo para demo
            session["user_name"] = "Usuário Demo"
            session["user_email"] = DEMO_EMAIL
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=1) # Sessão mais curta para demo

            response = redirect(url_for("dashboard"))
            flash("Login de demonstração realizado com sucesso!", "success")
            return response
        else:
            flash("Email ou senha incorretos. Use as credenciais de demonstração.", "danger")
        # --- Fim: Login Estático (Modo Demo) ---

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()
    return render_template("login.html", csrf_token=csrf_token)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Desabilitar registro em modo demo
    flash("O registro de novos usuários está desabilitado no modo de demonstração.", "info")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"], endpoint="forgot_password")
def forgot_password():
    # Desabilitar recuperação de senha em modo demo
    flash("A recuperação de senha está desabilitada no modo de demonstração.", "info")
    return redirect(url_for("login"))

@app.route("/reset-password/<token>", methods=["GET", "POST"], endpoint="reset_password")
def reset_password(token):
    # Desabilitar recuperação de senha em modo demo
    flash("A recuperação de senha está desabilitada no modo de demonstração.", "info")
    return redirect(url_for("login"))

@app.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    # Desabilitar exclusão de conta em modo demo
    flash("A exclusão de conta está desabilitada no modo de demonstração.", "info")
    return redirect(url_for("dashboard"))

# Rotas principais da aplicação (Modo Demo - podem não funcionar completamente)
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Em modo demo, não buscamos empresas reais
    user_name = session.get("user_name", "Usuário Demo")
    companies = [] # Lista vazia para demonstração
    return render_template("dashboard.html", user={"name": user_name}, companies=companies)

@app.route("/add-company", methods=["GET", "POST"])
@login_required
def add_company():
    if request.method == "POST":
        flash("Adicionar empresas está desabilitado no modo de demonstração.", "info")
        return redirect(url_for("dashboard"))

    csrf_token = security_manager.generate_csrf_token()
    return render_template("add_company.html", csrf_token=csrf_token)

@app.route("/company/<int:company_id>")
@login_required
def company_detail(company_id):
    # Em modo demo, mostramos dados fictícios ou uma mensagem
    flash("Visualização de detalhes da empresa desabilitada no modo de demonstração.", "info")
    # Poderíamos renderizar a página com dados fixos se necessário para UI
    # company_demo = {"id": company_id, "name": f"Empresa Demo {company_id}"}
    # return render_template("company_detail.html", company=company_demo, documents=[], questionnaire=None, progress=0)
    return redirect(url_for("dashboard"))

@app.route("/company/<int:company_id>/questionnaire", methods=["GET", "POST"])
@login_required
def questionnaire_view(company_id):
    if request.method == "POST":
        flash("Salvar questionário está desabilitado no modo de demonstração.", "info")
        return redirect(url_for("dashboard"))

    # Mostrar o template do questionário, mas sem salvar
    questionnaire_template = QuestionnaireTemplate.get_template()
    csrf_token = security_manager.generate_csrf_token()
    company_demo = {"id": company_id, "name": f"Empresa Demo {company_id}"}
    return render_template(
        "questionnaire.html",
        company=company_demo,
        questionnaire_template=questionnaire_template,
        existing_responses={},
        csrf_token=csrf_token
    )

@app.route("/company/<int:company_id>/upload", methods=["GET", "POST"])
@login_required
def upload_document(company_id):
    if request.method == "POST":
        flash("Upload de documentos está desabilitado no modo de demonstração.", "info")
        return redirect(url_for("dashboard"))

    csrf_token = security_manager.generate_csrf_token()
    company_demo = {"id": company_id, "name": f"Empresa Demo {company_id}"}
    return render_template("upload_document.html", company=company_demo, csrf_token=csrf_token)

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    # Desabilitar download em modo demo por segurança
    flash("Download de arquivos desabilitado no modo de demonstração.", "info")
    return redirect(url_for("dashboard"))

@app.route("/company/<int:company_id>/financial-diagnostic")
@login_required
def financial_diagnostic_view(company_id):
    # Mostrar página com dados fictícios ou mensagem
    flash("Diagnóstico financeiro desabilitado no modo de demonstração.", "info")
    company_demo = {"id": company_id, "name": f"Empresa Demo {company_id}"}
    return render_template("financial_diagnostic.html", company=company_demo, diagnostic_data=None)

@app.route("/company/<int:company_id>/valuation")
@login_required
def valuation_view(company_id):
    # Mostrar página com dados fictícios ou mensagem
    flash("Cálculo de valuation desabilitado no modo de demonstração.", "info")
    company_demo = {"id": company_id, "name": f"Empresa Demo {company_id}"}
    return render_template("valuation.html", company=company_demo, valuation_data=None)

# Handlers de erro
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro interno do servidor: {e}", exc_info=True)
    return render_template("500.html"), 500

# Ponto de entrada para execução
if __name__ == "__main__":
    # Render define a porta pela variável PORT
    port = int(os.environ.get("PORT", 5000))
    # debug=False é importante para produção no Render
    app.run(debug=False, host="0.0.0.0", port=port)

