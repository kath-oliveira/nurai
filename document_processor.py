"""
Processamento de documentos financeiros, diagnóstico e valuation.
Versão com cálculos básicos usando dados do questionário.
"""

import os
import json
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funções Auxiliares de Cálculo ---
def safe_float(value, default=0.0):
    """Converte valor para float de forma segura."""
    if value is None or value == '':
        return default
    try:
        return float(str(value).replace('R$', '').replace('%', '').replace('.', '').replace(',', '.').strip())
    except (ValueError, TypeError):
        logger.warning(f"Não foi possível converter '{value}' para float. Usando default: {default}")
        return default

# --- Classes de Processamento ---

class DocumentProcessor:
    """Processa documentos financeiros (versão simulada)."""
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        logger.info(f"DocumentProcessor inicializado para pasta: {upload_folder}")

    def process_document(self, file_path, document_type):
        """Simula o processamento de um documento. NÃO MARCA COMO PROCESSADO."""
        logger.info(f"Processando (simulado) documento: {file_path} do tipo {document_type}")
        # Lógica de processamento real e atualização do status no DB seria necessária aqui
        try:
            file_size = os.path.getsize(file_path)
            return {
                "processed": True,
                "message": f"Documento '{os.path.basename(file_path)}' recebido (processamento simulado).",
                "file_size": file_size,
                "document_type": document_type,
                "analysis_status": "Pendente (Simulado)" # Status não é atualizado no DB
            }
        except Exception as e:
            logger.error(f"Erro ao simular processamento do documento {file_path}: {e}")
            return {
                "processed": False,
                "message": f"Erro ao processar documento: {e}",
                "analysis_status": "Erro"
            }

class FinancialDiagnostic:
    """Gera diagnóstico financeiro básico usando dados do questionário."""
    def generate_diagnostic(self, questionnaire_data, documents_data):
        """Gera um diagnóstico financeiro básico com base nos dados do questionário."""
        logger.info("Gerando diagnóstico financeiro com dados do questionário...")

        # Valores padrão
        diagnostic = {
            "status": "Preliminar (Baseado no Questionário)",
            "summary": "Análise inicial baseada nas respostas fornecidas.",
            "recommendations": [
                "Implementar controle de custos mais rigoroso.",
                "Analisar fluxo de caixa periodicamente."
            ],
            "indicators": {
                "rentabilidade": "Não calculado",
                "liquidez": "Não calculado",
                "endividamento": "Não calculado",
                "margem_lucro": "Não calculado"
            }
        }

        if not questionnaire_data:
            diagnostic["summary"] = "Nenhum dado do questionário disponível para análise."
            return diagnostic

        # Extrair dados do questionário com conversão segura
        faturamento = safe_float(questionnaire_data.get("faturamento_anual"))
        lucro_liquido = safe_float(questionnaire_data.get("lucro_liquido_anual"))
        endividamento_total = safe_float(questionnaire_data.get("endividamento_total"))

        # Calcular Indicadores Básicos
        summary_parts = []
        recommendations = set(diagnostic["recommendations"]) # Usar set para evitar duplicatas

        # Margem de Lucro e Rentabilidade (usando margem como proxy)
        if faturamento > 0:
            margem_lucro = (lucro_liquido / faturamento) * 100
            margem_lucro_str = f"{margem_lucro:.2f}%"
            diagnostic["indicators"]["margem_lucro"] = margem_lucro_str
            diagnostic["indicators"]["rentabilidade"] = margem_lucro_str # Usando margem como proxy

            if margem_lucro < 5:
                summary_parts.append("Margem de lucro parece baixa.")
                recommendations.add("Analisar precificação e estrutura de custos.")
            elif margem_lucro > 20:
                summary_parts.append("Margem de lucro parece saudável.")
            else:
                 summary_parts.append("Margem de lucro em nível razoável.")
        else:
            diagnostic["indicators"]["margem_lucro"] = "Faturamento não informado ou zero."
            diagnostic["indicators"]["rentabilidade"] = "Não calculado (faturamento zero ou não informado)."
            summary_parts.append("Não foi possível calcular a margem de lucro/rentabilidade (faturamento zero ou não informado).")

        # Endividamento (Corrigido: calcular se faturamento > 0)
        if faturamento > 0:
            indice_endividamento = (endividamento_total / faturamento)
            diagnostic["indicators"]["endividamento"] = f"Dívida/Faturamento: {indice_endividamento:.2f}"
            if indice_endividamento > 0.8:
                summary_parts.append("Nível de endividamento parece alto em relação ao faturamento.")
                recommendations.add("Analisar estrutura de capital e renegociar dívidas se possível.")
            elif indice_endividamento < 0:
                 summary_parts.append("Crédito líquido informado (dívida negativa).")
            else:
                summary_parts.append("Nível de endividamento parece controlado.")
        else:
            diagnostic["indicators"]["endividamento"] = "Não calculado (faturamento zero ou não informado)."

        # Liquidez (Não calculável apenas com questionário)
        # Para calcular Liquidez Corrente (Ativo Circulante / Passivo Circulante) ou Seca,
        # precisaríamos desses dados, que não estão no questionário atual.
        diagnostic["indicators"]["liquidez"] = "Não calculado (dados insuficientes)"

        # Atualizar Sumário e Recomendações
        if summary_parts:
            diagnostic["summary"] = " ".join(summary_parts)
        diagnostic["recommendations"] = list(recommendations)

        # Adicionar nota sobre dados de documentos (que não são processados)
        diagnostic["summary"] += " (Análise baseada apenas no questionário. Processamento de documentos não implementado.)"

        return diagnostic

class ValuationCalculator:
    """Calcula o valuation da empresa (versão básica usando múltiplo de faturamento)."""
    def calculate_valuation(self, questionnaire_data, financial_data):
        """Simula o cálculo do valuation usando um múltiplo simples do faturamento informado."""
        logger.info("Calculando valuation básico com dados do questionário...")

        valuation = {
            "status": "Estimativa Preliminar (Múltiplo de Faturamento)",
            "range_min": "Não calculado",
            "range_max": "Não calculado",
            "methods_used": ["Múltiplo de Faturamento (Simples)"],
            "assumptions": "Assume um múltiplo de 0.8x a 1.2x sobre o faturamento anual informado.",
            "sensitivity_analysis": "Não disponível nesta versão."
        }

        if not questionnaire_data:
            valuation["status"] = "Dados insuficientes (questionário não preenchido)."
            return valuation

        faturamento = safe_float(questionnaire_data.get("faturamento_anual"))

        if faturamento > 0:
            # Usar múltiplos simples de faturamento (exemplo)
            multiplo_min = 0.8
            multiplo_max = 1.2
            val_min = faturamento * multiplo_min
            val_max = faturamento * multiplo_max
            valuation["range_min"] = f"R$ {val_min:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valuation["range_max"] = f"R$ {val_max:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valuation["assumptions"] += f" Faturamento Anual Informado: R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "."
        else:
            valuation["status"] = "Estimativa Preliminar (Faturamento não informado ou zero)"
            valuation["assumptions"] = "Não foi possível calcular o valuation pois o faturamento anual não foi informado ou é zero."

        return valuation


