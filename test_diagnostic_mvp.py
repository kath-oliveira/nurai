"""
Testes para validar o cálculo do diagnóstico financeiro na versão MVP.
Este script testa a integração entre dados de documentos e questionário sem dependência de banco de dados.
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

def test_valuation_calculation():
    """Testa o cálculo de valuation."""
    logger.info("Teste 3: Cálculo de valuation")
    
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
        "setor_atuacao": "Tecnologia",
        "modelo_negocios": "Assinatura"
    }
    
    # Gera diagnóstico financeiro
    financial_diagnostic = FinancialDiagnostic()
    diagnostic = financial_diagnostic.generate_diagnostic([], questionnaire_data)
    
    # Calcula valuation
    valuation_calculator = ValuationCalculator()
    valuation = valuation_calculator.calculate_valuation(diagnostic, questionnaire_data)
    
    # Verifica se o valuation foi calculado corretamente
    assert valuation is not None, "O valuation não foi calculado"
    assert "valuation" in valuation, "O resultado não contém o campo 'valuation'"
    assert "range_min" in valuation, "O resultado não contém o campo 'range_min'"
    assert "range_max" in valuation, "O resultado não contém o campo 'range_max'"
    
    logger.info(f"Valuation: {valuation['valuation']}")
    logger.info(f"Range: {valuation['range_min']} - {valuation['range_max']}")
    logger.info("Teste 3 concluído com sucesso!")
    
    return valuation

def test_document_processing():
    """Testa o processamento de documentos."""
    logger.info("Teste 4: Processamento de documentos")
    
    # Inicializa o processador de documentos
    document_processor = DocumentProcessor("./uploads")
    
    # Simula o processamento de um documento
    result = document_processor.process_document("./uploads/documento_teste.pdf", "balanco_patrimonial")
    
    # Verifica se o processamento foi realizado corretamente
    assert result is not None, "O resultado do processamento não foi gerado"
    assert "processed" in result, "O resultado não contém o campo 'processed'"
    assert result["processed"] is True, "O documento não foi processado com sucesso"
    assert "extracted_data" in result, "O resultado não contém dados extraídos"
    
    # Verifica se os dados extraídos estão corretos
    extracted_data = result["extracted_data"]
    assert "ativo_total" in extracted_data, "Dados de ativo total não encontrados"
    assert "passivo_total" in extracted_data, "Dados de passivo total não encontrados"
    
    logger.info(f"Dados extraídos: {extracted_data}")
    logger.info("Teste 4 concluído com sucesso!")
    
    return result

def run_all_tests():
    """Executa todos os testes e compara os resultados."""
    logger.info("Iniciando testes do MVP sem banco de dados...")
    
    # Cria diretório de uploads se não existir
    import os
    os.makedirs("./uploads", exist_ok=True)
    
    # Cria um arquivo de teste vazio
    with open("./uploads/documento_teste.pdf", "w") as f:
        f.write("Arquivo de teste")
    
    # Executa os testes
    try:
        diagnostic_without_docs = test_diagnostic_without_documents()
        diagnostic_with_docs = test_diagnostic_with_documents()
        valuation_result = test_valuation_calculation()
        document_result = test_document_processing()
        
        # Compara os resultados
        logger.info("Comparando diagnósticos com e sem documentos:")
        logger.info(f"Pontuação sem documentos: {diagnostic_without_docs['overall_score']}")
        logger.info(f"Pontuação com documentos: {diagnostic_with_docs['overall_score']}")
        logger.info(f"Diferença: {diagnostic_with_docs['overall_score'] - diagnostic_without_docs['overall_score']}")
        
        logger.info("Todos os testes concluídos com sucesso!")
        
        # Salva os resultados em um arquivo JSON para análise detalhada
        results = {
            "without_docs": diagnostic_without_docs,
            "with_docs": diagnostic_with_docs,
            "valuation": valuation_result,
            "document_processing": document_result
        }
        
        with open("test_results_mvp.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info("Resultados dos testes salvos em test_results_mvp.json")
        return True
    except Exception as e:
        logger.error(f"Erro durante os testes: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    print(f"Testes concluídos {'com sucesso' if success else 'com falhas'}")
