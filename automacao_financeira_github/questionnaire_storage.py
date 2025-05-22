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
            # Template básico de fallback
            return {
                "sections": [
                    {
                        "id": "info_gerais",
                        "title": "Informações Gerais",
                        "questions": [
                            {"id": "nome_empresa", "label": "Nome da Empresa", "type": "text"},
                            {"id": "cnpj", "label": "CNPJ", "type": "text"}
                        ]
                    }
                    # Adicione mais seções e perguntas conforme necessário
                ]
            }

