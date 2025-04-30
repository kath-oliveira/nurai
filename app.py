"""
Configuração do aplicativo Flask para implantação no Heroku.
Este módulo contém as configurações necessárias para executar o aplicativo
de automação financeira no ambiente de produção do Heroku.
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

# Configurar o aplicativo para funcionar atrás de proxies (necessário no Heroku)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Configurações do banco de dados PostgreSQL (Heroku)
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
migrate = Migrate(app, db)

# --- Início: Inicialização automática do banco de dados ---
def initialize_database():
    with app.app_context():
        inspector = inspect(db.engine)
        # Verifica se a tabela 'users' existe como um indicativo
        if not inspector.has_table("users"):
            app.logger.info("Tabelas do banco de dados não encontradas. Criando tabelas...")
            try:
                db.create_all()
                app.logger.info("Tabelas do banco de dados criadas com sucesso.")
            except Exception as e:
                app.logger.error(f"Erro ao criar tabelas do banco de dados: {e}")
        else:
            app.logger.info("Tabelas do banco de dados já existem.")

# Chama a função de inicialização durante a configuração do app
initialize_database()
# --- Fim: Inicialização automática do banco de dados ---

# Inicializar gerenciador de segurança
security_manager = SecurityManager(app)
app.security_manager = security_manager  # Tornar acessível globalmente

# Aplicar configurações de segurança específicas para o Heroku
configure_heroku_security(app)

# Configurar logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Aplicativo CFO as a Service iniciado")

# Modelos de banco de dados
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
        def __init__(self, *args):
            pass
        def process_document(self, *args):
            return None

    class FinancialDiagnostic:
        def generate_diagnostic(self, *args):
            return None

    class ValuationCalculator:
        def calculate_valuation(self, *args):
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

# Rotas para autenticação
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

            # Gerar token JWT para API (se necessário)
            # jwt_token = security_manager.generate_jwt_token(user.id)

            # Definir cookie seguro com o token JWT (se necessário)
            response = redirect(url_for("dashboard"))
            # response.set_cookie(
            #     "jwt_token",
            #     jwt_token,
            #     httponly=True,
            #     secure=not app.debug, # Secure apenas em produção
            #     samesite="Lax",
            #     max_age=int(app.permanent_session_lifetime.total_seconds()),
            # )

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

    # Remover cookie JWT (se estiver usando)
    response = redirect(url_for("login"))
    # response.delete_cookie("jwt_token")

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

        # Sanitizar entrada
        email = security_manager.sanitize_input(email)

        user = User.query.filter_by(email=email).first()

        if user:
            # Gerar token de recuperação
            reset_token = str(uuid.uuid4())
            expiration = datetime.utcnow() + timedelta(hours=1)

            # Atualizar usuário com token
            user.reset_token = reset_token
            user.reset_token_expiry = expiration
            try:
                db.session.commit()
                # Em um sistema real, enviaríamos um email com o link de recuperação
                # Ex: send_recovery_email(user.email, reset_token)
                app.logger.info(f"Token de recuperação gerado para {email}: {reset_token}")
                flash(f"Um link de recuperação foi enviado para seu email (se ele estiver cadastrado).", "info")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar token de recuperação para {email}: {e}")
                flash("Ocorreu um erro ao processar sua solicitação. Tente novamente.", "danger")
        else:
            # Não informar se o email existe ou não por segurança
            flash("Se o email estiver cadastrado, um link de recuperação será enviado.", "info")
            app.logger.warning(f"Tentativa de recuperação de senha para email não cadastrado: {email}")
            return redirect(url_for("login")) # Redireciona mesmo se não encontrar para não vazar informação

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("forgot_password.html", csrf_token=csrf_token)

@app.route("/reset-password/<token>", methods=["GET", "POST"], endpoint="reset_password")
def reset_password(token):
    # Verificar se o token é válido
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

        # Validação de senha forte (exemplo)
        if len(password) < 8:
             flash("A senha deve ter pelo menos 8 caracteres.", "danger")
             csrf_token = security_manager.generate_csrf_token()
             return render_template("reset_password.html", token=token, csrf_token=csrf_token)

        # Atualizar senha
        hashed_password = security_manager.hash_password(password)

        user.password = hashed_password
        user.reset_token = None
        user.reset_token_expiry = None
        try:
            db.session.commit()
            flash("Senha atualizada com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao resetar senha para {user.email}: {e}")
            flash("Ocorreu um erro ao atualizar sua senha. Tente novamente.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("reset_password.html", token=token, csrf_token=csrf_token)

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("reset_password.html", token=token, csrf_token=csrf_token)

@app.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("delete_account"))

        password = request.form.get("password")
        user_id = session.get("user_id")
        user = User.query.get(user_id)

        if user and security_manager.check_password(user.password, password):
            try:
                # Excluir usuário e dados associados (cascade)
                db.session.delete(user)
                db.session.commit()
                session.clear()
                flash("Sua conta foi excluída com sucesso.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao excluir conta do usuário {user_id}: {e}")
                flash("Ocorreu um erro ao tentar excluir sua conta. Tente novamente.", "danger")
        else:
            flash("Senha incorreta. A exclusão da conta não foi realizada.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("delete_account.html", csrf_token=csrf_token)

# Rotas principais da aplicação
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get("user_id")
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
        user_id = session.get("user_id")

        # Sanitizar entrada
        name = security_manager.sanitize_input(name)
        cnpj = security_manager.sanitize_input(cnpj)
        segment = security_manager.sanitize_input(segment)
        description = security_manager.sanitize_input(description)

        if not name:
            flash("O nome da empresa é obrigatório.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("add_company.html", csrf_token=csrf_token, name=name, cnpj=cnpj, segment=segment, description=description)

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
            flash("Empresa adicionada com sucesso!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao adicionar empresa para usuário {user_id}: {e}")
            flash("Ocorreu um erro ao adicionar a empresa. Tente novamente.", "danger")
            csrf_token = security_manager.generate_csrf_token()
            return render_template("add_company.html", csrf_token=csrf_token, name=name, cnpj=cnpj, segment=segment, description=description)

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("add_company.html", csrf_token=csrf_token)

@app.route("/company/<int:company_id>")
@login_required
def company_detail(company_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    documents = Document.query.filter_by(company_id=company_id).order_by(Document.upload_date.desc()).all()
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).order_by(Questionnaire.updated_at.desc()).first()

    # Calcular progresso (exemplo simples)
    progress = 0
    if questionnaire:
        progress += 50
    if documents:
        progress += 50

    return render_template("company_detail.html", company=company, documents=documents, questionnaire=questionnaire, progress=progress)

@app.route("/company/<int:company_id>/questionnaire", methods=["GET", "POST"])
@login_required
def questionnaire_view(company_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    questionnaire_template = QuestionnaireTemplate.get_template()
    existing_questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()
    existing_responses = json.loads(existing_questionnaire.responses) if existing_questionnaire else {}

    if request.method == "POST":
        # Verificar token CSRF
        csrf_token = request.form.get("csrf_token")
        if not security_manager.validate_csrf_token(csrf_token):
            flash("Erro de validação do formulário. Tente novamente.", "danger")
            return redirect(url_for("questionnaire_view", company_id=company_id))

        responses = {}
        for section in questionnaire_template["sections"]:
            for question in section["questions"]:
                responses[question["id"]] = security_manager.sanitize_input(request.form.get(question["id"]))

        responses_json = json.dumps(responses)

        try:
            if existing_questionnaire:
                existing_questionnaire.responses = responses_json
            else:
                new_questionnaire = Questionnaire(company_id=company_id, responses=responses_json)
                db.session.add(new_questionnaire)
            db.session.commit()
            flash("Questionário salvo com sucesso!", "success")
            return redirect(url_for("company_detail", company_id=company_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao salvar questionário para empresa {company_id}: {e}")
            flash("Ocorreu um erro ao salvar o questionário. Tente novamente.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

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
    user_id = session.get("user_id")
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
            # Criar nome de arquivo único para armazenamento
            file_ext = original_filename.rsplit(".", 1)[1].lower()
            stored_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)

            try:
                file.save(file_path)

                new_document = Document(
                    company_id=company_id,
                    original_filename=original_filename,
                    stored_filename=stored_filename,
                    document_type=document_type,
                    file_path=file_path,
                    status="Enviado" # Atualiza status após salvar
                )
                db.session.add(new_document)
                db.session.commit()

                # Opcional: Iniciar processamento em background aqui
                # process_document_async(new_document.id)

                flash("Documento enviado com sucesso!", "success")
                return redirect(url_for("company_detail", company_id=company_id))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar documento para empresa {company_id}: {e}")
                # Tentar remover arquivo parcialmente salvo se existir
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as remove_error:
                        app.logger.error(f"Erro ao remover arquivo parcialmente salvo {file_path}: {remove_error}")
                flash("Ocorreu um erro ao enviar o documento. Tente novamente.", "danger")

        else:
            flash("Tipo de arquivo não permitido.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("upload_document.html", company=company, csrf_token=csrf_token)

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    # Adicionar verificação para garantir que o usuário só possa acessar seus próprios arquivos
    # Esta é uma implementação básica, pode precisar de mais segurança
    doc = Document.query.filter_by(stored_filename=filename).first_or_404()
    company = Company.query.get_or_404(doc.company_id)
    if company.user_id != session.get("user_id"):
        return "Acesso não autorizado", 403

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/company/<int:company_id>/financial-diagnostic")
@login_required
def financial_diagnostic_view(company_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    documents = Document.query.filter_by(company_id=company_id).all()
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    # Gerar diagnóstico (exemplo)
    diagnostic_data = financial_diagnostic.generate_diagnostic(documents, questionnaire)

    return render_template("financial_diagnostic.html", company=company, diagnostic_data=diagnostic_data)

@app.route("/company/<int:company_id>/valuation")
@login_required
def valuation_view(company_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(id=company_id, user_id=user_id).first_or_404()
    documents = Document.query.filter_by(company_id=company_id).all()
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    # Calcular valuation (exemplo)
    valuation_data = valuation_calculator.calculate_valuation(documents, questionnaire)

    return render_template("valuation.html", company=company, valuation_data=valuation_data)

# Handlers de erro
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Logar o erro real
    app.logger.error(f"Erro interno do servidor: {e}", exc_info=True)
    # Em produção, não mostrar detalhes do erro para o usuário
    return render_template("500.html"), 500

# Ponto de entrada para execução (se necessário para desenvolvimento local)
if __name__ == "__main__":
    # Não use db.create_all() aqui em produção, use migrações
    # Com a inicialização automática acima, isso não é mais necessário
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

