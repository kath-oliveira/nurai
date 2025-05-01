import json
import logging # Importação adicionada
from document_processor import FinancialDiagnostic, logger

# Desabilitar logs do logger importado para não poluir a saída do teste
logger.setLevel(logging.CRITICAL)

# Dados de exemplo baseados nos logs do usuário
sample_questionnaire_data = {
    'faturamento_anual': '10000000',
    'lucro_liquido_anual': '499997',
    'endividamento_total': '-3'
    # Outros campos não são usados nos cálculos atuais
}

# Instanciar a classe
diagnostic_calculator = FinancialDiagnostic()

# Gerar diagnóstico
result = diagnostic_calculator.generate_diagnostic(sample_questionnaire_data, []) # Passa lista vazia para documents_data

# Imprimir resultado formatado
print(json.dumps(result, indent=4, ensure_ascii=False))
