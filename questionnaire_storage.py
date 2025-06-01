"""
Armazenamento e template do questionário financeiro.
Versão simplificada para MVP sem banco de dados.
"""

class QuestionnaireTemplate:
    """Classe para gerenciar o template do questionário financeiro."""
    
    @staticmethod
    def get_template():
        """Retorna o template do questionário financeiro."""
        return {
            "title": "Questionário de Diagnóstico Financeiro",
            "description": "Este questionário ajudará a realizar um diagnóstico financeiro completo da sua empresa.",
            "sections": [
                {
                    "title": "Informações Financeiras Básicas",
                    "description": "Informe os dados financeiros básicos da sua empresa.",
                    "questions": [
                        {
                            "id": "receita_ano1",
                            "type": "number",
                            "label": "Receita total no último ano (R$)",
                            "placeholder": "Ex: 1000000",
                            "required": True
                        },
                        {
                            "id": "receita_ano2",
                            "type": "number",
                            "label": "Receita total projetada para este ano (R$)",
                            "placeholder": "Ex: 1200000",
                            "required": False
                        },
                        {
                            "id": "receita_ano3",
                            "type": "number",
                            "label": "Receita total projetada para o próximo ano (R$)",
                            "placeholder": "Ex: 1500000",
                            "required": False
                        },
                        {
                            "id": "receita_ano4",
                            "type": "number",
                            "label": "Receita total projetada para daqui a 2 anos (R$)",
                            "placeholder": "Ex: 1800000",
                            "required": False
                        },
                        {
                            "id": "receita_ano5",
                            "type": "number",
                            "label": "Receita total projetada para daqui a 3 anos (R$)",
                            "placeholder": "Ex: 2200000",
                            "required": False
                        },
                        {
                            "id": "custos_ano1",
                            "type": "number",
                            "label": "Custos totais no último ano (R$)",
                            "placeholder": "Ex: 700000",
                            "required": True
                        },
                        {
                            "id": "custos_ano2",
                            "type": "number",
                            "label": "Custos totais projetados para este ano (R$)",
                            "placeholder": "Ex: 800000",
                            "required": False
                        },
                        {
                            "id": "custos_ano3",
                            "type": "number",
                            "label": "Custos totais projetados para o próximo ano (R$)",
                            "placeholder": "Ex: 1000000",
                            "required": False
                        },
                        {
                            "id": "custos_ano4",
                            "type": "number",
                            "label": "Custos totais projetados para daqui a 2 anos (R$)",
                            "placeholder": "Ex: 1200000",
                            "required": False
                        },
                        {
                            "id": "custos_ano5",
                            "type": "number",
                            "label": "Custos totais projetados para daqui a 3 anos (R$)",
                            "placeholder": "Ex: 1400000",
                            "required": False
                        },
                        {
                            "id": "custos_fixos_pct",
                            "type": "number",
                            "label": "Percentual de custos fixos (%)",
                            "placeholder": "Ex: 60",
                            "required": False
                        }
                    ]
                },
                {
                    "title": "Informações Operacionais",
                    "description": "Informe os dados operacionais da sua empresa.",
                    "questions": [
                        {
                            "id": "num_funcionarios",
                            "type": "number",
                            "label": "Número de funcionários",
                            "placeholder": "Ex: 10",
                            "required": True
                        },
                        {
                            "id": "setor_atuacao",
                            "type": "select",
                            "label": "Setor de atuação",
                            "options": [
                                {"value": "Tecnologia", "label": "Tecnologia"},
                                {"value": "SaaS", "label": "SaaS"},
                                {"value": "Saúde", "label": "Saúde"},
                                {"value": "Varejo", "label": "Varejo"},
                                {"value": "Indústria", "label": "Indústria"},
                                {"value": "Serviços", "label": "Serviços"},
                                {"value": "Agro", "label": "Agronegócio"},
                                {"value": "Construção", "label": "Construção"},
                                {"value": "Educação", "label": "Educação"},
                                {"value": "Outros", "label": "Outros"}
                            ],
                            "required": True
                        },
                        {
                            "id": "modelo_negocios",
                            "type": "select",
                            "label": "Modelo de negócios",
                            "options": [
                                {"value": "Assinatura", "label": "Assinatura (SaaS)"},
                                {"value": "Venda direta", "label": "Venda direta"},
                                {"value": "Licenciamento", "label": "Licenciamento"},
                                {"value": "Intermediação", "label": "Intermediação/Marketplace"},
                                {"value": "Freemium", "label": "Freemium"},
                                {"value": "Outro", "label": "Outro"}
                            ],
                            "required": True
                        },
                        {
                            "id": "principais_produtos",
                            "type": "text",
                            "label": "Principais produtos ou serviços",
                            "placeholder": "Ex: Software de gestão financeira",
                            "required": True
                        }
                    ]
                },
                {
                    "title": "Mercado e Concorrência",
                    "description": "Informe dados sobre o mercado e concorrência.",
                    "questions": [
                        {
                            "id": "tam_valor",
                            "type": "number",
                            "label": "Tamanho total do mercado - TAM (R$)",
                            "placeholder": "Ex: 1000000000",
                            "required": False
                        },
                        {
                            "id": "sam_valor",
                            "type": "number",
                            "label": "Mercado disponível - SAM (R$)",
                            "placeholder": "Ex: 500000000",
                            "required": False
                        },
                        {
                            "id": "som_valor",
                            "type": "number",
                            "label": "Mercado acessível - SOM (R$)",
                            "placeholder": "Ex: 100000000",
                            "required": False
                        },
                        {
                            "id": "principais_riscos",
                            "type": "text",
                            "label": "Principais riscos e desafios",
                            "placeholder": "Ex: Concorrência de grandes players, mudanças regulatórias",
                            "required": False
                        }
                    ]
                }
            ]
        }
