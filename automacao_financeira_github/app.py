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

# Importar módulos de segurança
from security_measures import SecurityManager, configure_heroku_security, csrf_protected

# Configuração do aplicativo
app = Flask(__name__)

# Configurar o aplicativo para funcionar atrás de proxies (necessário no Heroku)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Configurações do banco de dados PostgreSQL (Heroku)
database_url = os.environ.get("DATABASE_URL", "")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configurações de upload de arquivos
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "png", "jpg", "jpeg", "xls", "xlsx", "csv", "txt"}

# Garantir que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Inicializar banco de dados
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    status = db.Column(db.String(20), nullable=False)
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

            # Gerar token JWT para API
            jwt_token = security_manager.generate_jwt_token(user.id)

            # Definir cookie seguro com o token JWT
            response = redirect(url_for("dashboard"))
            response.set_cookie(
                "jwt_token",
                jwt_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=86400,  # 1 dia
            )

            flash("Login realizado com sucesso!", "success")
            return response
        else:
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
            return render_template("register.html", csrf_token=csrf_token)

        if password != confirm_password:
            flash("As senhas não coincidem.", "danger")
            return render_template("register.html", csrf_token=csrf_token)

        # Verificar se o email já está em uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Este email já está em uso. Tente outro.", "danger")
            return render_template("register.html", csrf_token=csrf_token)

        # Criar novo usuário
        hashed_password = security_manager.hash_password(password)

        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("register.html", csrf_token=csrf_token)

@app.route("/logout")
def logout():
    session.clear()

    # Remover cookie JWT
    response = redirect(url_for("login"))
    response.delete_cookie("jwt_token")

    flash("Você saiu do sistema.", "info")
    return response

@app.route("/forgot-password", methods=["GET", "POST"])
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
            db.session.commit()

            # Em um sistema real, enviaríamos um email com o link de recuperação
            # Para fins de demonstração, apenas mostramos o token
            flash(f"Um link de recuperação foi enviado para seu email. Token: {reset_token}", "info")
            return redirect(url_for("login"))
        else:
            flash("Email não encontrado.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("forgot_password.html", csrf_token=csrf_token)

@app.route("/reset-password/<token>", methods=["GET", "POST"])
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
            return render_template("reset_password.html", token=token, csrf_token=csrf_token)

        # Atualizar senha
        hashed_password = security_manager.hash_password(password)

        user.password = hashed_password
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash("Senha atualizada com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("reset_password.html", token=token, csrf_token=csrf_token)

@app.route("/delete-account", methods=["GET", "POST"])
@login_required
@csrf_protected
def delete_account():
    if request.method == "POST":
        password = request.form.get("password")

        # Verificar senha
        user = User.query.get(session["user_id"])

        if user and security_manager.check_password(user.password, password):
            # Excluir usuário (cascade delete configurado nos relacionamentos)
            db.session.delete(user)
            db.session.commit()

            # Limpar sessão
            session.clear()

            # Remover cookie JWT
            response = redirect(url_for("login"))
            response.delete_cookie("jwt_token")

            flash("Sua conta foi excluída com sucesso.", "info")
            return response
        else:
            flash("Senha incorreta. Tente novamente.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("delete_account.html", csrf_token=csrf_token)

# Rotas para dashboard e empresas
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Buscar empresas do usuário
    companies = Company.query.filter_by(user_id=session["user_id"]).all()

    return render_template("dashboard.html", companies=companies)

@app.route("/company/add", methods=["GET", "POST"])
@login_required
@csrf_protected
def add_company():
    if request.method == "POST":
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
            return render_template("add_company.html", csrf_token=security_manager.generate_csrf_token())

        # Criar nova empresa
        new_company = Company(
            user_id=session["user_id"],
            name=name,
            cnpj=cnpj,
            segment=segment,
            description=description,
        )

        db.session.add(new_company)
        db.session.commit()

        flash("Empresa adicionada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("add_company.html", csrf_token=csrf_token)

@app.route("/company/<int:company_id>")
@login_required
def company_detail(company_id):
    # Buscar empresa
    company = Company.query.filter_by(id=company_id, user_id=session["user_id"]).first_or_404()

    # Buscar documentos da empresa
    documents = Document.query.filter_by(company_id=company_id).all()

    # Buscar questionário da empresa
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    # Se não existir questionário, criar um vazio
    has_questionnaire = questionnaire is not None

    return render_template(
        "company_detail.html",
        company=company,
        documents=documents,
        has_questionnaire=has_questionnaire,
    )

@app.route("/company/<int:company_id>/questionnaire", methods=["GET", "POST"])
@login_required
@csrf_protected
def questionnaire(company_id):
    # Buscar empresa
    company = Company.query.filter_by(id=company_id, user_id=session["user_id"]).first_or_404()

    # Obter template do questionário
    template = QuestionnaireTemplate.get_template()

    # Buscar questionário existente
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    if request.method == "POST":
        # Processar respostas do formulário
        responses = {}

        for section in template["sections"]:
            section_id = section["id"]
            responses[section_id] = {}

            for question in section["questions"]:
                question_id = question["id"]
                field_name = f"{section_id}_{question_id}"
                response_value = request.form.get(field_name, "")

                # Sanitizar entrada
                response_value = security_manager.sanitize_input(response_value)

                responses[section_id][question_id] = response_value

        # Salvar questionário
        if questionnaire:
            questionnaire.responses = json.dumps(responses)
            questionnaire.updated_at = datetime.utcnow()
        else:
            questionnaire = Questionnaire(company_id=company_id, responses=json.dumps(responses))
            db.session.add(questionnaire)

        db.session.commit()

        flash("Questionário salvo com sucesso!", "success")
        return redirect(url_for("company_detail", company_id=company_id))

    # Preparar dados do questionário para o template
    questionnaire_data = None
    if questionnaire:
        try:
            questionnaire_data = {
                "id": questionnaire.id,
                "responses": json.loads(questionnaire.responses),
            }
        except json.JSONDecodeError:
            app.logger.error(f"Erro ao decodificar JSON do questionário {questionnaire.id}")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template(
        "questionnaire.html",
        company=company,
        template=template,
        questionnaire=questionnaire_data,
        csrf_token=csrf_token,
    )

@app.route("/company/<int:company_id>/upload", methods=["GET", "POST"])
@login_required
@csrf_protected
def upload_document(company_id):
    # Buscar empresa
    company = Company.query.filter_by(id=company_id, user_id=session["user_id"]).first_or_404()

    if request.method == "POST":
        # Verificar se o arquivo foi enviado
        if "document" not in request.files:
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        file = request.files["document"]

        # Se o usuário não selecionar um arquivo, o navegador envia um arquivo vazio
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        document_type = request.form.get("document_type")
        description = request.form.get("description", "")

        # Sanitizar entrada
        document_type = security_manager.sanitize_input(document_type)
        description = security_manager.sanitize_input(description)

        if not document_type:
            flash("Tipo de documento é obrigatório.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Gerar nome seguro para o arquivo
            original_filename = file.filename
            filename = secure_filename(original_filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

            # Salvar arquivo
            file.save(file_path)

            # Processar documento (simulação)
            result = {"processed": True, "message": "Documento recebido para processamento."}
            # result = document_processor.process_document(file_path, document_type)

            # Salvar informações do documento no banco de dados
            new_document = Document(
                company_id=company_id,
                original_filename=original_filename,
                stored_filename=unique_filename,
                document_type=document_type,
                file_path=file_path,
                extracted_data=json.dumps(result) if result else None,
                status="processed" if result and result.get("processed") else "error",
            )

            db.session.add(new_document)
            db.session.commit()

            flash("Documento enviado com sucesso!", "success")
            return redirect(url_for("company_detail", company_id=company_id))
        else:
            flash("Tipo de arquivo não permitido.", "danger")

    # Gerar token CSRF para o formulário
    csrf_token = security_manager.generate_csrf_token()

    return render_template("upload_document.html", company=company, csrf_token=csrf_token)

@app.route("/company/<int:company_id>/diagnostic")
@login_required
def financial_diagnostic_route(company_id): # Renomeado para evitar conflito
    # Buscar empresa
    company = Company.query.filter_by(id=company_id, user_id=session["user_id"]).first_or_404()

    # Buscar documentos da empresa
    documents = Document.query.filter_by(company_id=company_id, status="processed").all()

    # Converter documentos para formato adequado
    documents_data = []
    for doc in documents:
        if doc.extracted_data:
            try:
                extracted_data = json.loads(doc.extracted_data)
                documents_data.append(extracted_data)
            except json.JSONDecodeError:
                app.logger.error(f"Erro ao decodificar JSON do documento {doc.id}")

    # Buscar questionário da empresa
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    # Preparar dados do questionário
    questionnaire_data = None
    if questionnaire:
        try:
            questionnaire_data = json.loads(questionnaire.responses)
        except json.JSONDecodeError:
            app.logger.error(f"Erro ao decodificar JSON do questionário {questionnaire.id}")

    # Gerar diagnóstico
    diagnostic = None
    if questionnaire_data or documents_data:
        diagnostic = financial_diagnostic.generate_diagnostic(documents_data, questionnaire_data)

    return render_template(
        "financial_diagnostic.html", company=company, diagnostic=diagnostic
    )

@app.route("/company/<int:company_id>/valuation")
@login_required
def valuation_route(company_id): # Renomeado para evitar conflito
    # Buscar empresa
    company = Company.query.filter_by(id=company_id, user_id=session["user_id"]).first_or_404()

    # Buscar documentos da empresa
    documents = Document.query.filter_by(company_id=company_id, status="processed").all()

    # Converter documentos para formato adequado
    financial_data = []
    for doc in documents:
        if doc.extracted_data:
            try:
                extracted_data = json.loads(doc.extracted_data)
                financial_data.append(extracted_data)
            except json.JSONDecodeError:
                app.logger.error(f"Erro ao decodificar JSON do documento {doc.id}")

    # Buscar questionário da empresa
    questionnaire = Questionnaire.query.filter_by(company_id=company_id).first()

    # Preparar dados do questionário
    questionnaire_data = None
    if questionnaire:
        try:
            questionnaire_data = json.loads(questionnaire.responses)
        except json.JSONDecodeError:
            app.logger.error(f"Erro ao decodificar JSON do questionário {questionnaire.id}")

    # Calcular valuation
    valuation_result = None
    if questionnaire_data:
        valuation_result = valuation_calculator.calculate_valuation(financial_data, questionnaire_data)

    return render_template("valuation.html", company=company, valuation=valuation_result)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return app.send_static_file(filename)

@app.route("/uploads/<path:filename>")
@login_required
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Criar usuário de demonstração
def create_demo_user():
    # Verificar se o usuário de demonstração já existe
    demo_user = User.query.filter_by(email="demo@cfoasaservice.com").first()

    if not demo_user:
        # Criar usuário de demonstração
        hashed_password = security_manager.hash_password("demo123")

        demo_user = User(
            name="Usuário Demo", email="demo@cfoasaservice.com", password=hashed_password
        )

        db.session.add(demo_user)
        db.session.commit()

        # Criar empresa de demonstração
        demo_company = Company(
            user_id=demo_user.id,
            name="Empresa Demonstração",
            cnpj="12.345.678/0001-90",
            segment="Tecnologia",
            description="Empresa de demonstração para o sistema CFO as a Service",
        )

        db.session.add(demo_company)
        db.session.commit()

        # Criar questionário de demonstração
        template = QuestionnaireTemplate.get_template()
        responses = {
            "rentabilidade": {
                "margem_liquida": "12%",
                "margem_bruta": "35%",
                "variacao_receita": "8%",
                "ganhos_nao_recorrentes": "Venda de um imóvel no valor de R$ 500.000 no último trimestre.",
            },
            "liquidez": {
                "geracao_caixa": "A empresa tem gerado caixa operacional positivo nos últimos 12 meses, com média mensal de R$ 80.000.",
                "uso_recursos": "Os recursos têm sido utilizados principalmente para investimentos em expansão (60%) e pagamento de dívidas (30%), com 10% distribuídos aos sócios.",
                "capital_giro": "R$ 750.000",
                "current_ratio": "1.8",
            },
            "endividamento": {
                "nivel_dividas": "A empresa possui R$ 1.500.000 em dívidas, sendo 70% de longo prazo (financiamentos bancários) e 30% de curto prazo (fornecedores e empréstimos).",
                "prazos": "As dívidas de longo prazo têm prazo médio de 4 anos. As de curto prazo vencem em até 12 meses.",
                "cobertura_juros": "3.5",
                "riscos_fora_balanco": "Existem garantias prestadas para parceiros comerciais no valor de R$ 300.000.",
            },
            "eficiencia": {
                "giro_estoque": "6.2",
                "prazo_recebimento": "45",
                "prazo_pagamento": "30",
                "uso_ativos": "A empresa tem um giro do ativo total de 1.2x, indicando uso moderadamente eficiente dos ativos.",
            },
            "crescimento": {
                "evolucao_receita": "15%",
                "dependencia_produtos": "O principal produto representa 40% da receita total.",
                "riscos_mercado": "Aumento da concorrência internacional e possíveis mudanças regulatórias no setor.",
            },
            "cenario_externo": {
                "impacto_concorrencia": "Pressão moderada sobre as margens devido a novos entrantes no mercado.",
                "impacto_economia": "Sensibilidade média a variações na taxa de juros e câmbio.",
                "impacto_regulacoes": "Mudanças na legislação ambiental podem exigir investimentos adicionais nos próximos 2 anos.",
            },
            "gestao": {
                "metas_financeiras": "Crescimento de receita de 20% ao ano, margem EBITDA de 18% e redução da dívida líquida/EBITDA para menos de 1.5x em 3 anos.",
                "controle_custos": "Implementação de sistema de gestão de custos e revisão trimestral de despesas com metas de redução.",
                "sustentabilidade_dividendos": "Política de distribuição de 30% do lucro líquido, condicionada a manter índice de liquidez corrente acima de 1.5.",
            },
            "valuation": {
                "expectativa_crescimento": "10%",
                "taxa_desconto": "15%",
                "multiplo_referencia": "8x EBITDA",
                "informacoes_adicionais": "A empresa está em negociação para uma aquisição estratégica que pode impactar o valuation."
            }
        }

        demo_questionnaire = Questionnaire(
            company_id=demo_company.id, responses=json.dumps(responses)
        )

        db.session.add(demo_questionnaire)
        db.session.commit()

        app.logger.info("Usuário e empresa de demonstração criados com sucesso!")
    else:
        app.logger.info("Usuário de demonstração já existe.")

# Iniciar o aplicativo
if __name__ == "__main__":
    with app.app_context():
        # Criar tabelas do banco de dados
        db.create_all()

        # Criar usuário de demonstração
        create_demo_user()

    # Iniciar o servidor Flask
    # O Heroku usa o Gunicorn (definido no Procfile), então esta linha não será executada lá
    # app.run(debug=False, host='0.0.0.0')

