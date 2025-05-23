"""
Configuração do aplicativo Flask para implantação no Render.com (Versão Completa).
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

# Configurações do banco de dados PostgreSQL (Render)
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

# Inicializar banco de dados
db = SQLAlchemy(app)
migrate = Migrate(app, db) # Flask-Migrate será usado para criar/atualizar tabelas

# --- INÍCIO: Inicialização automática do banco de dados via before_first_request ---
@app.before_request
def create_tables():
    # O decorator @app.before_request executa antes de CADA requisição.
    # Usamos uma flag global para garantir que db.create_all() só rode uma vez.
    if not getattr(app, 'db_initialized', False):
        with app.app_context():
            inspector = inspect(db.engine)
            if not inspector.has_table("users"):
                app.logger.info("Tabela 'users' não encontrada. Criando todas as tabelas...")
                try:
                    db.create_all()
                    app.logger.info("Tabelas criadas com sucesso.")
                except Exception as e:
                    app.logger.error(f"Erro ao criar tabelas: {e}")
            else:
                app.logger.info("Tabelas já existem.")
        app.db_initialized = True # Marca que a inicialização foi feita (ou verificada)
# --- FIM: Inicialização automática do banco de dados via before_first_request ---

# Inicializar gerenciador de segurança
security_manager = SecurityManager(app)
app.security_manager = security_manager  # Tornar acessível globalmente

# Aplicar configurações de segurança (Revisar se necessário para Render)
# configure_heroku_security(app) # Comentado por enquanto

# Configurar logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Aplicativo CFO as a Service iniciado (Versão Completa)")

# Modelos de banco de dados (sem alterações)
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
    status = db.Column(db.String(20), nullable=False, default="Pendente") # Status inicial
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Questionnaire(db.Model):
    __tablename__ = "questionnaires"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    responses = db.Column(db.Text, nullable=False)  # JSON serializado
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

# Funções auxiliares
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Importar módulos de processamento
# Certifique-se que estes arquivos existem no mesmo diretório
try:
    from questionnaire_storage import QuestionnaireTemplate
    from document_processor import DocumentProcessor, FinancialDiagnostic, ValuationCalculator
except ImportError as e:
    app.logger.error(f"Erro ao importar módulos de processamento: {e}")
    # Definir classes dummy para evitar erros de inicialização
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

# Inicializar classes de processamento
document_processor = DocumentProcessor(app.config["UPLOAD_FOLDER"])
financial_diagnostic = FinancialDiagnostic()
valuation_calculator = ValuationCalculator()

# Decorator para verificar se o usuário está logado
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, faça login para acessar esta página.", "warning")
            return redirect(url_for("login"))
        # Verificar se o usuário ainda existe no banco de dados
        user = User.query.get(session["user_id"])
        if not user:
            session.clear()
            flash("Sua sessão expirou ou sua conta foi removida. Faça login novamente.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Rotas para autenticação (Versão Completa - com banco de dados)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Sanitizar entrada
        email = security_manager.sanitize_input(email)

        user = User.query.filter_by(email=email).first()

        if user and security_manager.check_password(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session.permanent = True # Manter sessão
            app.permanent_session_lifetime = timedelta(days=7) # Duração da sessão

            response = redirect(url_for("dashboard"))
            flash("Login realizado com sucesso!", "success")
            return response
        else:
            # Implementar rate limiting aqui se necessário
            flash("Email ou senha incorretos. Tente novamente.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()
    return render_template("login.html", csrf_token=csrf_token)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("register"))

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Sanitizar entrada
        name = security_manager.sanitize_input(name)
        email = security_manager.sanitize_input(email)

        # Validações básicas
        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("register.html", csrf_token=csrf_token, name=name, email=email)

        if password != confirm_password:
            flash("As senhas não coincidem.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("register.html", csrf_token=csrf_token, name=name, email=email)

        # Validação de senha forte (exemplo)
        if len(password) < 8:
             flash("A senha deve ter pelo menos 8 caracteres.", "danger")
             csrf_token = security_manager.generate_csrf_token()
             return render_template("register.html", csrf_token=csrf_token, name=name, email=email)

        # Verificar se o email já está em uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Este email já está em uso. Tente outro.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("register.html", csrf_token=csrf_token, name=name, email=email)

        # Criar novo usuário
        hashed_password = security_manager.hash_password(password)
        new_user = User(name=name, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao registrar usuário: {e}")
            flash("Ocorreu um erro ao tentar registrar. Tente novamente mais tarde.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("register.html", csrf_token=csrf_token, name=name, email=email)

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()
    return render_template("register.html", csrf_token=csrf_token)

@app.route("/logout")
def logout():
    session.clear()
    response = redirect(url_for("login"))
    flash("Você saiu do sistema.", "info")
    return response

@app.route("/forgot-password", methods=["GET", "POST"], endpoint="forgot_password")
def forgot_password():
    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("forgot_password"))

        email = request.form.get("email")
        email = security_manager.sanitize_input(email)
        user = User.query.filter_by(email=email).first()

        if user:
            reset_token = str(uuid.uuid4())
            expiration = datetime.utcnow() + timedelta(hours=1)
            user.reset_token = reset_token
            user.reset_token_expiry = expiration
            try:
                db.session.commit()
                # Em um sistema real, enviaríamos um email com o link de recuperação
                app.logger.info(f"Token de recuperação gerado para {email}: {reset_token}")
                flash(f"Um link de recuperação foi enviado para seu email (se ele estiver cadastrado).", "info")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar token de recuperação para {email}: {e}")
                flash("Ocorreu um erro ao processar sua solicitação. Tente novamente.", "danger")
        else:
            flash("Se o email estiver cadastrado, um link de recuperação será enviado.", "info")
            app.logger.warning(f"Tentativa de recuperação de senha para email não cadastrado: {email}")
            return redirect(url_for("login"))

    csrf_token = security_manager.generate_csrf_token()
    return render_template("forgot_password.html", csrf_token=csrf_token)

@app.route("/reset-password/<token>", methods=["GET", "POST"], endpoint="reset_password")
def reset_password(token):
    user = User.query.filter(
        User.reset_token == token, User.reset_token_expiry > datetime.utcnow()
    ).first()

    if not user:
        flash("Link de recuperação inválido ou expirado.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("reset_password", token=token))

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not password or password != confirm_password:
            flash("As senhas não coincidem.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("reset_password.html", token=token, csrf_token=csrf_token)

        if len(password) < 8:
             flash("A senha deve ter pelo menos 8 caracteres.", "danger")
             csrf_token = security_manager.generate_csrf_token()
             return render_template("reset_password.html", token=token, csrf_token=csrf_token)

        # Atualizar senha e invalidar token
        user.password = security_manager.hash_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        try:
            db.session.commit()
            flash("Sua senha foi redefinida com sucesso! Faça login com a nova senha.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao redefinir senha para usuário {user.id}: {e}")
            flash("Ocorreu um erro ao tentar redefinir sua senha. Tente novamente.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("reset_password.html", token=token, csrf_token=csrf_token)

    csrf_token = security_manager.generate_csrf_token()
    return render_template("reset_password.html", token=token, csrf_token=csrf_token)

@app.route("/delete-account", methods=["GET", "POST"], endpoint="delete_account")
@login_required
def delete_account():
    user_id = session["user_id"]
    user = User.query.get(user_id)

    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("delete_account"))

        password = request.form.get("password")
        if not password:
            flash("Por favor, digite sua senha para confirmar a exclusão da conta.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("delete_account.html", csrf_token=csrf_token)

        if not security_manager.check_password(user.password, password):
            flash("Senha incorreta. Tente novamente.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("delete_account.html", csrf_token=csrf_token)

        try:
            # Excluir usuário (e todas as empresas, documentos e questionários relacionados via cascade)
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash("Sua conta foi excluída com sucesso.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao excluir usuário {user_id}: {e}")
            flash("Ocorreu um erro ao tentar excluir sua conta. Tente novamente mais tarde.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("delete_account.html", csrf_token=csrf_token)

    csrf_token = security_manager.generate_csrf_token()
    return render_template("delete_account.html", csrf_token=csrf_token)

# Rotas principais
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = User.query.get(user_id)
    companies = Company.query.filter_by(user_id=user_id).order_by(Company.name).all()
    return render_template("dashboard.html", user=user, companies=companies)

@app.route("/add-company", methods=["GET", "POST"])
@login_required
def add_company():
    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("add_company"))

        name = request.form.get("name")
        cnpj = request.form.get("cnpj")
        segment = request.form.get("segment")
        description = request.form.get("description")

        # Sanitizar entrada
        name = security_manager.sanitize_input(name)
        cnpj = security_manager.sanitize_input(cnpj)
        segment = security_manager.sanitize_input(segment)
        description = security_manager.sanitize_input(description)

        if not name:
            flash("O nome da empresa é obrigatório.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("add_company.html", csrf_token=csrf_token, name=name, cnpj=cnpj, segment=segment, description=description)

        user_id = session["user_id"]
        new_company = Company(
            user_id=user_id,
            name=name,
            cnpj=cnpj,
            segment=segment,
            description=description
        )

        try:
            db.session.add(new_company)
            db.session.commit()
            flash(f"Empresa {name} adicionada com sucesso!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao adicionar empresa para usuário {user_id}: {e}")
            flash("Ocorreu um erro ao tentar adicionar a empresa. Tente novamente.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("add_company.html", csrf_token=csrf_token, name=name, cnpj=cnpj, segment=segment, description=description)

    csrf_token = security_manager.generate_csrf_token()
    return render_template("add_company.html", csrf_token=csrf_token)

@app.route("/company/<int:company_id>")
@login_required
def company_detail(company_id):
    user_id = session["user_id"]
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    documents = Document.query.filter_by(company_id=company_id).order_by(Document.upload_date.desc()).all()
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).order_by(Questionnaire.updated_at.desc()).first()

    # Calcular progresso (exemplo simples)
    progress = 0
    if questionnaire: progress += 50
    if documents: progress += 50

    return render_template("company_detail.html", company=company, documents=documents, questionnaire=questionnaire, progress=progress)

@app.route("/company/<int:company_id>/questionnaire", methods=["GET", "POST"])
@login_required
def questionnaire_view(company_id):
    user_id = session["user_id"]
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    questionnaire_template = QuestionnaireTemplate.get_template()
    existing_questionnaire = Questionnaire.query.filter_by(company_id=company_id).order_by(Questionnaire.updated_at.desc()).first()
    
    # Correção: Garantir que existing_responses seja sempre um    # Carregar respostas existentes se houver
    existing_questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()
    existing_responses = {}
    if existing_questionnaire and existing_questionnaire.responses:
        try:
            # Carregar diretamente como dicionário plano
            existing_responses = json.loads(existing_questionnaire.responses)
            app.logger.info(f"Carregadas {len(existing_responses)} respostas existentes para empresa {company_id}")
        except Exception as e:
            app.logger.error(f"Erro ao carregar respostas existentes: {e}")

    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("questionnaire_view", company_id=company_id))

        # Coletar todas as respostas do formulário como dicionário plano
        responses = {}
        for section in questionnaire_template.get("sections", []):
            for question in section.get("questions", []):
                q_id = question.get("id", "")
                if q_id:
                    # Obter o valor do formulário
                    value = request.form.get(q_id, "")
                    # Armazenar diretamente no dicionário plano
                    responses[q_id] = value
                    
        app.logger.info(f"Coletadas {len(responses)} respostas do formulário para empresa {company_id}")

        # Serializar para JSON
        try:
            responses_json = json.dumps(responses)
        except Exception as e:
            app.logger.error(f"Erro ao serializar respostas para JSON: {e}")
            flash("Ocorreu um erro ao processar as respostas. Tente novamente.", "danger")
            return render_template(
                "questionnaire.html",
                company=company,
                questionnaire_template=questionnaire_template,
                existing_responses=existing_responses,
                csrf_token=csrf_token
            )

        try:
            if existing_questionnaire:
                # Atualizar questionário existente
                existing_questionnaire.responses = responses_json
                existing_questionnaire.updated_at = datetime.utcnow()
                app.logger.info(f"Atualizando questionário existente para empresa {company_id}")
            else:
                # Criar novo questionário
                new_questionnaire = Questionnaire(company_id=company_id, responses=responses_json)
                db.session.add(new_questionnaire)
                app.logger.info(f"Criando novo questionário para empresa {company_id}")
            
            # Commit das alterações
            db.session.commit()
            flash("Questionário salvo com sucesso!", "success")
            
            # Redirecionar para a página de detalhes da empresa
            return redirect(url_for("company_detail", company_id=company_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao salvar questionário para empresa {company_id}: {e}")
            flash("Ocorreu um erro ao tentar salvar o questionário. Tente novamente.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()
    
    # Renderizar o template com os dados necessários
    return render_template(
        "questionnaire.html",
        company=company,
        questionnaire_template=questionnaire_template,
        existing_responses=existing_responses,
        csrf_token=csrf_token
    )

@app.route("/company/<int:company_id>/upload", methods=["GET", "POST"])
@login_required
def upload_document(company_id):
    user_id = session["user_id"]
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()

    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("upload_document", company_id=company_id))

        if "file" not in request.files:
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        document_type = request.form.get("document_type", "Outro")

        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            # Criar um nome de arquivo único para armazenamento
            stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)

            try:
                file.save(file_path)

                # Salvar informações no banco de dados
                new_document = Document(
                    company_id=company_id,
                    original_filename=original_filename,
                    stored_filename=stored_filename,
                    document_type=document_type,
                    file_path=file_path,
                    status="Recebido" # Atualizar status
                )
                db.session.add(new_document)
                db.session.commit()

                flash(f"Arquivo {original_filename} enviado com sucesso!", "success")

                # Opcional: Iniciar processamento assíncrono aqui
                # process_document_async(new_document.id)

                return redirect(url_for("company_detail", company_id=company_id))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar upload para empresa {company_id}: {e}")
                flash("Ocorreu um erro ao tentar salvar o arquivo. Tente novamente.", "danger")
                # Tentar remover o arquivo se o save falhou após o upload
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as remove_error:
                        app.logger.error(f"Erro ao remover arquivo órfão {file_path}: {remove_error}")
        else:
            flash("Tipo de arquivo não permitido.", "danger")

    csrf_token = security_manager.generate_csrf_token()
    return render_template("upload_document.html", company=company, csrf_token=csrf_token)

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    # Validar se o usuário logado tem acesso a este arquivo
    user_id = session["user_id"]
    document = Document.query.filter_by(stored_filename=filename).first_or_404()
    company = Company.query.filter_by(id=document.company_id, user_id=user_id).first()

    if not company:
        flash("Você não tem permissão para acessar este arquivo.", "danger")
        return redirect(url_for("dashboard"))

    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        app.logger.error(f"Arquivo não encontrado no servidor: {filename}")
        flash("Arquivo não encontrado no servidor.", "danger")
        return redirect(url_for("company_detail", company_id=document.company_id))

@app.route("/company/<int:company_id>/financial-diagnostic")
@login_required
def financial_diagnostic_view(company_id):
    user_id = session["user_id"]
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()

    # Coletar dados (exemplo: do questionário e documentos processados)
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()
    documents = Document.query.filter_by(company_id=company_id, status="Processado").all()

    # Inicializar dados vazios
    questionnaire_data = {}
    document_data = []
    
    # Processar dados do questionário se existir
    if questionnaire and questionnaire.responses:
        try:
            # Usar diretamente o dicionário plano de respostas
            questionnaire_data = json.loads(questionnaire.responses)
            app.logger.info(f"Dados do questionário processados para empresa {company_id}: {len(questionnaire_data)} campos")
        except Exception as e:
            app.logger.error(f"Erro ao processar dados do questionário: {e}")
            questionnaire_data = {}
    
    # Processar dados dos documentos se existirem
    for doc in documents:
        if doc.extracted_data:
            try:
                doc_data = json.loads(doc.extracted_data)
                document_data.append(doc_data)
            except json.JSONDecodeError:
                app.logger.error(f"Erro ao decodificar JSON do documento {doc.id}")

    # Gerar diagnóstico com os dados processados
    diagnostic = financial_diagnostic.generate_diagnostic(questionnaire_data, document_data)

    return render_template("financial_diagnostic.html", company=company, diagnostic=diagnostic)

@app.route("/company/<int:company_id>/valuation")
@login_required
def valuation_view(company_id):
    user_id = session["user_id"]
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()

    # Coletar dados (similar ao diagnóstico)
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()
    documents = Document.query.filter_by(company_id=company_id, status="Processado").all()

    # Inicializar dados vazios
    questionnaire_data = {}
    document_data = []
    
    # Processar dados do questionário se existir
    if questionnaire and questionnaire.responses:
        try:
            # Deserializar JSON para dicionário
            responses_dict = json.loads(questionnaire.responses)
            
            # Extrair respostas de todas as seções para um único dicionário plano
            for section_id, questions in responses_dict.items():
                if isinstance(questions, dict):
                    # Adicionar todas as respostas ao dicionário principal
                    questionnaire_data.update(questions)
                else:
                    # Caso a estrutura seja diferente, tentar usar diretamente
                    questionnaire_data[section_id] = questions
            
            app.logger.info(f"Dados do questionário processados para valuation da empresa {company_id}")
        except json.JSONDecodeError:
            app.logger.error(f"Erro ao decodificar JSON das respostas para valuation da empresa {company_id}")
    
    # Processar dados dos documentos se existirem
    for doc in documents:
        if doc.extracted_data:
            try:
                doc_data = json.loads(doc.extracted_data)
                document_data.append(doc_data)
            except json.JSONDecodeError:
                app.logger.error(f"Erro ao decodificar JSON do documento {doc.id} para valuation")

    # Calcular valuation com os dados processados
    valuation = valuation_calculator.calculate_valuation(questionnaire_data, document_data)

    return render_template("valuation.html", company=company, valuation=valuation)

# Handlers de erro
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro interno do servidor: {e}", exc_info=True)
    # Tentar rollback da sessão do DB em caso de erro 500 durante uma transação
    try:
        db.session.rollback()
        app.logger.info("Sessão do banco de dados revertida após erro 500.")
    except Exception as rollback_error:
        app.logger.error(f"Erro ao tentar reverter sessão do banco de dados: {rollback_error}")
    return render_template("500.html"), 500

# Ponto de entrada para execução
if __name__ == "__main__":
    # Render define a porta pela variável PORT
    port = int(os.environ.get("PORT", 5000))
    # debug=False é importante para produção no Render
    app.run(debug=False, host="0.0.0.0", port=port)
