"""
Armazenamento e gerenciamento do template do questionário financeiro.
"""

import json

class QuestionnaireTemplate:
    @staticmethod
    def get_template():
        # Template completo do questionário incorporado diretamente no código
        # Removida a dependência do arquivo questionnaire_template.json
        return {
            "sections": [
                {
                    "id": "info_gerais",
                    "title": "Informações Gerais da Empresa",
                    "questions": [
                        {"id": "nome_empresa", "label": "Nome da Empresa", "type": "text", "required": True},
                        {"id": "cnpj", "label": "CNPJ", "type": "text", "required": True},
                        {"id": "segmento_atuacao", "label": "Segmento de Atuação", "type": "text", "required": True},
                        {"id": "ano_fundacao", "label": "Ano de Fundação", "type": "number", "required": False},
                        {"id": "numero_funcionarios", "label": "Número de Funcionários", "type": "number", "required": False},
                        {"id": "website", "label": "Website da Empresa", "type": "url", "required": False}
                    ]
                },
                {
                    "id": "saude_financeira",
                    "title": "Saúde Financeira",
                    "questions": [
                        {"id": "faturamento_anual", "label": "Faturamento Anual (último exercício)", "type": "number", "prefix": "R$", "required": True},
                        {"id": "lucro_liquido_anual", "label": "Lucro Líquido Anual (último exercício)", "type": "number", "prefix": "R$", "required": True},
                        {"id": "margem_lucro", "label": "Margem de Lucro (%)", "type": "number", "suffix": "%", "required": False},
                        {"id": "endividamento_total", "label": "Endividamento Total", "type": "number", "prefix": "R$", "required": False},
                        {"id": "principais_fontes_receita", "label": "Principais Fontes de Receita", "type": "textarea", "required": False},
                        {"id": "principais_despesas", "label": "Principais Despesas", "type": "textarea", "required": False},
                        {"id": "necessidade_capital_giro", "label": "Necessidade de Capital de Giro", "type": "select", "options": ["Baixa", "Média", "Alta"], "required": False}
                    ]
                },
                {
                    "id": "operacoes_processos",
                    "title": "Operações e Processos",
                    "questions": [
                        {"id": "sistema_gestao", "label": "Utiliza algum Sistema de Gestão (ERP)? Qual?", "type": "text", "required": False},
                        {"id": "processo_contas_pagar_receber", "label": "Como é o processo de contas a pagar e receber?", "type": "textarea", "required": False},
                        {"id": "controle_estoque", "label": "Possui controle de estoque? Como é feito?", "type": "textarea", "required": False},
                        {"id": "principais_fornecedores", "label": "Principais Fornecedores", "type": "textarea", "required": False},
                        {"id": "principais_clientes", "label": "Principais Clientes", "type": "textarea", "required": False}
                    ]
                },
                {
                    "id": "estrategia_mercado",
                    "title": "Estratégia e Mercado",
                    "questions": [
                        {"id": "principais_concorrentes", "label": "Principais Concorrentes", "type": "textarea", "required": False},
                        {"id": "diferenciais_competitivos", "label": "Quais os diferenciais competitivos da empresa?", "type": "textarea", "required": False},
                        {"id": "planos_expansao", "label": "Existem planos de expansão para os próximos anos?", "type": "textarea", "required": False},
                        {"id": "maiores_desafios", "label": "Quais os maiores desafios atuais da empresa?", "type": "textarea", "required": False}
                    ]
                }
            ]
        }

