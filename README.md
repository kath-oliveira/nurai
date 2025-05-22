# Formulário de Diagnóstico Financeiro

Este documento descreve as modificações realizadas na aplicação para implementar o formulário de diagnóstico financeiro estruturado conforme as especificações.

## Modificações Realizadas

### 1. Modelo de Dados
- Criado novo modelo `DiagnosticQuestionnaire` com todos os campos necessários para as 9 seções do formulário
- Implementados relacionamentos com os modelos existentes
- Mantido o modelo legado `QuestionarioResposta` para compatibilidade

### 2. Backend
- Implementadas novas rotas para o formulário multi-etapas
- Adicionada lógica para processamento de cada seção do formulário
- Criada funcionalidade de revisão de dados antes da finalização
- Implementada validação de dados no servidor

### 3. Frontend
- Criado template para o formulário multi-etapas (wizard)
- Implementadas as 9 seções conforme especificações:
  - Dados Gerais da Empresa
  - Proposta de Valor e Mercado
  - Mercado e Validação
  - Estrutura e Operação
  - Produto/Solução e Propriedade Intelectual
  - Concorrência e Estratégia de Mercado
  - Modelo de Negócio e Fontes de Receita
  - Projeções Financeiras
  - Marketing, Comercial e Distribuição
- Criada interface para revisão de dados
- Implementada navegação entre etapas
- Adicionada validação de formulário no cliente

### 4. Estilos e Scripts
- Adicionados estilos CSS para o formulário multi-etapas
- Implementados scripts JavaScript para validação e interatividade

## Arquivos Modificados
- `models.py` - Novo arquivo com os modelos de dados
- `app.py` - Modificado para incluir as novas rotas e funcionalidades
- `templates/diagnostic_questionnaire.html` - Novo template para o formulário multi-etapas
- `templates/review_questionnaire.html` - Novo template para a revisão de dados
- `static/css/style.css` - Estilos para o formulário
- `static/js/diagnostic.js` - Scripts para validação e interatividade

## Como Usar
1. Acesse o dashboard da aplicação
2. Selecione uma empresa ou adicione uma nova
3. Clique em "Iniciar Diagnóstico Financeiro"
4. Preencha as 9 seções do formulário, navegando com os botões "Próximo" e "Anterior"
5. Revise todos os dados na tela de revisão
6. Finalize o diagnóstico

## Observações
- O formulário salva automaticamente cada seção ao avançar ou voltar
- Campos obrigatórios são marcados com asterisco (*)
- A tela de revisão mostra todos os dados preenchidos antes da finalização
