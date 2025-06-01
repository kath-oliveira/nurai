"""
Testes para validar o cálculo do diagnóstico financeiro.
Este script testa a integração entre dados de documentos e questionário.
"""

import json
import logging
from document_processor import DocumentProcessor, FinancialDiagnostic, ValuationCalculator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_diagnostic_without_documents():
    """Testa o diagnóstico financeiro apenas com dados do questionário."""
    logger.info("Teste 1: Diagnóstico apenas com dados do questionário")
    
    # Dados de exemplo do questionário
    questionnaire_data = {
        "receita_ano1": 1000000,
        "receita_ano2": 1200000,
        "receita_ano3": 1500000,
        "receita_ano4": 1800000,
        "receita_ano5": 2200000,
        "custos_ano1": 700000,
        "custos_ano2": 800000,
        "custos_ano3": 1000000,
        "custos_ano4": 1200000,
        "custos_ano5": 1400000,
        "num_funcionarios": 10,
        "setor_atuacao": "Tecnologia",
        "modelo_negocios": "Assinatura",
        "principais_produtos": "Software de gestão financeira"
    }
    
    # Inicializa o diagnóstico financeiro
    financial_diagnostic = FinancialDiagnostic()
    
    # Gera o diagnóstico sem documentos
    diagnostic = financial_diagnostic.generate_diagnostic([], questionnaire_data)
    
    # Verifica se o diagnóstico foi gerado corretamente
    assert diagnostic is not None, "O diagnóstico não foi gerado"
    assert "status" in diagnostic, "O diagnóstico não contém o campo 'status'"
    assert "Baseado apenas nas respostas do questionário" in diagnostic["status"], "O status não indica que é baseado apenas no questionário"
    
    # Verifica se os indicadores foram calculados
    assert "indicators" in diagnostic, "O diagnóstico não contém indicadores"
    assert "rentabilidade" in diagnostic["indicators"], "Indicador de rentabilidade não encontrado"
    assert "liquidez" in diagnostic["indicators"], "Indicador de liquidez não encontrado"
    
    # Verifica se a pontuação geral foi calculada
    assert "overall_score" in diagnostic, "Pontuação geral não encontrada"
    
    logger.info(f"Pontuação geral: {diagnostic['overall_score']}")
    logger.info(f"Status de saúde: {diagnostic['dashboard']['health_status']}")
    logger.info("Teste 1 concluído com sucesso!")
    
    return diagnostic

def test_diagnostic_with_documents():
    """Testa o diagnóstico financeiro com dados de documentos e questionário."""
    logger.info("Teste 2: Diagnóstico com dados de documentos e questionário")
    
    # Dados de exemplo do questionário
    questionnaire_data = {
        "receita_ano1": 1000000,
        "receita_ano2": 1200000,
        "receita_ano3": 1500000,
        "receita_ano4": 1800000,
        "receita_ano5": 2200000,
        "custos_ano1": 700000,
        "custos_ano2": 800000,
        "custos_ano3": 1000000,
        "custos_ano4": 1200000,
        "custos_ano5": 1400000,
        "num_funcionarios": 10,
        "setor_atuacao": "Tecnologia",
        "modelo_negocios": "Assinatura",
        "principais_produtos": "Software de gestão financeira"
    }
    
    # Dados de exemplo de documentos
    documents_data = [
        {
            "document_type": "balanco_patrimonial",
            "extracted_data": {
                "ativo_total": 1500000,
                "passivo_total": 900000,
                "patrimonio_liquido": 600000,
                "ativo_circulante": 800000,
                "passivo_circulante": 500000,
                "estoques": 300000
            }
        },
        {
            "document_type": "dre",
            "extracted_data": {
                "receita_liquida": 1100000,  # Valor diferente do questionário
                "custo_produtos": 650000,    # Valor diferente do questionário
                "lucro_bruto": 450000,
                "despesas_operacionais": 200000,
                "lucro_operacional": 250000,
                "lucro_liquido": 200000
            }
        },
        {
            "document_type": "relatorio_contas",
            "extracted_data": {
                "contas_receber": 400000,
                "prazo_medio_recebimento": 45,
                "contas_pagar": 300000,
                "prazo_medio_pagamento": 30
            }
        }
    ]
    
    # Inicializa o diagnóstico financeiro
    financial_diagnostic = FinancialDiagnostic()
    
    # Gera o diagnóstico com documentos
    diagnostic = financial_diagnostic.generate_diagnostic(documents_data, questionnaire_data)
    
    # Verifica se o diagnóstico foi gerado corretamente
    assert diagnostic is not None, "O diagnóstico não foi gerado"
    assert "status" in diagnostic, "O diagnóstico não contém o campo 'status'"
    assert "documentos enviados" in diagnostic["status"], "O status não indica que inclui dados de documentos"
    
    # Verifica se os indicadores foram calculados
    assert "indicators" in diagnostic, "O diagnóstico não contém indicadores"
    assert "rentabilidade" in diagnostic["indicators"], "Indicador de rentabilidade não encontrado"
    assert "liquidez" in diagnostic["indicators"], "Indicador de liquidez não encontrado"
    
    # Verifica se a pontuação geral foi calculada
    assert "overall_score" in diagnostic, "Pontuação geral não encontrada"
    
    logger.info(f"Pontuação geral: {diagnostic['overall_score']}")
    logger.info(f"Status de saúde: {diagnostic['dashboard']['health_status']}")
    logger.info("Teste 2 concluído com sucesso!")
    
    return diagnostic

def test_diagnostic_with_conflicting_data():
    """Testa o diagnóstico financeiro com dados conflitantes entre documentos e questionário."""
    logger.info("Teste 3: Diagnóstico com dados conflitantes")
    
    # Dados de exemplo do questionário (valores muito diferentes dos documentos)
    questionnaire_data = {
        "receita_ano1": 2000000,  # Muito maior que o documento
        "receita_ano2": 2400000,
        "receita_ano3": 3000000,
        "receita_ano4": 3600000,
        "receita_ano5": 4400000,
        "custos_ano1": 1400000,  # Muito maior que o documento
        "custos_ano2": 1600000,
        "custos_ano3": 2000000,
        "custos_ano4": 2400000,
        "custos_ano5": 2800000,
        "num_funcionarios": 10,
        "setor_atuacao": "Tecnologia",
        "modelo_negocios": "Assinatura",
        "principais_produtos": "Software de gestão financeira"
    }
    
    # Dados de exemplo de documentos
    documents_data = [
        {
            "document_type": "dre",
            "extracted_data": {
                "receita_liquida": 1100000,  # Muito menor que o questionário
                "custo_produtos": 650000,    # Muito menor que o questionário
                "lucro_bruto": 450000,
                "despesas_operacionais": 200000,
                "lucro_operacional": 250000,
                "lucro_liquido": 200000
            }
        }
    ]
    
    # Inicializa o diagnóstico financeiro
    financial_diagnostic = FinancialDiagnostic()
    
    # Gera o diagnóstico com dados conflitantes
    diagnostic = financial_diagnostic.generate_diagnostic(documents_data, questionnaire_data)
    
    # Verifica se o diagnóstico foi gerado corretamente
    assert diagnostic is not None, "O diagnóstico não foi gerado"
    
    # Verifica se os valores foram ajustados (média entre questionário e documentos)
    assert "dashboard" in diagnostic, "Dashboard não encontrado no diagnóstico"
    assert "kpis" in diagnostic["dashboard"], "KPIs não encontrados no dashboard"
    
    # O valor do faturamento deve estar entre o valor do questionário e o do documento
    faturamento = diagnostic["dashboard"]["kpis"]["faturamento_anual"]
    assert 1100000 <= faturamento <= 2000000, f"Faturamento ajustado incorretamente: {faturamento}"
    
    logger.info(f"Faturamento ajustado: {faturamento}")
    logger.info(f"Pontuação geral: {diagnostic['overall_score']}")
    logger.info("Teste 3 concluído com sucesso!")
    
    return diagnostic

def test_diagnostic_with_missing_data():
    """Testa o diagnóstico financeiro com dados incompletos."""
    logger.info("Teste 4: Diagnóstico com dados incompletos")
    
    # Dados de exemplo do questionário (incompletos)
    questionnaire_data = {
        "receita_ano1": 1000000,
        # Faltam receitas dos anos 2-5
        "custos_ano1": 700000,
        # Faltam custos dos anos 2-5
        "num_funcionarios": 10,
        "setor_atuacao": "Tecnologia"
        # Faltam outros campos
    }
    
    # Inicializa o diagnóstico financeiro
    financial_diagnostic = FinancialDiagnostic()
    
    # Gera o diagnóstico com dados incompletos
    diagnostic = financial_diagnostic.generate_diagnostic([], questionnaire_data)
    
    # Verifica se o diagnóstico foi gerado mesmo com dados incompletos
    assert diagnostic is not None, "O diagnóstico não foi gerado"
    
    # Verifica se há indicadores calculados, mesmo que parcialmente
    assert "indicators" in diagnostic, "O diagnóstico não contém indicadores"
    
    # Alguns indicadores podem ser None devido à falta de dados
    logger.info(f"Indicadores calculados: {[k for k, v in diagnostic['indicators'].items() if v.get('score') is not None]}")
    logger.info(f"Pontuação geral: {diagnostic['overall_score']}")
    logger.info("Teste 4 concluído com sucesso!")
    
    return diagnostic

def compare_diagnostics(without_docs, with_docs):
    """Compara diagnósticos com e sem documentos para verificar diferenças."""
    logger.info("Comparando diagnósticos com e sem documentos:")
    
    # Compara pontuações gerais
    score_without = without_docs["overall_score"]
    score_with = with_docs["overall_score"]
    logger.info(f"Pontuação sem documentos: {score_without}")
    logger.info(f"Pontuação com documentos: {score_with}")
    logger.info(f"Diferença: {score_with - score_without}")
    
    # Compara indicadores específicos
    for indicator in ["rentabilidade", "liquidez", "endividamento", "eficiencia", "crescimento"]:
        if indicator in without_docs["indicators"] and indicator in with_docs["indicators"]:
            score_without = without_docs["indicators"][indicator].get("score")
            score_with = with_docs["indicators"][indicator].get("score")
            
            if score_without is not None and score_with is not None:
                logger.info(f"Indicador {indicator}: sem docs = {score_without}, com docs = {score_with}, diferença = {score_with - score_without}")
    
    # Verifica se há campos adicionais no diagnóstico com documentos
    for indicator in with_docs["indicators"]:
        for field in with_docs["indicators"][indicator]:
            if field not in without_docs["indicators"][indicator]:
                logger.info(f"Campo adicional em {indicator}: {field} = {with_docs['indicators'][indicator][field]}")

def run_all_tests():
    """Executa todos os testes e compara os resultados."""
    logger.info("Iniciando testes de diagnóstico financeiro...")
    
    # Executa os testes
    diagnostic_without_docs = test_diagnostic_without_documents()
    diagnostic_with_docs = test_diagnostic_with_documents()
    diagnostic_conflicting = test_diagnostic_with_conflicting_data()
    diagnostic_missing = test_diagnostic_with_missing_data()
    
    # Compara os resultados
    compare_diagnostics(diagnostic_without_docs, diagnostic_with_docs)
    
    logger.info("Todos os testes concluídos com sucesso!")
    
    # Retorna os resultados para análise
    return {
        "without_docs": diagnostic_without_docs,
        "with_docs": diagnostic_with_docs,
        "conflicting": diagnostic_conflicting,
        "missing": diagnostic_missing
    }

if __name__ == "__main__":
    results = run_all_tests()
    
    # Salva os resultados em um arquivo JSON para análise detalhada
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info("Resultados dos testes salvos em test_results.json")
