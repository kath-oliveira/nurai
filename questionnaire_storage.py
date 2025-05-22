"""
Armazenamento e gerenciamento do template do questionário financeiro.
"""

import json

class QuestionnaireTemplate:
    @staticmethod
    def get_template():
        # Retorna um template básico ou carrega de um arquivo JSON se existir
        try:
            with open("questionnaire_template.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Template completo baseado nas perguntas fornecidas pelo usuário
            return {
                "sections": [
                    {
                        "id": "dados_gerais",
                        "title": "Dados Gerais da Empresa",
                        "questions": [
                            {"id": "nome_empresa", "label": "Nome da empresa", "type": "text"},
                            {"id": "cnpj", "label": "CNPJ da empresa", "type": "text"},
                            {"id": "ano_fundacao", "label": "Ano de fundação", "type": "number"},
                            {"id": "num_socios", "label": "Número de sócios", "type": "number"},
                            {"id": "num_funcionarios", "label": "Número de funcionários", "type": "number"},
                            {"id": "faturamento_anual", "label": "Faturamento anual (R$)", "type": "number"},
                            {"id": "setor_atuacao", "label": "Qual o setor de atuação?", "type": "select", 
                             "options": ["Indústria", "Varejo", "Serviços", "Tecnologia", "Agro", "Construção", "Saúde", "Educação", "Outros"]}
                        ]
                    },
                    {
                        "id": "proposta_valor",
                        "title": "Proposta de Valor",
                        "questions": [
                            {"id": "problemas_resolve", "label": "Qual(is) o(s) problema(s) que a empresa resolve?", "type": "textarea"},
                            {"id": "solucoes_oferece", "label": "Qual(is) a(s) solução(ões) que a empresa oferece?", "type": "textarea"},
                            {"id": "timing_negocio", "label": "Por que agora é o momento certo (timing) para este negócio?", "type": "textarea"},
                            {"id": "diferenciais_competitivos", "label": "Quais são os diferenciais competitivos da empresa?", "type": "textarea"},
                            {"id": "portfolio_atual", "label": "Descreva o portfólio atual de produtos/serviços.", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "validacao_mercado",
                        "title": "Validação de Mercado",
                        "questions": [
                            {"id": "identificacao_mercado", "label": "Como sua empresa identificou esse mercado?", "type": "textarea"},
                            {"id": "num_potenciais_clientes", "label": "Quantos potenciais clientes sua empresa já conversou?", "type": "number"},
                            {"id": "num_entrevistas_stakeholders", "label": "Quantas entrevistas foram realizadas com stakeholders?", "type": "number"},
                            {"id": "necessidades_clientes", "label": "Quais necessidades dos clientes serão atendidas com a sua solução?", "type": "textarea"},
                            {"id": "harmonizacao_portfolio", "label": "Como sua solução se harmoniza com o portfólio atual ou potencial dos clientes?", "type": "textarea"},
                            {"id": "segmentos_alvo", "label": "Quais são os segmentos-alvo? Caracterize-os (tamanho, faturamento, localização, nacional/internacional).", "type": "textarea"},
                            {"id": "satisfacao_atual", "label": "Como os clientes atualmente satisfazem a necessidade que sua empresa propõe atender?", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "estrutura_equipe",
                        "title": "Estrutura Operacional e Equipe",
                        "questions": [
                            {"id": "estrutura_atual", "label": "Descreva a estrutura atual da empresa (áreas, organograma).", "type": "textarea"},
                            {"id": "colaboradores_por_area", "label": "Informe o número de colaboradores/sócios por área.", "type": "textarea"},
                            {"id": "competencias_equipe", "label": "Quais são as principais competências e experiências da equipe?", "type": "textarea"},
                            {"id": "deficiencias_equipe", "label": "Existem deficiências na equipe? Como serão resolvidas?", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "produto_propriedade",
                        "title": "Produto, Solução e Propriedade Intelectual",
                        "questions": [
                            {"id": "atributos_solucao", "label": "Quais os principais atributos e características da sua solução/produto?", "type": "textarea"},
                            {"id": "permite_protecao", "label": "Sua solução permite proteção intelectual?", "type": "select", 
                             "options": ["Sim", "Não"]},
                            {"id": "estrategia_protecao", "label": "Se sim, qual a estratégia de proteção adotada?", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "concorrencia_estrategia",
                        "title": "Concorrência e Estratégia Competitiva",
                        "questions": [
                            {"id": "concorrentes", "label": "Quem são os concorrentes diretos e indiretos?", "type": "textarea"},
                            {"id": "atributos_diferenciadores", "label": "Quais atributos diferenciam sua solução em relação aos concorrentes?", "type": "textarea"},
                            {"id": "posicionamento_mercado", "label": "Qual o posicionamento atual ou pretendido da empresa no mercado?", "type": "textarea"},
                            {"id": "barreiras_entrada", "label": "Quais são as barreiras de entrada no mercado? Como a empresa pretende superá-las?", "type": "textarea"},
                            {"id": "riscos_mitigacao", "label": "Quais são os principais riscos de operação do negócio e como serão mitigados?", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "modelo_monetizacao",
                        "title": "Modelo de Negócio e Monetização",
                        "questions": [
                            {"id": "modelo_negocios", "label": "Qual é o modelo de negócios da empresa?", "type": "select", 
                             "options": ["Assinatura", "Venda direta", "Licenciamento", "Intermediação", "Freemium", "Outro"]},
                            {"id": "contribuicao_receitas", "label": "Como o modelo de negócio adotado contribui para gerar receitas da inovação?", "type": "textarea"},
                            {"id": "fontes_receita", "label": "Quais são as fontes atuais de receita?", "type": "textarea"},
                            {"id": "racionalidade_projecoes", "label": "Justifique a racionalidade das projeções de custos e receitas.", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "projecoes_financeiras",
                        "title": "Projeções Financeiras (5 Anos)",
                        "questions": [
                            {"id": "tam_mercado", "label": "Estimativa de TAM (mercado total disponível) em R$.", "type": "number"},
                            {"id": "sam_mercado", "label": "Estimativa de SAM (mercado útil disponível) em R$.", "type": "number"},
                            {"id": "som_mercado", "label": "Estimativa de SOM (mercado alcançável) em R$.", "type": "number"},
                            {"id": "receita_ano1", "label": "Receita projetada para o 1º ano.", "type": "number"},
                            {"id": "receita_ano2", "label": "Receita projetada para o 2º ano.", "type": "number"},
                            {"id": "receita_ano3", "label": "Receita projetada para o 3º ano.", "type": "number"},
                            {"id": "receita_ano4", "label": "Receita projetada para o 4º ano.", "type": "number"},
                            {"id": "receita_ano5", "label": "Receita projetada para o 5º ano.", "type": "number"},
                            {"id": "custos_ano1", "label": "Custos fixos e variáveis projetados para o 1º ano.", "type": "number"},
                            {"id": "custos_ano2", "label": "Custos fixos e variáveis projetados para o 2º ano.", "type": "number"},
                            {"id": "custos_ano3", "label": "Custos fixos e variáveis projetados para o 3º ano.", "type": "number"},
                            {"id": "custos_ano4", "label": "Custos fixos e variáveis projetados para o 4º ano.", "type": "number"},
                            {"id": "custos_ano5", "label": "Custos fixos e variáveis projetados para o 5º ano.", "type": "number"},
                            {"id": "justificativa_projecoes", "label": "Justifique as projeções de receitas e custos.", "type": "textarea"},
                            {"id": "cronograma_financeiro", "label": "Cronograma físico-financeiro resumido.", "type": "textarea"}
                        ]
                    },
                    {
                        "id": "comercial_marketing",
                        "title": "Comercial, Vendas e Marketing",
                        "questions": [
                            {"id": "estrategias_marketing", "label": "Quais as estratégias de marketing para o produto/solução?", "type": "textarea"},
                            {"id": "metodos_venda", "label": "Quais métodos de venda serão utilizados?", "type": "textarea"},
                            {"id": "estrategia_insercao", "label": "Qual é a estratégia de inserção no mercado?", "type": "textarea"},
                            {"id": "estrategia_precificacao", "label": "Qual é a estratégia de precificação?", "type": "textarea"},
                            {"id": "estrategia_distribuicao", "label": "Qual a estratégia de distribuição, assistência técnica e pós-venda?", "type": "textarea"}
                        ]
                    }
                ]
            }
