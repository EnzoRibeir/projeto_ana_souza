from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "segredo_super_seguro"

# Configuração do SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------- COLUNA DE USUÁRIO -----------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(200))
    data_nascimento = db.Column(db.String(10))
    telefone = db.Column(db.String(15))
    
# ----------------- COLUNA DE PRODUTO -----------------
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(50))
    imagem = db.Column(db.String(200))  # caminho da imagem na pasta static

# ----------------- ROTAS -----------------
@app.route("/")
def bio():
    return render_template("tela_link_bio/tela_link_bio.html")

@app.route("/home")
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

@app.route("/esqueceu a senha")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/todos_produtos")
def all_products():    
    lista_produtos = Produto.query.all()  # pega todos os produtos
    print(lista_produtos)  
    return render_template("all_products.html", produtos=lista_produtos)


@app.route('/produto/<int:id>')
def produto_detalhes(id):
    produto = Produto.query.get_or_404(id)
    lista_produtos = Produto.query.all()
    return render_template('product_details.html', produto=produto, produtos=lista_produtos)


@app.route("/carrinho")
def cart():
    return render_template("cart.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/post_blog/<int:post_id>")
def blog_post(post_id):
    return render_template("blog_post.html", post_id=post_id)

@app.route("/contato")
def contact():
    return render_template("contact.html")

@app.route("/sobre")
def lading_page():
    return render_template("lading_page/index.html")


# ----------------- INICIALIZAR BANCO -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # cria a tabela se não existir
    app.run(debug=True)
