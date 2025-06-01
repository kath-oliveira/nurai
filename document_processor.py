"""
Processamento de documentos financeiros, diagnóstico e valuation.
Implementação de cálculos reais para o MVP com dashboard visual.
"""

import os
import json
import logging
import math

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processa documentos financeiros."""
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        logger.info(f"DocumentProcessor inicializado para pasta: {upload_folder}")

    def process_document(self, file_path, document_type):
        """Processa um documento financeiro."""
        logger.info(f"Processando documento: {file_path} do tipo {document_type}")
        try:
            file_size = os.path.getsize(file_path)
            
            # Aqui seria implementada a extração real de dados do documento
            # Para o MVP, simulamos dados extraídos com base no tipo de documento
            extracted_data = self._simulate_document_extraction(file_path, document_type)
            
            return {
                "processed": True,
                "message": f"Documento '{os.path.basename(file_path)}' processado com sucesso.",
                "file_size": file_size,
                "document_type": document_type,
                "analysis_status": "Processado",
                "extracted_data": extracted_data
            }
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            return {
                "processed": False,
                "message": f"Erro ao processar documento: {e}",
                "analysis_status": "Erro",
                "extracted_data": {}
            }
    
    def _simulate_document_extraction(self, file_path, document_type):
        """Simula a extração de dados de documentos para o MVP."""
        filename = os.path.basename(file_path).lower()
        
        # Dados simulados com base no tipo de documento
        if document_type == "balanco_patrimonial":
            return {
                "ativo_total": 1500000,
                "passivo_total": 900000,
                "patrimonio_liquido": 600000,
                "ativo_circulante": 800000,
                "passivo_circulante": 500000,
                "estoques": 300000
            }
        elif document_type == "dre":
            return {
                "receita_liquida": 2000000,
                "custo_produtos": 1200000,
                "lucro_bruto": 800000,
                "despesas_operacionais": 500000,
                "lucro_operacional": 300000,
                "lucro_liquido": 250000
            }
        elif document_type == "fluxo_caixa":
            return {
                "caixa_operacional": 350000,
                "caixa_investimentos": -150000,
                "caixa_financiamentos": -50000,
                "variacao_liquida": 150000
            }
        elif document_type == "relatorio_contas":
            return {
                "contas_receber": 400000,
                "prazo_medio_recebimento": 45,
                "contas_pagar": 300000,
                "prazo_medio_pagamento": 30
            }
        else:
            # Documento genérico
            return {
                "tamanho_arquivo": os.path.getsize(file_path),
                "tipo_documento": document_type
            }

class FinancialDiagnostic:
    """Gera diagnóstico financeiro baseado nas respostas do questionário e documentos."""
    
    def generate_diagnostic(self, documents_data, questionnaire_data):
        """Gera um diagnóstico financeiro com base nas respostas do questionário e documentos."""
        logger.info("Gerando diagnóstico financeiro integrado...")
        
        # Extrai dados básicos do questionário
        try:
            # Dados financeiros do questionário
            receita_ano1 = float(questionnaire_data.get("receita_ano1", 0) or 0)
            receita_ano2 = float(questionnaire_data.get("receita_ano2", 0) or 0)
            receita_ano3 = float(questionnaire_data.get("receita_ano3", 0) or 0)
            receita_ano4 = float(questionnaire_data.get("receita_ano4", 0) or 0)
            receita_ano5 = float(questionnaire_data.get("receita_ano5", 0) or 0)
            
            custos_ano1 = float(questionnaire_data.get("custos_ano1", 0) or 0)
            custos_ano2 = float(questionnaire_data.get("custos_ano2", 0) or 0)
            custos_ano3 = float(questionnaire_data.get("custos_ano3", 0) or 0)
            custos_ano4 = float(questionnaire_data.get("custos_ano4", 0) or 0)
            custos_ano5 = float(questionnaire_data.get("custos_ano5", 0) or 0)
            
            # Dados operacionais
            num_funcionarios = int(questionnaire_data.get("num_funcionarios", 0) or 0)
            
            # Dados de mercado e modelo de negócio
            setor_atuacao = questionnaire_data.get("setor_atuacao", "")
            modelo_negocios = questionnaire_data.get("modelo_negocios", "")
            principais_produtos = questionnaire_data.get("principais_produtos", "")
            
            # Estimativa de custos fixos vs variáveis (padrão se não informado)
            custos_fixos_pct = float(questionnaire_data.get("custos_fixos_pct", 60) or 60)
            custos_variaveis_pct = 100 - custos_fixos_pct
            
            # Estimativa de TAM/SAM/SOM
            tam_valor = float(questionnaire_data.get("tam_valor", 0) or 0)
            sam_valor = float(questionnaire_data.get("sam_valor", 0) or 0)
            som_valor = float(questionnaire_data.get("som_valor", 0) or 0)
            
            # Principais riscos
            principais_riscos = questionnaire_data.get("principais_riscos", "Concorrência")
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do questionário: {e}")
            # Valores padrão em caso de erro
            receita_ano1 = receita_ano2 = receita_ano3 = receita_ano4 = receita_ano5 = 0
            custos_ano1 = custos_ano2 = custos_ano3 = custos_ano4 = custos_ano5 = 0
            num_funcionarios = 0
            setor_atuacao = modelo_negocios = principais_produtos = ""
            custos_fixos_pct = 60
            custos_variaveis_pct = 40
            tam_valor = sam_valor = som_valor = 0
            principais_riscos = "Concorrência"
        
        # Extrair e integrar dados dos documentos
        integrated_data = self._integrate_document_data(documents_data, questionnaire_data)
        
        # Calcula indicadores financeiros com dados integrados
        indicators = self._calculate_financial_indicators(questionnaire_data, integrated_data)
        
        # Calcula a pontuação geral
        scores = [
            indicators["rentabilidade"]["score"],
            indicators["liquidez"]["score"],
            indicators["endividamento"]["score"],
            indicators["eficiencia"]["score"],
            indicators["crescimento"]["score"]
        ]
        
        valid_scores = [s for s in scores if s is not None]
        overall_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0
        
        # Determina a classificação de saúde financeira
        health_status, health_color = self._get_health_status(overall_score)
        
        # Calcula KPIs para o dashboard
        kpis = self._calculate_dashboard_kpis(questionnaire_data, integrated_data)
        
        # Prepara dados para gráficos
        chart_data = self._prepare_chart_data(questionnaire_data, integrated_data)
        
        # Gera recomendações com base nos indicadores
        recommendations = self._generate_recommendations(indicators, integrated_data)
        
        # Gera o resumo com base na pontuação geral
        summary = self._generate_summary(overall_score, integrated_data)
        
        # Determina a fonte dos dados para o diagnóstico
        data_source = "Baseado apenas nas respostas do questionário"
        if integrated_data.get("has_document_data", False):
            data_source = "Baseado nas respostas do questionário e documentos enviados"
        
        # Monta o diagnóstico completo
        diagnostic = {
            "status": data_source,
            "summary": summary,
            "recommendations": recommendations,
            "indicators": indicators,
            "overall_score": overall_score,
            
            # Dados para o dashboard visual
            "dashboard": {
                "health_status": health_status,
                "health_color": health_color,
                "kpis": kpis,
                "chart_data": chart_data,
                
                # Informações de negócio
                "business_info": {
                    "modelo_negocios": modelo_negocios or "Venda direta",
                    "principais_produtos": principais_produtos or "Vendas de produtos",
                    "principais_riscos": principais_riscos,
                    "setor_atuacao": setor_atuacao,
                    "num_funcionarios": num_funcionarios,
                    "produtividade_media": kpis["produtividade_media"]
                },
                
                # Dados de mercado
                "market_data": {
                    "tam_valor": self._format_currency(tam_valor) if tam_valor > 0 else "Não informado",
                    "sam_valor": self._format_currency(sam_valor) if sam_valor > 0 else "Não informado",
                    "som_valor": self._format_currency(som_valor) if som_valor > 0 else "Não informado",
                    "tam_pct": 100,
                    "sam_pct": round((sam_valor / tam_valor) * 100 if tam_valor > 0 and sam_valor > 0 else 60),
                    "som_pct": round((som_valor / tam_valor) * 100 if tam_valor > 0 and som_valor > 0 else 30)
                },
                
                # Estrutura de custos
                "cost_structure": {
                    "fixos_pct": custos_fixos_pct,
                    "variaveis_pct": custos_variaveis_pct
                }
            }
        }
        
        return diagnostic
    
    def _integrate_document_data(self, documents_data, questionnaire_data):
        """Integra dados extraídos de documentos com dados do questionário."""
        logger.info("Integrando dados de documentos com questionário...")
        
        # Inicializa o dicionário de dados integrados
        integrated_data = {
            "has_document_data": False,
            "financial_ratios": {},
            "balance_sheet": {},
            "income_statement": {},
            "cash_flow": {}
        }
        
        # Se não houver documentos, retorna apenas os dados do questionário
        if not documents_data or len(documents_data) == 0:
            logger.info("Nenhum documento disponível para integração.")
            return integrated_data
        
        try:
            # Processa cada documento e extrai dados relevantes
            for doc in documents_data:
                if not doc.get("extracted_data"):
                    continue
                
                doc_type = doc.get("document_type", "").lower()
                extracted = doc.get("extracted_data", {})
                
                # Marca que temos dados de documentos
                integrated_data["has_document_data"] = True
                
                # Integra dados de balanço patrimonial
                if doc_type == "balanco_patrimonial":
                    integrated_data["balance_sheet"].update(extracted)
                    
                    # Calcula índices financeiros do balanço
                    if "ativo_circulante" in extracted and "passivo_circulante" in extracted and extracted["passivo_circulante"] > 0:
                        integrated_data["financial_ratios"]["liquidez_corrente"] = extracted["ativo_circulante"] / extracted["passivo_circulante"]
                    
                    if "ativo_circulante" in extracted and "estoques" in extracted and "passivo_circulante" in extracted and extracted["passivo_circulante"] > 0:
                        integrated_data["financial_ratios"]["liquidez_seca"] = (extracted["ativo_circulante"] - extracted["estoques"]) / extracted["passivo_circulante"]
                    
                    if "passivo_total" in extracted and "ativo_total" in extracted and extracted["ativo_total"] > 0:
                        integrated_data["financial_ratios"]["endividamento_geral"] = extracted["passivo_total"] / extracted["ativo_total"]
                
                # Integra dados de DRE
                elif doc_type == "dre":
                    integrated_data["income_statement"].update(extracted)
                    
                    # Calcula índices financeiros da DRE
                    if "lucro_liquido" in extracted and "receita_liquida" in extracted and extracted["receita_liquida"] > 0:
                        integrated_data["financial_ratios"]["margem_liquida"] = extracted["lucro_liquido"] / extracted["receita_liquida"]
                    
                    if "lucro_bruto" in extracted and "receita_liquida" in extracted and extracted["receita_liquida"] > 0:
                        integrated_data["financial_ratios"]["margem_bruta"] = extracted["lucro_bruto"] / extracted["receita_liquida"]
                
                # Integra dados de fluxo de caixa
                elif doc_type == "fluxo_caixa":
                    integrated_data["cash_flow"].update(extracted)
                
                # Integra dados de relatório de contas
                elif doc_type == "relatorio_contas":
                    if "prazo_medio_recebimento" in extracted:
                        integrated_data["financial_ratios"]["prazo_medio_recebimento"] = extracted["prazo_medio_recebimento"]
                    
                    if "prazo_medio_pagamento" in extracted:
                        integrated_data["financial_ratios"]["prazo_medio_pagamento"] = extracted["prazo_medio_pagamento"]
            
            # Ajusta dados do questionário com base nos documentos, se necessário
            if integrated_data["has_document_data"]:
                # Se temos dados de receita da DRE, podemos ajustar a receita do ano 1
                if "receita_liquida" in integrated_data.get("income_statement", {}):
                    receita_ano1 = float(questionnaire_data.get("receita_ano1", 0) or 0)
                    receita_dre = integrated_data["income_statement"]["receita_liquida"]
                    
                    # Se a diferença for significativa, usamos a média ou o valor da DRE
                    if receita_ano1 > 0:
                        if abs(receita_ano1 - receita_dre) / receita_ano1 > 0.2:  # Diferença > 20%
                            integrated_data["adjusted_revenue"] = (receita_ano1 + receita_dre) / 2
                        else:
                            integrated_data["adjusted_revenue"] = receita_ano1
                    else:
                        integrated_data["adjusted_revenue"] = receita_dre
                
                # Se temos dados de custos da DRE, podemos ajustar os custos do ano 1
                if "custo_produtos" in integrated_data.get("income_statement", {}):
                    custos_ano1 = float(questionnaire_data.get("custos_ano1", 0) or 0)
                    custos_dre = integrated_data["income_statement"]["custo_produtos"]
                    
                    # Se a diferença for significativa, usamos a média ou o valor da DRE
                    if custos_ano1 > 0:
                        if abs(custos_ano1 - custos_dre) / custos_ano1 > 0.2:  # Diferença > 20%
                            integrated_data["adjusted_costs"] = (custos_ano1 + custos_dre) / 2
                        else:
                            integrated_data["adjusted_costs"] = custos_ano1
                    else:
                        integrated_data["adjusted_costs"] = custos_dre
            
            logger.info(f"Integração de dados concluída. Dados de documentos disponíveis: {integrated_data['has_document_data']}")
            return integrated_data
            
        except Exception as e:
            logger.error(f"Erro ao integrar dados de documentos: {e}")
            return integrated_data
    
    def _calculate_financial_indicators(self, data, integrated_data=None):
        """Calcula todos os indicadores financeiros."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
        
        return {
            "rentabilidade": self._calculate_rentability_score(data, integrated_data),
            "liquidez": self._calculate_liquidity_score(data, integrated_data),
            "endividamento": self._calculate_debt_score(data, integrated_data),
            "eficiencia": self._calculate_efficiency_score(data, integrated_data),
            "crescimento": self._calculate_growth_score(data, integrated_data)
        }
    
    def _calculate_dashboard_kpis(self, data, integrated_data=None):
        """Calcula os KPIs principais para o dashboard."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Extrai dados relevantes, priorizando dados de documentos quando disponíveis
            if integrated_data.get("has_document_data") and "adjusted_revenue" in integrated_data:
                receita_ano1 = integrated_data["adjusted_revenue"]
            else:
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                
            if integrated_data.get("has_document_data") and "adjusted_costs" in integrated_data:
                custos_ano1 = integrated_data["adjusted_costs"]
            else:
                custos_ano1 = float(data.get("custos_ano1", 0) or 0)
                
            receita_ano5 = float(data.get("receita_ano5", 0) or 0)
            num_funcionarios = int(data.get("num_funcionarios", 0) or 0)
            
            # Calcula margem operacional
            if "margem_liquida" in integrated_data.get("financial_ratios", {}):
                # Usa margem da DRE se disponível
                margem_operacional = integrated_data["financial_ratios"]["margem_liquida"] * 100
            else:
                # Calcula com dados do questionário
                margem_operacional = round(((receita_ano1 - custos_ano1) / receita_ano1) * 100, 1) if receita_ano1 > 0 else 0
            
            # Calcula CAGR
            cagr = round((math.pow(receita_ano5 / receita_ano1, 1/4) - 1) * 100, 1) if receita_ano1 > 0 and receita_ano5 > 0 else 0
            
            # Calcula produtividade média
            produtividade_media = round(receita_ano1 / num_funcionarios) if num_funcionarios > 0 else 0
            
            # Estrutura de custos (padrão se não informado)
            custos_fixos_pct = float(data.get("custos_fixos_pct", 60) or 60)
            
            return {
                "faturamento_anual": receita_ano1,
                "faturamento_anual_formatado": self._format_currency(receita_ano1),
                "margem_operacional": margem_operacional,
                "crescimento_projetado": cagr,
                "estrutura_custos": custos_fixos_pct,
                "produtividade_media": produtividade_media,
                "produtividade_media_formatada": self._format_currency(produtividade_media)
            }
        except Exception as e:
            logger.error(f"Erro ao calcular KPIs do dashboard: {e}")
            return {
                "faturamento_anual": 0,
                "faturamento_anual_formatado": "R$ 0",
                "margem_operacional": 0,
                "crescimento_projetado": 0,
                "estrutura_custos": 60,
                "produtividade_media": 0,
                "produtividade_media_formatada": "R$ 0"
            }
    
    def _prepare_chart_data(self, data, integrated_data=None):
        """Prepara dados para os gráficos do dashboard."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Ajusta receita do ano 1 se temos dados de documentos
            if integrated_data.get("has_document_data") and "adjusted_revenue" in integrated_data:
                receita_ano1_ajustada = integrated_data["adjusted_revenue"]
            else:
                receita_ano1_ajustada = float(data.get("receita_ano1", 0) or 0)
                
            # Ajusta custos do ano 1 se temos dados de documentos
            if integrated_data.get("has_document_data") and "adjusted_costs" in integrated_data:
                custos_ano1_ajustados = integrated_data["adjusted_costs"]
            else:
                custos_ano1_ajustados = float(data.get("custos_ano1", 0) or 0)
            
            # Extrai dados de receita e custos
            receitas = [
                receita_ano1_ajustada,
                float(data.get("receita_ano2", 0) or 0),
                float(data.get("receita_ano3", 0) or 0),
                float(data.get("receita_ano4", 0) or 0),
                float(data.get("receita_ano5", 0) or 0)
            ]
            
            custos = [
                custos_ano1_ajustados,
                float(data.get("custos_ano2", 0) or 0),
                float(data.get("custos_ano3", 0) or 0),
                float(data.get("custos_ano4", 0) or 0),
                float(data.get("custos_ano5", 0) or 0)
            ]
            
            # Se não houver dados suficientes, cria dados de exemplo
            if sum(receitas) == 0:
                receitas = [1000000, 1200000, 1500000, 1750000, 2000000]
                custos = [800000, 900000, 1100000, 1200000, 1300000]
            
            # Estrutura de custos (padrão se não informado)
            custos_fixos_pct = float(data.get("custos_fixos_pct", 60) or 60)
            custos_variaveis_pct = 100 - custos_fixos_pct
            
            return {
                "receitas": receitas,
                "custos": custos,
                "anos": ["Ano 1", "Ano 2", "Ano 3", "Ano 4", "Ano 5"],
                "custos_fixos_pct": custos_fixos_pct,
                "custos_variaveis_pct": custos_variaveis_pct
            }
        except Exception as e:
            logger.error(f"Erro ao preparar dados para gráficos: {e}")
            # Dados de exemplo em caso de erro
            return {
                "receitas": [1000000, 1200000, 1500000, 1750000, 2000000],
                "custos": [800000, 900000, 1100000, 1200000, 1300000],
                "anos": ["Ano 1", "Ano 2", "Ano 3", "Ano 4", "Ano 5"],
                "custos_fixos_pct": 60,
                "custos_variaveis_pct": 40
            }
    
    def _get_health_status(self, score):
        """Determina o status de saúde financeira com base na pontuação geral."""
        if score >= 7:
            return "Saudável", "success"  # Verde
        elif score >= 4:
            return "Estável", "warning"   # Amarelo
        else:
            return "Atenção", "danger"    # Vermelho
    
    def _calculate_rentability_score(self, data, integrated_data=None):
        """Calcula o score de rentabilidade."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Verifica se temos dados de margem da DRE
            if integrated_data.get("has_document_data") and "margem_liquida" in integrated_data.get("financial_ratios", {}):
                # Usa margem da DRE
                margem_liquida = integrated_data["financial_ratios"]["margem_liquida"] * 100
                
                # Calcula score (0-10) baseado na margem líquida
                if margem_liquida >= 30:
                    score = 10
                elif margem_liquida >= 25:
                    score = 9
                elif margem_liquida >= 20:
                    score = 8
                elif margem_liquida >= 15:
                    score = 7
                elif margem_liquida >= 10:
                    score = 6
                elif margem_liquida >= 5:
                    score = 5
                else:
                    score = max(0, min(4, margem_liquida))
                
                return {
                    "score": score,
                    "margem_media": round(margem_liquida, 2),
                    "tendencia": "baseado em documentos",
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                # Usa dados do questionário
                # Extrai dados relevantes do questionário
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                receita_ano2 = float(data.get("receita_ano2", 0) or 0)
                custos_ano1 = float(data.get("custos_ano1", 0) or 0)
                custos_ano2 = float(data.get("custos_ano2", 0) or 0)
                
                # Calcula margens
                if receita_ano1 > 0:
                    margem_ano1 = (receita_ano1 - custos_ano1) / receita_ano1 * 100
                else:
                    margem_ano1 = 0
                    
                if receita_ano2 > 0:
                    margem_ano2 = (receita_ano2 - custos_ano2) / receita_ano2 * 100
                else:
                    margem_ano2 = 0
                
                # Calcula tendência
                tendencia = "estável"
                if margem_ano2 > margem_ano1 * 1.1:  # 10% de aumento
                    tendencia = "crescente"
                elif margem_ano2 < margem_ano1 * 0.9:  # 10% de queda
                    tendencia = "decrescente"
                
                # Calcula score (0-10)
                score = 0
                if margem_ano1 > 0 or margem_ano2 > 0:
                    media_margem = (margem_ano1 + margem_ano2) / 2
                    # Pontuação baseada na margem média
                    if media_margem >= 30:
                        score = 10
                    elif media_margem >= 25:
                        score = 9
                    elif media_margem >= 20:
                        score = 8
                    elif media_margem >= 15:
                        score = 7
                    elif media_margem >= 10:
                        score = 6
                    elif media_margem >= 5:
                        score = 5
                    else:
                        score = max(0, min(4, media_margem))
                    
                    # Ajuste pela tendência
                    if tendencia == "crescente":
                        score = min(10, score + 1)
                    elif tendencia == "decrescente":
                        score = max(0, score - 1)
                
                return {
                    "score": score,
                    "margem_media": round((margem_ano1 + margem_ano2) / 2, 2) if (margem_ano1 or margem_ano2) else None,
                    "tendencia": tendencia,
                    "avaliacao": self._get_evaluation_text(score)
                }
        except Exception as e:
            logger.warning(f"Erro ao calcular score de rentabilidade: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_liquidity_score(self, data, integrated_data=None):
        """Calcula o score de liquidez."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Verifica se temos dados de liquidez do balanço
            if integrated_data.get("has_document_data") and "liquidez_corrente" in integrated_data.get("financial_ratios", {}):
                # Usa índice de liquidez do balanço
                liquidez_corrente = integrated_data["financial_ratios"]["liquidez_corrente"]
                
                # Calcula score (0-10) baseado na liquidez corrente
                if liquidez_corrente >= 2.0:
                    score = 10
                elif liquidez_corrente >= 1.8:
                    score = 9
                elif liquidez_corrente >= 1.5:
                    score = 8
                elif liquidez_corrente >= 1.3:
                    score = 7
                elif liquidez_corrente >= 1.1:
                    score = 6
                elif liquidez_corrente >= 1.0:
                    score = 5
                elif liquidez_corrente >= 0.8:
                    score = 4
                elif liquidez_corrente >= 0.6:
                    score = 3
                elif liquidez_corrente >= 0.4:
                    score = 2
                else:
                    score = 1
                
                return {
                    "score": score,
                    "indice_liquidez": round(liquidez_corrente, 2),
                    "fonte": "balanço patrimonial",
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                # Para o MVP, usamos uma estimativa baseada na relação entre receitas e custos
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                custos_ano1 = float(data.get("custos_ano1", 0) or 0)
                
                if receita_ano1 > 0 and custos_ano1 > 0:
                    # Índice de liquidez estimado (receita/custos)
                    indice_liquidez = receita_ano1 / custos_ano1
                    
                    # Calcula score (0-10)
                    if indice_liquidez >= 2.0:
                        score = 10
                    elif indice_liquidez >= 1.8:
                        score = 9
                    elif indice_liquidez >= 1.5:
                        score = 8
                    elif indice_liquidez >= 1.3:
                        score = 7
                    elif indice_liquidez >= 1.1:
                        score = 6
                    elif indice_liquidez >= 1.0:
                        score = 5
                    elif indice_liquidez >= 0.8:
                        score = 4
                    elif indice_liquidez >= 0.6:
                        score = 3
                    elif indice_liquidez >= 0.4:
                        score = 2
                    else:
                        score = 1
                    
                    return {
                        "score": score,
                        "indice_liquidez": round(indice_liquidez, 2),
                        "fonte": "estimativa baseada em receitas/custos",
                        "avaliacao": self._get_evaluation_text(score)
                    }
                else:
                    return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de liquidez: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_debt_score(self, data, integrated_data=None):
        """Calcula o score de endividamento."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Verifica se temos dados de endividamento do balanço
            if integrated_data.get("has_document_data") and "endividamento_geral" in integrated_data.get("financial_ratios", {}):
                # Usa índice de endividamento do balanço
                endividamento_geral = integrated_data["financial_ratios"]["endividamento_geral"]
                
                # Calcula score (0-10) baseado no endividamento geral
                if endividamento_geral <= 0.3:
                    score = 10
                elif endividamento_geral <= 0.4:
                    score = 9
                elif endividamento_geral <= 0.5:
                    score = 8
                elif endividamento_geral <= 0.6:
                    score = 7
                elif endividamento_geral <= 0.7:
                    score = 6
                elif endividamento_geral <= 0.8:
                    score = 5
                elif endividamento_geral <= 0.9:
                    score = 4
                elif endividamento_geral <= 1.0:
                    score = 3
                elif endividamento_geral <= 1.2:
                    score = 2
                else:
                    score = 1
                
                return {
                    "score": score,
                    "indice_endividamento": round(endividamento_geral * 100, 2),
                    "fonte": "balanço patrimonial",
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                # Para o MVP, usamos uma estimativa baseada no crescimento projetado
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                receita_ano2 = float(data.get("receita_ano2", 0) or 0)
                receita_ano3 = float(data.get("receita_ano3", 0) or 0)
                
                if receita_ano1 > 0 and receita_ano2 > 0 and receita_ano3 > 0:
                    # Calcula taxas de crescimento
                    taxa_crescimento_ano2 = (receita_ano2 - receita_ano1) / receita_ano1
                    taxa_crescimento_ano3 = (receita_ano3 - receita_ano2) / receita_ano2
                    
                    # Se o crescimento for muito agressivo, pode indicar alto endividamento
                    media_crescimento = (taxa_crescimento_ano2 + taxa_crescimento_ano3) / 2
                    
                    # Calcula score (0-10) - crescimento muito alto pode indicar risco de endividamento
                    if media_crescimento <= 0.2:  # Crescimento sustentável
                        score = 8
                    elif media_crescimento <= 0.5:  # Crescimento acelerado mas ainda gerenciável
                        score = 6
                    elif media_crescimento <= 1.0:  # Crescimento muito rápido, possível risco
                        score = 4
                    else:  # Crescimento extremamente agressivo, alto risco
                        score = 2
                    
                    return {
                        "score": score,
                        "taxa_crescimento_media": round(media_crescimento * 100, 2),
                        "avaliacao": self._get_evaluation_text(score)
                    }
                else:
                    # Sem projeções futuras, assumimos score médio
                    return {"score": 5, "avaliacao": "Médio (dados limitados)"}
                
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de endividamento: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_efficiency_score(self, data, integrated_data=None):
        """Calcula o score de eficiência operacional."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Extrai dados relevantes, priorizando dados de documentos quando disponíveis
            if integrated_data.get("has_document_data") and "adjusted_revenue" in integrated_data:
                receita_ano1 = integrated_data["adjusted_revenue"]
            else:
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                
            if integrated_data.get("has_document_data") and "adjusted_costs" in integrated_data:
                custos_ano1 = integrated_data["adjusted_costs"]
            else:
                custos_ano1 = float(data.get("custos_ano1", 0) or 0)
                
            num_funcionarios = float(data.get("num_funcionarios", 0) or 0)
            
            # Verifica se temos dados de prazos médios
            has_prazo_data = False
            if integrated_data.get("has_document_data"):
                prazo_recebimento = integrated_data.get("financial_ratios", {}).get("prazo_medio_recebimento")
                prazo_pagamento = integrated_data.get("financial_ratios", {}).get("prazo_medio_pagamento")
                has_prazo_data = prazo_recebimento is not None and prazo_pagamento is not None
            
            if receita_ano1 > 0 and num_funcionarios > 0:
                # Receita por funcionário
                receita_por_funcionario = receita_ano1 / num_funcionarios
                
                # Margem operacional
                if "margem_liquida" in integrated_data.get("financial_ratios", {}):
                    margem_operacional = integrated_data["financial_ratios"]["margem_liquida"] * 100
                else:
                    margem_operacional = (receita_ano1 - custos_ano1) / receita_ano1 * 100 if receita_ano1 > 0 else 0
                
                # Calcula score (0-10) baseado na receita por funcionário e margem
                score_receita = 0
                if receita_por_funcionario >= 500000:
                    score_receita = 10
                elif receita_por_funcionario >= 400000:
                    score_receita = 9
                elif receita_por_funcionario >= 300000:
                    score_receita = 8
                elif receita_por_funcionario >= 250000:
                    score_receita = 7
                elif receita_por_funcionario >= 200000:
                    score_receita = 6
                elif receita_por_funcionario >= 150000:
                    score_receita = 5
                elif receita_por_funcionario >= 100000:
                    score_receita = 4
                elif receita_por_funcionario >= 75000:
                    score_receita = 3
                elif receita_por_funcionario >= 50000:
                    score_receita = 2
                else:
                    score_receita = 1
                
                score_margem = 0
                if margem_operacional >= 30:
                    score_margem = 10
                elif margem_operacional >= 25:
                    score_margem = 9
                elif margem_operacional >= 20:
                    score_margem = 8
                elif margem_operacional >= 15:
                    score_margem = 7
                elif margem_operacional >= 10:
                    score_margem = 6
                elif margem_operacional >= 5:
                    score_margem = 5
                else:
                    score_margem = max(0, min(4, margem_operacional))
                
                # Score adicional para ciclo financeiro, se disponível
                score_ciclo = None
                if has_prazo_data:
                    ciclo_financeiro = prazo_recebimento - prazo_pagamento
                    if ciclo_financeiro <= 0:
                        score_ciclo = 10  # Excelente: recebe antes de pagar
                    elif ciclo_financeiro <= 15:
                        score_ciclo = 8
                    elif ciclo_financeiro <= 30:
                        score_ciclo = 6
                    elif ciclo_financeiro <= 45:
                        score_ciclo = 4
                    else:
                        score_ciclo = 2  # Ruim: demora muito para receber
                
                # Score final é a média dos scores disponíveis
                if score_ciclo is not None:
                    score = (score_receita + score_margem + score_ciclo) / 3
                else:
                    score = (score_receita + score_margem) / 2
                
                result = {
                    "score": round(score, 1),
                    "receita_por_funcionario": round(receita_por_funcionario, 2),
                    "margem_operacional": round(margem_operacional, 2),
                    "avaliacao": self._get_evaluation_text(score)
                }
                
                # Adiciona informações de ciclo financeiro, se disponíveis
                if has_prazo_data:
                    result["ciclo_financeiro"] = prazo_recebimento - prazo_pagamento
                    result["prazo_recebimento"] = prazo_recebimento
                    result["prazo_pagamento"] = prazo_pagamento
                
                return result
            else:
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de eficiência: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_growth_score(self, data, integrated_data=None):
        """Calcula o score de crescimento."""
        # Se não temos dados integrados, inicializa um dicionário vazio
        if integrated_data is None:
            integrated_data = {"has_document_data": False}
            
        try:
            # Extrai dados de receita projetada, priorizando dados ajustados se disponíveis
            if integrated_data.get("has_document_data") and "adjusted_revenue" in integrated_data:
                receita_ano1 = integrated_data["adjusted_revenue"]
            else:
                receita_ano1 = float(data.get("receita_ano1", 0) or 0)
                
            receita_ano2 = float(data.get("receita_ano2", 0) or 0)
            receita_ano3 = float(data.get("receita_ano3", 0) or 0)
            receita_ano4 = float(data.get("receita_ano4", 0) or 0)
            receita_ano5 = float(data.get("receita_ano5", 0) or 0)
            
            # Verifica se temos dados suficientes
            if receita_ano1 > 0 and receita_ano5 > 0:
                # Calcula CAGR (Taxa Composta de Crescimento Anual)
                cagr = (math.pow(receita_ano5 / receita_ano1, 1/4) - 1) * 100
                
                # Calcula score (0-10)
                if cagr >= 100:  # Crescimento extremamente alto (100%+ ao ano)
                    score = 10
                elif cagr >= 80:
                    score = 9
                elif cagr >= 60:
                    score = 8
                elif cagr >= 40:
                    score = 7
                elif cagr >= 30:
                    score = 6
                elif cagr >= 20:
                    score = 5
                elif cagr >= 15:
                    score = 4
                elif cagr >= 10:
                    score = 3
                elif cagr >= 5:
                    score = 2
                elif cagr > 0:
                    score = 1
                else:
                    score = 0
                
                return {
                    "score": score,
                    "cagr": round(cagr, 2),
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de crescimento: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _get_evaluation_text(self, score):
        """Retorna texto de avaliação com base no score."""
        if score is None:
            return "Dados insuficientes"
        elif score >= 9:
            return "Excelente"
        elif score >= 7:
            return "Muito Bom"
        elif score >= 5:
            return "Bom"
        elif score >= 3:
            return "Regular"
        else:
            return "Atenção"
    
    def _generate_recommendations(self, indicators, integrated_data=None):
        """Gera recomendações com base nos indicadores."""
        recommendations = []
        
        # Recomendações para rentabilidade
        if indicators["rentabilidade"]["score"] is not None:
            if indicators["rentabilidade"]["score"] < 5:
                recommendations.append("Revisar estrutura de custos e política de preços para melhorar margens.")
            if indicators["rentabilidade"].get("tendencia") == "decrescente":
                recommendations.append("Investigar causas da queda de rentabilidade e implementar ações corretivas.")
        
        # Recomendações para liquidez
        if indicators["liquidez"]["score"] is not None and indicators["liquidez"]["score"] < 5:
            recommendations.append("Melhorar gestão de capital de giro e revisar prazos de pagamento e recebimento.")
        
        # Recomendações para endividamento
        if indicators["endividamento"]["score"] is not None and indicators["endividamento"]["score"] < 5:
            recommendations.append("Revisar estratégia de crescimento para garantir sustentabilidade financeira.")
        
        # Recomendações para eficiência
        if indicators["eficiencia"]["score"] is not None and indicators["eficiencia"]["score"] < 5:
            recommendations.append("Otimizar processos operacionais e revisar produtividade por funcionário.")
            
        # Recomendações específicas baseadas em dados de documentos
        if integrated_data and integrated_data.get("has_document_data"):
            # Recomendações baseadas no ciclo financeiro
            if "prazo_medio_recebimento" in integrated_data.get("financial_ratios", {}) and "prazo_medio_pagamento" in integrated_data.get("financial_ratios", {}):
                prazo_recebimento = integrated_data["financial_ratios"]["prazo_medio_recebimento"]
                prazo_pagamento = integrated_data["financial_ratios"]["prazo_medio_pagamento"]
                ciclo_financeiro = prazo_recebimento - prazo_pagamento
                
                if ciclo_financeiro > 30:
                    recommendations.append(f"Reduzir o ciclo financeiro atual de {ciclo_financeiro} dias, negociando melhores prazos com fornecedores ou clientes.")
            
            # Recomendações baseadas na liquidez
            if "liquidez_corrente" in integrated_data.get("financial_ratios", {}) and integrated_data["financial_ratios"]["liquidez_corrente"] < 1.0:
                recommendations.append("Aumentar o capital de giro para melhorar a liquidez corrente que está abaixo do ideal.")
            
            # Recomendações baseadas no endividamento
            if "endividamento_geral" in integrated_data.get("financial_ratios", {}) and integrated_data["financial_ratios"]["endividamento_geral"] > 0.7:
                recommendations.append("Reduzir o nível de endividamento geral que está acima do recomendado.")
        
        # Recomendações gerais se não houver específicas
        if not recommendations:
            recommendations.append("Manter monitoramento constante dos indicadores financeiros.")
            recommendations.append("Considerar análise mais detalhada com dados financeiros completos.")
        
        return recommendations
    
    def _generate_summary(self, overall_score, integrated_data=None):
        """Gera um resumo com base na pontuação geral."""
        # Base do resumo pela pontuação
        if overall_score >= 8:
            base_summary = "A empresa apresenta indicadores financeiros sólidos, com boas perspectivas de crescimento sustentável."
        elif overall_score >= 6:
            base_summary = "A empresa apresenta indicadores financeiros satisfatórios, com potencial para melhorias em algumas áreas."
        elif overall_score >= 4:
            base_summary = "A empresa apresenta indicadores financeiros regulares, com necessidade de atenção em áreas específicas."
        elif overall_score > 0:
            base_summary = "A empresa apresenta indicadores financeiros preocupantes, necessitando de ações corretivas imediatas."
        else:
            return "Não foi possível gerar um diagnóstico completo devido à insuficiência de dados."
        
        # Adiciona informações sobre a fonte dos dados
        if integrated_data and integrated_data.get("has_document_data"):
            data_source = " Este diagnóstico considera tanto as respostas do questionário quanto os documentos financeiros enviados."
        else:
            data_source = " Este diagnóstico é baseado apenas nas respostas do questionário."
        
        return base_summary + data_source
    
    def _format_currency(self, value):
        """Formata um valor monetário."""
        if value is None or value == 0:
            return "R$ 0"
            
        if value >= 1_000_000_000:  # Bilhões
            return f"R$ {value/1_000_000_000:.2f} bilhões"
        elif value >= 1_000_000:  # Milhões
            return f"R$ {value/1_000_000:.2f} milhões"
        elif value >= 1_000:  # Milhares
            return f"R$ {value/1_000:.2f} mil"
        else:
            return f"R$ {value:.2f}"


class ValuationCalculator:
    """Calcula o valuation da empresa com base nas respostas do questionário."""
    
    def calculate_valuation(self, financial_data, questionnaire_data):
        """Calcula o valuation com base nas respostas do questionário."""
        logger.info("Calculando valuation...")
        
        try:
            # Extrai dados relevantes do questionário
            receita_ano1 = float(questionnaire_data.get("receita_ano1", 0) or 0)
            receita_ano2 = float(questionnaire_data.get("receita_ano2", 0) or 0)
            receita_ano3 = float(questionnaire_data.get("receita_ano3", 0) or 0)
            receita_ano4 = float(questionnaire_data.get("receita_ano4", 0) or 0)
            receita_ano5 = float(questionnaire_data.get("receita_ano5", 0) or 0)
            
            custos_ano1 = float(questionnaire_data.get("custos_ano1", 0) or 0)
            custos_ano2 = float(questionnaire_data.get("custos_ano2", 0) or 0)
            custos_ano3 = float(questionnaire_data.get("custos_ano3", 0) or 0)
            custos_ano4 = float(questionnaire_data.get("custos_ano4", 0) or 0)
            custos_ano5 = float(questionnaire_data.get("custos_ano5", 0) or 0)
            
            setor = questionnaire_data.get("setor_atuacao", "")
            modelo_negocios = questionnaire_data.get("modelo_negocios", "")
            
            # Verifica se temos dados suficientes para o cálculo
            if receita_ano5 <= 0:
                return {
                    "status": "Dados insuficientes",
                    "message": "É necessário fornecer projeções de receita para calcular o valuation."
                }
            
            # Calcula o valuation por múltiplos de receita
            valuation_multiplos = self._calculate_revenue_multiple_valuation(
                receita_ano5, setor, modelo_negocios
            )
            
            # Calcula o valuation por DCF (Fluxo de Caixa Descontado)
            valuation_dcf = self._calculate_dcf_valuation(
                [receita_ano1, receita_ano2, receita_ano3, receita_ano4, receita_ano5],
                [custos_ano1, custos_ano2, custos_ano3, custos_ano4, custos_ano5],
                setor
            )
            
            # Calcula o valuation final (média dos métodos)
            valuation_final = (valuation_multiplos + valuation_dcf) / 2
            
            # Calcula o range (±20%)
            valuation_min = valuation_final * 0.8
            valuation_max = valuation_final * 1.2
            
            # Formata os valores para exibição
            valuation_min_formatted = self._format_currency(valuation_min)
            valuation_max_formatted = self._format_currency(valuation_max)
            valuation_final_formatted = self._format_currency(valuation_final)
            
            # Prepara o resultado
            result = {
                "status": "Valuation calculado com base nas projeções financeiras",
                "valuation": valuation_final_formatted,
                "range_min": valuation_min_formatted,
                "range_max": valuation_max_formatted,
                "methods_used": ["Múltiplos de Receita", "Fluxo de Caixa Descontado (DCF)"],
                "assumptions": self._generate_assumptions(questionnaire_data),
                "details": {
                    "multiplos": self._format_currency(valuation_multiplos),
                    "dcf": self._format_currency(valuation_dcf)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao calcular valuation: {e}")
            return {
                "status": "Erro no cálculo",
                "message": f"Ocorreu um erro ao calcular o valuation: {str(e)}"
            }
    
    def _calculate_revenue_multiple_valuation(self, receita_ano5, setor, modelo_negocios):
        """Calcula o valuation baseado em múltiplos de receita."""
        # Define múltiplos por setor (valores típicos de mercado)
        multiplos_setor = {
            "Tecnologia": 5.0,
            "SaaS": 6.0,
            "Saúde": 4.0,
            "Varejo": 1.0,
            "Indústria": 1.5,
            "Serviços": 2.0,
            "Agro": 1.2,
            "Construção": 1.0,
            "Educação": 2.5,
            "Outros": 2.0
        }
        
        # Define ajustes por modelo de negócio
        ajustes_modelo = {
            "Assinatura": 1.5,
            "Venda direta": 1.0,
            "Licenciamento": 1.3,
            "Intermediação": 1.2,
            "Freemium": 1.4,
            "Outro": 1.0
        }
        
        # Obtém o múltiplo base pelo setor (ou usa o padrão)
        multiplo_base = multiplos_setor.get(setor, multiplos_setor["Outros"])
        
        # Aplica ajuste pelo modelo de negócio
        ajuste = ajustes_modelo.get(modelo_negocios, ajustes_modelo["Outro"])
        multiplo_final = multiplo_base * ajuste
        
        # Calcula o valuation
        valuation = receita_ano5 * multiplo_final
        
        return valuation
    
    def _calculate_dcf_valuation(self, receitas, custos, setor):
        """Calcula o valuation pelo método de Fluxo de Caixa Descontado."""
        # Define taxas de desconto por setor
        taxas_desconto = {
            "Tecnologia": 0.20,  # 20%
            "SaaS": 0.18,
            "Saúde": 0.15,
            "Varejo": 0.12,
            "Indústria": 0.14,
            "Serviços": 0.15,
            "Agro": 0.13,
            "Construção": 0.14,
            "Educação": 0.16,
            "Outros": 0.15
        }
        
        # Obtém a taxa de desconto (ou usa o padrão)
        taxa_desconto = taxas_desconto.get(setor, taxas_desconto["Outros"])
        
        # Calcula fluxos de caixa (simplificado: receita - custos)
        fluxos_caixa = []
        for i in range(len(receitas)):
            if i < len(custos):
                fluxo = receitas[i] - custos[i]
            else:
                # Se não temos custos para este ano, estimamos como 60% da receita
                fluxo = receitas[i] * 0.4
            fluxos_caixa.append(fluxo)
        
        # Calcula valor presente dos fluxos de caixa
        valor_presente = 0
        for i, fluxo in enumerate(fluxos_caixa):
            valor_presente += fluxo / math.pow(1 + taxa_desconto, i + 1)
        
        # Calcula valor terminal (perpetuidade com crescimento de 3%)
        taxa_crescimento_perpetuidade = 0.03
        valor_terminal = fluxos_caixa[-1] * (1 + taxa_crescimento_perpetuidade) / (taxa_desconto - taxa_crescimento_perpetuidade)
        valor_terminal_presente = valor_terminal / math.pow(1 + taxa_desconto, len(fluxos_caixa))
        
        # Valuation final é a soma do valor presente dos fluxos + valor terminal
        valuation = valor_presente + valor_terminal_presente
        
        return valuation
    
    def _generate_assumptions(self, data):
        """Gera premissas utilizadas no cálculo do valuation."""
        return [
            "Projeções de receita e custos conforme informado no questionário",
            "Taxa de crescimento na perpetuidade de 3%",
            "Múltiplos de receita ajustados por setor e modelo de negócio",
            "Horizonte de projeção de 5 anos"
        ]
    
    def _format_currency(self, value):
        """Formata um valor monetário."""
        if value is None or value == 0:
            return "R$ 0"
            
        if value >= 1_000_000_000:  # Bilhões
            return f"R$ {value/1_000_000_000:.2f} bilhões"
        elif value >= 1_000_000:  # Milhões
            return f"R$ {value/1_000_000:.2f} milhões"
        elif value >= 1_000:  # Milhares
            return f"R$ {value/1_000:.2f} mil"
        else:
            return f"R$ {value:.2f}"
