from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "segredo_super_seguro"

# Configuração do SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------- MODELO DE USUÁRIO -----------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(200))
    data_nascimento = db.Column(db.String(10))
    telefone = db.Column(db.String(15))

# ----------------- ROTAS -----------------
@app.route("/")
def home():
    return render_template("home_ecommerce.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        data_nascimento = request.form["data_nascimento"]
        telefone = request.form["telefone"]

        # Verifica se o usuário já existe
        if Usuario.query.filter_by(email=email).first():
            return "Email já cadastrado!"

        # Criptografa a senha
        hash_senha = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=hash_senha, data_nascimento=data_nascimento, telefone=telefone)
        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario"] = usuario.nome
            return redirect(url_for("home"))
        else:
            return "Email ou senha inválidos!"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# ----------------- INICIALIZAR BANCO -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # cria a tabela se não existir
    app.run(debug=True)
