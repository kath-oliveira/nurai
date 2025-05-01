# --- INÍCIO: Inicialização automática do banco de dados ---
def initialize_database():
    """Verifica se as tabelas existem e as cria se necessário."""
    with app.app_context():
        inspector = inspect(db.engine)
        # Verifica se a tabela 'users' existe
        if not inspector.has_table("users"):
            app.logger.info("Tabela 'users' não encontrada. Criando todas as tabelas...")
            try:
                db.create_all()
                app.logger.info("Tabelas criadas com sucesso.")
            except Exception as e:
                app.logger.error(f"Erro ao criar tabelas: {e}")
        else:
            app.logger.info("Tabelas já existem.")

# Chama a função de inicialização uma vez ao iniciar a aplicação
initialize_database()
# --- FIM: Inicialização automática do banco de dados ---

# Inicializar gerenciador de segurança
