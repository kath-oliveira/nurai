"""
Versão MVP simplificada do aplicativo de automação financeira.
Esta versão elimina a dependência de banco de dados PostgreSQL,
focando apenas no cálculo correto do diagnóstico financeiro.
"""

import os
import json
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

# Importar módulos de processamento
from document_processor import DocumentProcessor, FinancialDiagnostic, ValuationCalculator
from questionnaire_storage import QuestionnaireTemplate

# Configuração do aplicativo
app = Flask(__name__)

# Configurar o aplicativo para funcionar atrás de proxies (Render usa proxies)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Configurações básicas
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "uma-chave-secreta-muito-forte-padrao")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "png", "jpg", "jpeg", "xls", "xlsx", "csv", "txt"}

# Garantir que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Garantir que a pasta de dados exista (para armazenamento JSON)
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

# Configurar logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Aplicativo CFO as a Service iniciado (Versão MVP Simplificada)")

# Inicializar classes de processamento
document_processor = DocumentProcessor(app.config["UPLOAD_FOLDER"])
financial_diagnostic = FinancialDiagnostic()
valuation_calculator = ValuationCalculator()

# Funções auxiliares para armazenamento em JSON
def save_to_json(data, filename):
    """Salva dados em um arquivo JSON."""
    filepath = os.path.join(DATA_FOLDER, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath

def load_from_json(filename):
    """Carrega dados de um arquivo JSON."""
    filepath = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Simulação simplificada de autenticação para o MVP
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Para o MVP, aceita qualquer login
        session["user_id"] = "user_demo"
        session["user_name"] = "Usuário Demo"
        session["user_email"] = email
        
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("dashboard"))
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Para o MVP, apenas simula o registro
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

# Rotas principais
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    # Carrega empresas do usuário (para o MVP, usa dados de exemplo)
    companies = load_from_json(f"companies_{session['user_id']}.json")
    if not companies:
        companies = []
    
    return render_template("dashboard.html", companies=companies)

@app.route("/add-company", methods=["GET", "POST"])
def add_company():
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form.get("name")
        cnpj = request.form.get("cnpj")
        segment = request.form.get("segment")
        description = request.form.get("description")
        
        # Cria nova empresa
        company = {
            "id": str(uuid.uuid4()),
            "user_id": session["user_id"],
            "name": name,
            "cnpj": cnpj,
            "segment": segment,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Carrega empresas existentes
        companies = load_from_json(f"companies_{session['user_id']}.json")
        if not companies:
            companies = []
        
        # Adiciona nova empresa
        companies.append(company)
        
        # Salva empresas
        save_to_json(companies, f"companies_{session['user_id']}.json")
        
        flash("Empresa adicionada com sucesso!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("add_company.html")

@app.route("/company/<company_id>")
def company_detail(company_id):
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    # Carrega empresas
    companies = load_from_json(f"companies_{session['user_id']}.json")
    if not companies:
        flash("Empresa não encontrada.", "danger")
        return redirect(url_for("dashboard"))
    
    # Encontra a empresa específica
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        flash("Empresa não encontrada.", "danger")
        return redirect(url_for("dashboard"))
    
    # Carrega documentos da empresa
    documents = load_from_json(f"documents_{company_id}.json")
    if not documents:
        documents = []
    
    # Carrega questionários da empresa
    questionnaires = load_from_json(f"questionnaires_{company_id}.json")
    if not questionnaires:
        questionnaires = []
    
    return render_template("company_detail.html", company=company, documents=documents, questionnaires=questionnaires)

@app.route("/company/<company_id>/upload-document", methods=["GET", "POST"])
def upload_document(company_id):
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        document_type = request.form.get("document_type")
        
        if "file" not in request.files:
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)
        
        file = request.files["file"]
        
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            stored_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
            file.save(file_path)
            
            # Processa o documento
            result = document_processor.process_document(file_path, document_type)
            
            # Cria registro do documento
            document = {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "original_filename": filename,
                "stored_filename": stored_filename,
                "document_type": document_type,
                "file_path": file_path,
                "extracted_data": result.get("extracted_data", {}),
                "status": result.get("analysis_status", "Processado"),
                "upload_date": datetime.utcnow().isoformat()
            }
            
            # Carrega documentos existentes
            documents = load_from_json(f"documents_{company_id}.json")
            if not documents:
                documents = []
            
            # Adiciona novo documento
            documents.append(document)
            
            # Salva documentos
            save_to_json(documents, f"documents_{company_id}.json")
            
            flash("Documento enviado com sucesso!", "success")
            return redirect(url_for("company_detail", company_id=company_id))
        else:
            flash("Tipo de arquivo não permitido.", "danger")
            return redirect(request.url)
    
    return render_template("upload_document.html", company_id=company_id)

@app.route("/company/<company_id>/questionnaire", methods=["GET", "POST"])
def questionnaire(company_id):
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    # Obtém o template do questionário
    template = QuestionnaireTemplate.get_template()
    
    if request.method == "POST":
        # Coleta as respostas do formulário
        responses = {}
        for section in template["sections"]:
            for question in section["questions"]:
                question_id = question["id"]
                response = request.form.get(question_id)
                responses[question_id] = response
        
        # Cria registro do questionário
        questionnaire_data = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "responses": responses,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Carrega questionários existentes
        questionnaires = load_from_json(f"questionnaires_{company_id}.json")
        if not questionnaires:
            questionnaires = []
        
        # Adiciona novo questionário
        questionnaires.append(questionnaire_data)
        
        # Salva questionários
        save_to_json(questionnaires, f"questionnaires_{company_id}.json")
        
        flash("Questionário enviado com sucesso!", "success")
        return redirect(url_for("company_detail", company_id=company_id))
    
    return render_template("questionnaire.html", company_id=company_id, template=template)

@app.route("/company/<company_id>/financial-diagnostic")
def financial_diagnostic_view(company_id):
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    # Carrega questionários da empresa
    questionnaires = load_from_json(f"questionnaires_{company_id}.json")
    if not questionnaires or len(questionnaires) == 0:
        flash("É necessário preencher o questionário antes de gerar o diagnóstico financeiro.", "warning")
        return redirect(url_for("company_detail", company_id=company_id))
    
    # Usa o questionário mais recente
    questionnaire_data = sorted(questionnaires, key=lambda q: q["created_at"], reverse=True)[0]
    
    # Carrega documentos da empresa
    documents = load_from_json(f"documents_{company_id}.json")
    if not documents:
        documents = []
    
    # Gera o diagnóstico financeiro
    diagnostic = financial_diagnostic.generate_diagnostic(documents, questionnaire_data["responses"])
    
    # Salva o diagnóstico
    save_to_json(diagnostic, f"diagnostic_{company_id}.json")
    
    return render_template("financial_diagnostic.html", company_id=company_id, diagnostic=diagnostic)

@app.route("/company/<company_id>/valuation")
def valuation_view(company_id):
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for("login"))
    
    # Carrega diagnóstico financeiro
    diagnostic = load_from_json(f"diagnostic_{company_id}.json")
    if not diagnostic:
        flash("É necessário gerar o diagnóstico financeiro antes de calcular o valuation.", "warning")
        return redirect(url_for("company_detail", company_id=company_id))
    
    # Carrega questionários da empresa
    questionnaires = load_from_json(f"questionnaires_{company_id}.json")
    if not questionnaires or len(questionnaires) == 0:
        flash("É necessário preencher o questionário antes de calcular o valuation.", "warning")
        return redirect(url_for("company_detail", company_id=company_id))
    
    # Usa o questionário mais recente
    questionnaire_data = sorted(questionnaires, key=lambda q: q["created_at"], reverse=True)[0]
    
    # Calcula o valuation
    valuation = valuation_calculator.calculate_valuation(diagnostic, questionnaire_data["responses"])
    
    # Salva o valuation
    save_to_json(valuation, f"valuation_{company_id}.json")
    
    return render_template("valuation.html", company_id=company_id, valuation=valuation)

# Rota para servir arquivos estáticos
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

# Rota para servir arquivos enviados
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Página de erro 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Página de erro 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
