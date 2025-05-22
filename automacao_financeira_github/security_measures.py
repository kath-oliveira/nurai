"""
Implementação de medidas de segurança para o sistema de automação financeira.
Este módulo contém funções para criptografia de dados, proteção contra ataques comuns,
e configuração de autenticação segura.
"""

import os
import hashlib
import hmac
import base64
import secrets
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from cryptography.fernet import Fernet

class SecurityManager:
    """Gerenciador de segurança para o sistema de automação financeira."""
    
    def __init__(self, app=None):
        """Inicializa o gerenciador de segurança."""
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Configura o gerenciador de segurança para a aplicação Flask."""
        self.app = app
        
        # Gerar chave secreta se não existir
        if not app.secret_key:
            app.secret_key = secrets.token_hex(32)
        
        # Configurar chave para criptografia de dados
        if not app.config.get('ENCRYPTION_KEY'):
            app.config['ENCRYPTION_KEY'] = base64.urlsafe_b64encode(os.urandom(32))
        
        # Configurar chave para JWT
        if not app.config.get('JWT_SECRET_KEY'):
            app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
        
        # Configurar tempo de expiração do JWT (1 dia por padrão)
        if not app.config.get('JWT_EXPIRATION_DELTA'):
            app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)
        
        # Configurar CSRF protection
        if not app.config.get('CSRF_SECRET_KEY'):
            app.config['CSRF_SECRET_KEY'] = secrets.token_hex(32)
        
        # Inicializar o objeto Fernet para criptografia
        self.fernet = Fernet(app.config['ENCRYPTION_KEY'])
        
        # Configurar headers de segurança
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;"
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            return response
    
    def encrypt_data(self, data):
        """Criptografa dados sensíveis."""
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.fernet.encrypt(data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        """Descriptografa dados criptografados."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        decrypted_data = self.fernet.decrypt(encrypted_data).decode('utf-8')
        try:
            return json.loads(decrypted_data)
        except json.JSONDecodeError:
            return decrypted_data
    
    def generate_csrf_token(self):
        """Gera um token CSRF."""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']
    
    def validate_csrf_token(self, token):
        """Valida um token CSRF."""
        if not token or token != session.get('csrf_token'):
            return False
        return True
    
    def generate_jwt_token(self, user_id, additional_claims=None):
        """Gera um token JWT para autenticação."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.app.config['JWT_EXPIRATION_DELTA'],
            'iat': datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(
            payload,
            self.app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
    
    def decode_jwt_token(self, token):
        """Decodifica e valida um token JWT."""
        try:
            payload = jwt.decode(
                token,
                self.app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def hash_password(self, password):
        """Gera um hash seguro para senha."""
        return generate_password_hash(password)
    
    def check_password(self, password_hash, password):
        """Verifica se a senha corresponde ao hash."""
        return check_password_hash(password_hash, password)
    
    def sanitize_input(self, input_data):
        """Sanitiza entrada de usuário para prevenir XSS."""
        if isinstance(input_data, str):
            # Remover tags HTML e caracteres potencialmente perigosos
            import html
            return html.escape(input_data)
        elif isinstance(input_data, dict):
            return {k: self.sanitize_input(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        return input_data

# Decoradores para proteção de rotas

def jwt_required(f):
    """Decorador para exigir autenticação JWT em rotas."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Verificar se o token está no header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Verificar se o token está nos cookies
        if not token:
            token = request.cookies.get('jwt_token')
        
        if not token:
            return jsonify({'message': 'Token de autenticação ausente'}), 401
        
        # Decodificar e validar o token
        security_manager = current_app.security_manager
        payload = security_manager.decode_jwt_token(token)
        
        if not payload:
            return jsonify({'message': 'Token de autenticação inválido ou expirado'}), 401
        
        # Adicionar o ID do usuário ao contexto da requisição
        request.user_id = payload['user_id']
        
        return f(*args, **kwargs)
    
    return decorated_function

def csrf_protected(f):
    """Decorador para proteção CSRF em rotas POST/PUT/DELETE."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            
            security_manager = current_app.security_manager
            if not security_manager.validate_csrf_token(token):
                return jsonify({'message': 'CSRF token inválido'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(max_requests=100, window=60):
    """Decorador para limitar taxa de requisições."""
    def decorator(f):
        # Dicionário para armazenar contadores de requisições por IP
        request_counts = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obter IP do cliente
            ip = request.remote_addr
            
            # Inicializar contador para este IP se não existir
            if ip not in request_counts:
                request_counts[ip] = {'count': 0, 'reset_time': datetime.utcnow() + timedelta(seconds=window)}
            
            # Resetar contador se o tempo expirou
            if datetime.utcnow() >= request_counts[ip]['reset_time']:
                request_counts[ip] = {'count': 0, 'reset_time': datetime.utcnow() + timedelta(seconds=window)}
            
            # Incrementar contador
            request_counts[ip]['count'] += 1
            
            # Verificar se excedeu o limite
            if request_counts[ip]['count'] > max_requests:
                return jsonify({'message': 'Limite de requisições excedido. Tente novamente mais tarde.'}), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

# Funções para configuração de segurança no Heroku

def configure_heroku_security(app):
    """Configura medidas de segurança específicas para o Heroku."""
    # Forçar HTTPS
    @app.before_request
    def force_https():
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    # Configurar variáveis de ambiente seguras
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.secret_key)
    app.config['ENCRYPTION_KEY'] = os.environ.get('ENCRYPTION_KEY', app.config['ENCRYPTION_KEY'])
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['JWT_SECRET_KEY'])
    
    # Configurar sessão segura
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configurar tempo de expiração da sessão (1 hora)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    
    return app

# Função para sanitização de consultas SQL

def sanitize_sql_query(query, params):
    """Sanitiza consultas SQL para prevenir injeção SQL."""
    # Esta função é apenas um wrapper para lembrar que devemos sempre usar
    # consultas parametrizadas. O SQLite e outros drivers já fazem a sanitização.
    return query, params
