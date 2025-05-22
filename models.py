from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    companies = db.relationship('Company', backref='owner', lazy=True)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questionnaires = db.relationship('DiagnosticQuestionnaire', backref='company', lazy=True)

class DiagnosticQuestionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    status = db.Column(db.String(20), default='draft')  # draft, completed
    
    # Dados Gerais da Empresa
    nome_empresa = db.Column(db.String(120))
    cnpj = db.Column(db.String(18))
    ano_fundacao = db.Column(db.Integer)
    quantidade_socios = db.Column(db.Integer)
    quantidade_funcionarios = db.Column(db.Integer)
    faturamento_anual = db.Column(db.Float)
    setor_atuacao = db.Column(db.String(50))
    
    # Proposta de Valor e Mercado
    problema_resolve = db.Column(db.Text)
    solucao_oferece = db.Column(db.Text)
    timing_negocio = db.Column(db.Text)
    modelo_negocios = db.Column(db.String(50))
    diferenciais_competitivos = db.Column(db.Text)
    portfolio_produtos = db.Column(db.Text)
    
    # Mercado e Validação
    identificacao_mercado = db.Column(db.Text)
    potenciais_clientes_conversados = db.Column(db.Integer)
    entrevistas_stakeholders = db.Column(db.Integer)
    necessidades_clientes = db.Column(db.Text)
    solucao_portfolio_clientes = db.Column(db.Text)
    segmentos_alvo = db.Column(db.Text)
    satisfacao_atual_necessidade = db.Column(db.Text)
    
    # Estrutura e Operação
    estrutura_atual = db.Column(db.Text)
    colaboradores_por_area = db.Column(db.Text)
    competencias_experiencias = db.Column(db.Text)
    deficiencias_equipe = db.Column(db.Text)
    
    # Produto/Solução e Propriedade Intelectual
    atributos_solucao = db.Column(db.Text)
    propriedade_intelectual = db.Column(db.String(3))  # Sim/Não
    estrategia_propriedade = db.Column(db.Text)
    
    # Concorrência e Estratégia de Mercado
    concorrentes = db.Column(db.Text)
    diferenciais_concorrentes = db.Column(db.Text)
    posicionamento_mercado = db.Column(db.String(50))
    descricao_posicionamento = db.Column(db.Text)
    barreiras_entrada = db.Column(db.Text)
    riscos_mitigacoes = db.Column(db.Text)
    
    # Modelo de Negócio e Fontes de Receita
    fontes_receita = db.Column(db.Text)
    modelo_geracao_receita = db.Column(db.Text)
    
    # Projeções Financeiras
    tam_mercado_total = db.Column(db.Float)
    sam_mercado_alvo = db.Column(db.Float)
    som_mercado_alcancavel = db.Column(db.Float)
    receita_ano1 = db.Column(db.Float)
    receita_ano2 = db.Column(db.Float)
    receita_ano3 = db.Column(db.Float)
    receita_ano4 = db.Column(db.Float)
    receita_ano5 = db.Column(db.Float)
    custos_estimados = db.Column(db.Text)
    justificativa_projecoes = db.Column(db.Text)
    cronograma_financeiro = db.Column(db.Text)
    
    # Marketing, Comercial e Distribuição
    estrategias_marketing = db.Column(db.Text)
    metodos_venda = db.Column(db.Text)
    estrategia_insercao = db.Column(db.Text)
    estrategia_precificacao = db.Column(db.Text)
    estrategias_distribuicao = db.Column(db.Text)

# Modelo legado - mantido para compatibilidade
class QuestionarioResposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    empresa = db.Column(db.String(120))
    receita = db.Column(db.Float)
    lucro = db.Column(db.Float)
    crescimentoPlano = db.Column(db.Text)
    metodoValuation = db.Column(db.String(120))
    ofertasAnteriores = db.Column(db.Text)
    riscosESG = db.Column(db.Text)
    utilizaKPIs = db.Column(db.String(50))
