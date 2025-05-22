from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class QuestionarioResposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    empresa = db.Column(db.String(120))
    receita = db.Column(db.Float)
    lucro = db.Column(db.Float)
    crescimentoPlano = db.Column(db.Text)
    metodoValuation = db.Column(db.String(120))
    ofertasAnteriores = db.Column(db.Text)
    riscosESG = db.Column(db.Text)
    utilizaKPIs = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
    return redirect(url_for("questionario"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("questionario"))
        flash("Credenciais inválidas", "danger")
    return render_template("login.html", csrf_token="")

@app.route("/questionario", methods=["GET", "POST"])
@login_required
def questionario():
    if request.method == "POST":
        resposta = QuestionarioResposta(
            usuario_id=current_user.id,
            empresa=request.form.get("empresa"),
            receita=request.form.get("receita", type=float),
            lucro=request.form.get("lucro", type=float),
            crescimentoPlano=request.form.get("crescimento_plano"),
            metodoValuation=request.form.get("metodo_valuation"),
            ofertasAnteriores=request.form.get("ofertas_anteriores"),
            riscosESG=request.form.get("riscos_esg"),
            utilizaKPIs=request.form.get("utiliza_kpis")
        )
        db.session.add(resposta)
        db.session.commit()
        flash("Questionário salvo com sucesso!", "success")
        return redirect(url_for("questionario"))
    return render_template("questionario.html")

@app.route("/criar-demo")
def criar_demo():
    user = User.query.filter_by(email="demo@demo.com").first()
    if not user:
        demo = User(email="demo@demo.com", password=generate_password_hash("demo123"))
        db.session.add(demo)
        db.session.commit()
        return "Usuário demo criado com sucesso!"
    return "Usuário demo já existe."

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Usuário já existe", "danger")
            return render_template("register.html")
        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário criado com sucesso. Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")
