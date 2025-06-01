# CFO as a Service - Sistema de Automação Financeira

Um sistema completo para diagnóstico financeiro e cálculo de valuation para empresas, com foco em PMEs brasileiras.

## Visão Geral

O CFO as a Service é uma plataforma que permite:

- Cadastro e autenticação de usuários
- Preenchimento de questionário financeiro
- Upload e processamento de documentos financeiros
- Geração de diagnóstico financeiro integrado
- Cálculo de valuation baseado em múltiplos métodos
- Dashboard visual com indicadores financeiros

Esta versão MVP foi desenvolvida para funcionar sem dependência de banco de dados PostgreSQL, utilizando armazenamento local em arquivos JSON para persistência de dados.

## Estrutura do Projeto

```
automacao_financeira_mvp/
├── app.py                  # Aplicativo Flask principal
├── document_processor.py   # Processamento de documentos e diagnóstico financeiro
├── questionnaire_storage.py # Template e armazenamento do questionário
├── test_diagnostic_mvp.py  # Testes automatizados para diagnóstico financeiro
├── test_results_mvp.json   # Resultados dos testes automatizados
├── build_command.sh        # Comando de build para o Render.com
├── start_command.sh        # Comando de start para o Render.com
├── data/                   # Diretório para armazenamento de dados JSON
│   └── example_data.json   # Dados de exemplo para demonstração
├── uploads/                # Diretório para armazenamento de documentos
│   └── documento_teste.pdf # Documento de exemplo para demonstração
├── static/                 # Arquivos estáticos
│   ├── css/                # Estilos CSS
│   │   └── style.css       # Estilos personalizados
│   ├── js/                 # Scripts JavaScript
│   │   └── main.js         # Scripts personalizados
│   └── img/                # Imagens
├── templates/              # Templates HTML
│   ├── base.html           # Template base
│   ├── dashboard.html      # Dashboard principal
│   ├── login.html          # Página de login
│   ├── register.html       # Página de cadastro
│   ├── questionnaire.html  # Questionário financeiro
│   ├── upload_document.html # Upload de documentos
│   ├── financial_diagnostic.html # Diagnóstico financeiro
│   ├── valuation.html      # Cálculo de valuation
│   └── error.html          # Página de erro
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo
```

## Requisitos

- Python 3.8+
- Flask 2.2.3
- Werkzeug 2.2.3
- Gunicorn 20.1.0 (para deploy)
- Bootstrap 5 (CDN)
- Chart.js (CDN)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/automacao-financeira.git
   cd automacao-financeira
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Execute o aplicativo:
   ```
   python app.py
   ```

5. Acesse o aplicativo em seu navegador:
   ```
   http://localhost:5000
   ```

6. Credenciais de demonstração:
   ```
   Email: demo@example.com
   Senha: senha123
   ```

## Funcionalidades Principais

### Autenticação de Usuários
- Cadastro de novos usuários
- Login e logout
- Gerenciamento de perfil

### Questionário Financeiro
- Coleta de informações básicas da empresa
- Dados financeiros (receitas, custos, projeções)
- Dados de mercado (TAM, SAM, SOM)

### Upload de Documentos
- Suporte para diversos tipos de documentos financeiros
- Processamento e extração de dados
- Integração com diagnóstico financeiro

### Diagnóstico Financeiro
- Análise de rentabilidade, liquidez, endividamento, eficiência e crescimento
- Integração de dados do questionário e documentos
- Recomendações personalizadas
- Dashboard visual com gráficos

### Cálculo de Valuation
- Múltiplos métodos de valuation
- Fluxo de Caixa Descontado (DCF)
- Múltiplos de receita
- Range de valuation com premissas

## Personalização

### Estilos
Os estilos CSS estão localizados em `static/css/style.css`. Você pode personalizar as cores, fontes e outros elementos visuais editando este arquivo.

### Lógica de Negócio
- `document_processor.py`: Contém a lógica de processamento de documentos, diagnóstico financeiro e cálculo de valuation.
- `questionnaire_storage.py`: Define a estrutura do questionário e funções de armazenamento.
- `app.py`: Contém as rotas e a lógica de controle do aplicativo.

## Deploy

### Deploy Local
Para executar o aplicativo localmente:
```
python app.py
```

### Deploy no Render.com
1. Crie uma conta no [Render.com](https://render.com/)
2. Crie um novo Web Service
3. Conecte ao seu repositório GitHub
4. Configure o build command: `pip install -r requirements.txt`
   - **IMPORTANTE**: Não use o comando `flask db upgrade` pois esta versão não utiliza banco de dados SQL
5. Configure o start command: `gunicorn app:app`
6. Clique em "Create Web Service"

**Alternativa usando render.yaml:**
Este projeto inclui um arquivo `render.yaml` que configura automaticamente o serviço no Render.com. Se você estiver enfrentando problemas com a configuração manual, o Render.com detectará este arquivo e usará as configurações nele definidas.

## Testes

Para executar os testes automatizados do diagnóstico financeiro:
```
python test_diagnostic_mvp.py
```

Os resultados dos testes serão exibidos no console e também salvos no arquivo `test_results_mvp.json`.

## Limitações do MVP

- Armazenamento em arquivos JSON (não recomendado para produção com muitos usuários)
- Processamento simulado de documentos (extração real de dados não implementada)
- Sem backup automático de dados
- Autenticação básica sem recuperação de senha

## Solução de Problemas

### Erro no Deploy
Se encontrar erros durante o deploy no Render.com:
1. Verifique se o comando de build não inclui `flask db upgrade`
2. Certifique-se de que todos os diretórios necessários existem no repositório
3. Verifique se o arquivo `requirements.txt` está completo e correto

### Erro de Permissão de Arquivos
Se encontrar erros de permissão ao salvar arquivos:
1. Verifique se os diretórios `data` e `uploads` existem
2. Certifique-se de que o aplicativo tem permissão para escrever nesses diretórios

## Próximos Passos

- Implementar banco de dados PostgreSQL para persistência robusta
- Adicionar extração real de dados de documentos com OCR
- Implementar recuperação de senha e autenticação de dois fatores
- Adicionar mais métodos de valuation e análises financeiras
- Implementar exportação de relatórios em PDF

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para dúvidas ou suporte, entre em contato através do GitHub ou pelo email: seu-email@exemplo.com
