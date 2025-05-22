from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

from models import db, User, Company, DiagnosticQuestionnaire, QuestionarioResposta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    companies = Company.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", companies=companies)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Credenciais inválidas", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Usuário já existe", "danger")
            return render_template("register.html")
        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário criado com sucesso. Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/add-company", methods=["GET", "POST"])
@login_required
def add_company():
    if request.method == "POST":
        name = request.form["name"]
        company = Company(name=name, user_id=current_user.id)
        db.session.add(company)
        db.session.commit()
        flash("Empresa adicionada com sucesso", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_company.html")

@app.route("/company/<int:company_id>")
@login_required
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    if company.user_id != current_user.id:
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("dashboard"))
    questionnaires = DiagnosticQuestionnaire.query.filter_by(company_id=company_id).all()
    return render_template("company_detail.html", company=company, questionnaires=questionnaires)

@app.route("/company/<int:company_id>/diagnostic", methods=["GET", "POST"])
@login_required
def diagnostic_questionnaire(company_id):
    company = Company.query.get_or_404(company_id)
    if company.user_id != current_user.id:
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("dashboard"))
    
    # Verificar se já existe um questionário em rascunho
    questionnaire = DiagnosticQuestionnaire.query.filter_by(
        company_id=company_id, 
        status='draft'
    ).first()
    
    # Se não existir, criar um novo
    if not questionnaire:
        questionnaire = DiagnosticQuestionnaire(company_id=company_id)
        db.session.add(questionnaire)
        db.session.commit()
    
    # Definir a seção atual (padrão: dados_gerais)
    current_section = request.args.get('section', 'dados_gerais')
    
    # Se for POST, salvar os dados da seção atual
    if request.method == "POST":
        section = request.form.get('current_section')
        
        # Atualizar os campos com base na seção
        if section == 'dados_gerais':
            questionnaire.nome_empresa = request.form.get('nome_empresa')
            questionnaire.cnpj = request.form.get('cnpj')
            questionnaire.ano_fundacao = request.form.get('ano_fundacao', type=int)
            questionnaire.quantidade_socios = request.form.get('quantidade_socios', type=int)
            questionnaire.quantidade_funcionarios = request.form.get('quantidade_funcionarios', type=int)
            questionnaire.faturamento_anual = request.form.get('faturamento_anual', type=float)
            questionnaire.setor_atuacao = request.form.get('setor_atuacao')
            
        elif section == 'proposta_valor':
            questionnaire.problema_resolve = request.form.get('problema_resolve')
            questionnaire.solucao_oferece = request.form.get('solucao_oferece')
            questionnaire.timing_negocio = request.form.get('timing_negocio')
            questionnaire.modelo_negocios = request.form.get('modelo_negocios')
            questionnaire.diferenciais_competitivos = request.form.get('diferenciais_competitivos')
            questionnaire.portfolio_produtos = request.form.get('portfolio_produtos')
            
        elif section == 'mercado_validacao':
            questionnaire.identificacao_mercado = request.form.get('identificacao_mercado')
            questionnaire.potenciais_clientes_conversados = request.form.get('potenciais_clientes_conversados', type=int)
            questionnaire.entrevistas_stakeholders = request.form.get('entrevistas_stakeholders', type=int)
            questionnaire.necessidades_clientes = request.form.get('necessidades_clientes')
            questionnaire.solucao_portfolio_clientes = request.form.get('solucao_portfolio_clientes')
            questionnaire.segmentos_alvo = request.form.get('segmentos_alvo')
            questionnaire.satisfacao_atual_necessidade = request.form.get('satisfacao_atual_necessidade')
            
        elif section == 'estrutura_operacao':
            questionnaire.estrutura_atual = request.form.get('estrutura_atual')
            questionnaire.colaboradores_por_area = request.form.get('colaboradores_por_area')
            questionnaire.competencias_experiencias = request.form.get('competencias_experiencias')
            questionnaire.deficiencias_equipe = request.form.get('deficiencias_equipe')
            
        elif section == 'produto_solucao':
            questionnaire.atributos_solucao = request.form.get('atributos_solucao')
            questionnaire.propriedade_intelectual = request.form.get('propriedade_intelectual')
            questionnaire.estrategia_propriedade = request.form.get('estrategia_propriedade')
            
        elif section == 'concorrencia_estrategia':
            questionnaire.concorrentes = request.form.get('concorrentes')
            questionnaire.diferenciais_concorrentes = request.form.get('diferenciais_concorrentes')
            questionnaire.posicionamento_mercado = request.form.get('posicionamento_mercado')
            questionnaire.descricao_posicionamento = request.form.get('descricao_posicionamento')
            questionnaire.barreiras_entrada = request.form.get('barreiras_entrada')
            questionnaire.riscos_mitigacoes = request.form.get('riscos_mitigacoes')
            
        elif section == 'modelo_receita':
            questionnaire.fontes_receita = request.form.get('fontes_receita')
            questionnaire.modelo_geracao_receita = request.form.get('modelo_geracao_receita')
            
        elif section == 'projecoes_financeiras':
            questionnaire.tam_mercado_total = request.form.get('tam_mercado_total', type=float)
            questionnaire.sam_mercado_alvo = request.form.get('sam_mercado_alvo', type=float)
            questionnaire.som_mercado_alcancavel = request.form.get('som_mercado_alcancavel', type=float)
            questionnaire.receita_ano1 = request.form.get('receita_ano1', type=float)
            questionnaire.receita_ano2 = request.form.get('receita_ano2', type=float)
            questionnaire.receita_ano3 = request.form.get('receita_ano3', type=float)
            questionnaire.receita_ano4 = request.form.get('receita_ano4', type=float)
            questionnaire.receita_ano5 = request.form.get('receita_ano5', type=float)
            questionnaire.custos_estimados = request.form.get('custos_estimados')
            questionnaire.justificativa_projecoes = request.form.get('justificativa_projecoes')
            questionnaire.cronograma_financeiro = request.form.get('cronograma_financeiro')
            
        elif section == 'marketing_comercial':
            questionnaire.estrategias_marketing = request.form.get('estrategias_marketing')
            questionnaire.metodos_venda = request.form.get('metodos_venda')
            questionnaire.estrategia_insercao = request.form.get('estrategia_insercao')
            questionnaire.estrategia_precificacao = request.form.get('estrategia_precificacao')
            questionnaire.estrategias_distribuicao = request.form.get('estrategias_distribuicao')
            
        # Salvar as alterações
        db.session.commit()
        
        # Verificar se é para avançar, voltar ou ir para revisão
        next_action = request.form.get('next_action', 'next')
        
        if next_action == 'review':
            return redirect(url_for('review_questionnaire', company_id=company_id, questionnaire_id=questionnaire.id))
        
        # Determinar a próxima seção
        sections = ['dados_gerais', 'proposta_valor', 'mercado_validacao', 'estrutura_operacao', 
                   'produto_solucao', 'concorrencia_estrategia', 'modelo_receita', 
                   'projecoes_financeiras', 'marketing_comercial']
        
        current_index = sections.index(section)
        
        if next_action == 'next' and current_index < len(sections) - 1:
            next_section = sections[current_index + 1]
        elif next_action == 'prev' and current_index > 0:
            next_section = sections[current_index - 1]
        else:
            next_section = section
            
        flash("Dados salvos com sucesso!", "success")
        return redirect(url_for('diagnostic_questionnaire', company_id=company_id, section=next_section))
    
    return render_template("diagnostic_questionnaire.html", company=company, questionnaire=questionnaire, current_section=current_section)

@app.route("/company/<int:company_id>/questionnaire/<int:questionnaire_id>/review", methods=["GET", "POST"])
@login_required
def review_questionnaire(company_id, questionnaire_id):
    company = Company.query.get_or_404(company_id)
    questionnaire = DiagnosticQuestionnaire.query.get_or_404(questionnaire_id)
    
    if company.user_id != current_user.id:
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        # Finalizar o questionário
        questionnaire.status = 'completed'
        questionnaire.updated_at = datetime.now()
        db.session.commit()
        
        flash("Questionário finalizado com sucesso!", "success")
        return redirect(url_for('company_detail', company_id=company_id))
    
    return render_template("review_questionnaire.html", company=company, questionnaire=questionnaire)

# Rota legada - mantida para compatibilidade
@app.route("/questionario", methods=["GET", "POST"])
@login_required
def questionario():
    if request.method == "POST":
        resposta = QuestionarioResposta(
            usuario_id=current_user.id,
            empresa=request.form.get("empresa"),
            receita=request.form.get("receita", type=float),
            lucro=request.form.get("lucro", type=float),
            crescimentoPlano=request.form.get("crescimento_plano"),
            metodoValuation=request.form.get("metodo_valuation"),
            ofertasAnteriores=request.form.get("ofertas_anteriores"),
            riscosESG=request.form.get("riscos_esg"),
            utilizaKPIs=request.form.get("utiliza_kpis")
        )
        db.session.add(resposta)
        db.session.commit()
        flash("Questionário salvo com sucesso!", "success")
        return redirect(url_for("questionario"))
    return render_template("questionnaire.html")

@app.route("/criar-demo")
def criar_demo():
    user = User.query.filter_by(email="demo@demo.com").first()
    if not user:
        demo = User(email="demo@demo.com", password=generate_password_hash("demo123"))
        db.session.add(demo)
        db.session.commit()
        return "Usuário demo criado com sucesso!"
    return "Usuário demo já existe."

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
