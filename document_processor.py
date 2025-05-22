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
            return {
                "processed": True,
                "message": f"Documento '{os.path.basename(file_path)}' recebido com sucesso.",
                "file_size": file_size,
                "document_type": document_type,
                "analysis_status": "Processado"
            }
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            return {
                "processed": False,
                "message": f"Erro ao processar documento: {e}",
                "analysis_status": "Erro"
            }

class FinancialDiagnostic:
    """Gera diagnóstico financeiro baseado nas respostas do questionário."""
    
    def generate_diagnostic(self, documents_data, questionnaire_data):
        """Gera um diagnóstico financeiro com base nas respostas do questionário."""
        logger.info("Gerando diagnóstico financeiro...")
        
        # Extrai dados básicos do questionário
        try:
            # Dados financeiros
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
        
        # Calcula indicadores financeiros
        indicators = self._calculate_financial_indicators(questionnaire_data)
        
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
        kpis = self._calculate_dashboard_kpis(questionnaire_data)
        
        # Prepara dados para gráficos
        chart_data = self._prepare_chart_data(questionnaire_data)
        
        # Gera recomendações com base nos indicadores
        recommendations = self._generate_recommendations(indicators)
        
        # Gera o resumo com base na pontuação geral
        summary = self._generate_summary(overall_score)
        
        # Monta o diagnóstico completo
        diagnostic = {
            "status": "Baseado nas respostas do questionário",
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
    
    def _calculate_financial_indicators(self, data):
        """Calcula todos os indicadores financeiros."""
        return {
            "rentabilidade": self._calculate_rentability_score(data),
            "liquidez": self._calculate_liquidity_score(data),
            "endividamento": self._calculate_debt_score(data),
            "eficiencia": self._calculate_efficiency_score(data),
            "crescimento": self._calculate_growth_score(data)
        }
    
    def _calculate_dashboard_kpis(self, data):
        """Calcula os KPIs principais para o dashboard."""
        try:
            # Extrai dados relevantes
            receita_ano1 = float(data.get("receita_ano1", 0) or 0)
            receita_ano5 = float(data.get("receita_ano5", 0) or 0)
            custos_ano1 = float(data.get("custos_ano1", 0) or 0)
            num_funcionarios = int(data.get("num_funcionarios", 0) or 0)
            
            # Calcula margem operacional
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
    
    def _prepare_chart_data(self, data):
        """Prepara dados para os gráficos do dashboard."""
        try:
            # Extrai dados de receita e custos
            receitas = [
                float(data.get("receita_ano1", 0) or 0),
                float(data.get("receita_ano2", 0) or 0),
                float(data.get("receita_ano3", 0) or 0),
                float(data.get("receita_ano4", 0) or 0),
                float(data.get("receita_ano5", 0) or 0)
            ]
            
            custos = [
                float(data.get("custos_ano1", 0) or 0),
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
    
    def _calculate_rentability_score(self, data):
        """Calcula o score de rentabilidade."""
        try:
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
    
    def _calculate_liquidity_score(self, data):
        """Calcula o score de liquidez."""
        try:
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
                elif indice_liquidez >= 0.9:
                    score = 4
                elif indice_liquidez >= 0.8:
                    score = 3
                elif indice_liquidez >= 0.7:
                    score = 2
                elif indice_liquidez >= 0.6:
                    score = 1
                else:
                    score = 0
                
                return {
                    "score": score,
                    "indice_liquidez": round(indice_liquidez, 2),
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de liquidez: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_debt_score(self, data):
        """Calcula o score de endividamento."""
        try:
            # Para o MVP, usamos uma estimativa baseada na relação entre receitas futuras e atuais
            receita_ano1 = float(data.get("receita_ano1", 0) or 0)
            receita_ano2 = float(data.get("receita_ano2", 0) or 0)
            receita_ano3 = float(data.get("receita_ano3", 0) or 0)
            
            if receita_ano1 > 0:
                # Calculamos a taxa de crescimento projetada
                if receita_ano2 > 0 and receita_ano3 > 0:
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
            else:
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de endividamento: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_efficiency_score(self, data):
        """Calcula o score de eficiência operacional."""
        try:
            # Extrai dados relevantes
            receita_ano1 = float(data.get("receita_ano1", 0) or 0)
            custos_ano1 = float(data.get("custos_ano1", 0) or 0)
            num_funcionarios = float(data.get("num_funcionarios", 0) or 0)
            
            if receita_ano1 > 0 and num_funcionarios > 0:
                # Receita por funcionário
                receita_por_funcionario = receita_ano1 / num_funcionarios
                
                # Margem operacional
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
                
                # Score final é a média dos dois
                score = (score_receita + score_margem) / 2
                
                return {
                    "score": round(score, 1),
                    "receita_por_funcionario": round(receita_por_funcionario, 2),
                    "margem_operacional": round(margem_operacional, 2),
                    "avaliacao": self._get_evaluation_text(score)
                }
            else:
                return {"score": None, "avaliacao": "Dados insuficientes para análise"}
        except Exception as e:
            logger.warning(f"Erro ao calcular score de eficiência: {e}")
            return {"score": None, "avaliacao": "Dados insuficientes para análise"}
    
    def _calculate_growth_score(self, data):
        """Calcula o score de crescimento."""
        try:
            # Extrai dados de receita projetada
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
    
    def _generate_recommendations(self, indicators):
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
        
        # Recomendações gerais se não houver específicas
        if not recommendations:
            recommendations.append("Manter monitoramento constante dos indicadores financeiros.")
            recommendations.append("Considerar análise mais detalhada com dados financeiros completos.")
        
        return recommendations
    
    def _generate_summary(self, overall_score):
        """Gera um resumo com base na pontuação geral."""
        if overall_score >= 8:
            return "A empresa apresenta indicadores financeiros sólidos, com boas perspectivas de crescimento sustentável."
        elif overall_score >= 6:
            return "A empresa apresenta indicadores financeiros satisfatórios, com potencial para melhorias em algumas áreas."
        elif overall_score >= 4:
            return "A empresa apresenta indicadores financeiros regulares, com necessidade de atenção em áreas específicas."
        elif overall_score > 0:
            return "A empresa apresenta indicadores financeiros preocupantes, necessitando de ações corretivas imediatas."
        else:
            return "Não foi possível gerar um diagnóstico completo devido à insuficiência de dados."
    
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
        
        # Calcula os fluxos de caixa para cada ano
        fluxos_caixa = []
        for i in range(len(receitas)):
            if receitas[i] > 0:
                # Estimativa simplificada: Lucro = Receita - Custos
                lucro = receitas[i] - custos[i]
                
                # Estimativa de fluxo de caixa (lucro + depreciação estimada - capex estimado)
                # Para simplificar, assumimos que depreciação = capex em média
                fluxo_caixa = lucro
                fluxos_caixa.append(fluxo_caixa)
            else:
                fluxos_caixa.append(0)
        
        # Calcula o valor presente dos fluxos de caixa
        valor_presente = 0
        for i, fluxo in enumerate(fluxos_caixa):
            valor_presente += fluxo / math.pow(1 + taxa_desconto, i + 1)
        
        # Calcula o valor terminal (perpetuidade)
        # Assumindo crescimento perpétuo de 3%
        if fluxos_caixa[-1] > 0:
            taxa_crescimento_perpetuo = 0.03
            valor_terminal = fluxos_caixa[-1] * (1 + taxa_crescimento_perpetuo) / (taxa_desconto - taxa_crescimento_perpetuo)
            valor_terminal_presente = valor_terminal / math.pow(1 + taxa_desconto, len(fluxos_caixa))
        else:
            valor_terminal_presente = 0
        
        # Valuation final é a soma do valor presente dos fluxos + valor terminal
        valuation = valor_presente + valor_terminal_presente
        
        return valuation
    
    def _format_currency(self, value):
        """Formata um valor monetário."""
        if value >= 1_000_000_000:  # Bilhões
            return f"R$ {value/1_000_000_000:.2f} bilhões"
        elif value >= 1_000_000:  # Milhões
            return f"R$ {value/1_000_000:.2f} milhões"
        else:  # Milhares
            return f"R$ {value/1_000:.2f} mil"
    
    def _generate_assumptions(self, data):
        """Gera texto com as premissas utilizadas no cálculo."""
        setor = data.get("setor_atuacao", "não especificado")
        modelo = data.get("modelo_negocios", "não especificado")
        
        assumptions = f"Valuation baseado em projeções para empresa do setor '{setor}' "
        assumptions += f"com modelo de negócios '{modelo}'. "
        
        # Adiciona informações sobre crescimento se disponíveis
        try:
            receita_ano1 = float(data.get("receita_ano1", 0) or 0)
            receita_ano5 = float(data.get("receita_ano5", 0) or 0)
            
            if receita_ano1 > 0 and receita_ano5 > 0:
                cagr = (math.pow(receita_ano5 / receita_ano1, 1/4) - 1) * 100
                assumptions += f"CAGR projetado de {cagr:.2f}% ao ano. "
        except:
            pass
        
        assumptions += "Cálculo considera múltiplos de receita e fluxo de caixa descontado."
        
        return assumptions
