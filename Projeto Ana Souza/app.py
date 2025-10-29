from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Em processamento")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    
    # Relação com produtos do pedido
    itens = db.relationship("PedidoProduto", backref="pedido", lazy=True)
    
    usuario = db.relationship("Usuario", backref="pedidos")

    def total(self):
        """Calcula o total do pedido"""
        return sum([item.preco_unitario * item.quantidade for item in self.itens])


class PedidoProduto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Float, nullable=False)

    # Relacionamento com o produto
    produto = db.relationship("Produto")

# ----------------- COLUNA DE POST DO BLOG -----------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    subtitulo = db.Column(db.String(250))
    conteudo = db.Column(db.Text, nullable=False)
    autor = db.Column(db.String(100))
    data_publicacao = db.Column(db.String(20))
    imagem = db.Column(db.String(200))  # caminho da imagem na pasta static


# ----------------- ROTAS -----------------
@app.route("/")
def bio():
    return render_template("tela_link_bio/tela_link_bio.html")

@app.route("/home")
def home():
    lista_produtos = Produto.query.all()
    posts = Post.query.order_by(Post.id.desc()).limit(3).all()
    return render_template("home_ecommerce.html", posts=posts, produtos=lista_produtos)

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
    # Se já estiver logado, redireciona para user
    if "usuario" in session:
        return redirect(url_for("user_info"))
    
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario"] = usuario.email
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

from flask import flash  # opcional, para mensagens

# ----------------- CARRINHO DE COMPRAS -----------------
@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    produto = Produto.query.get_or_404(id)
    
    # inicializa o carrinho se não existir
    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']

    # adiciona ou incrementa a quantidade
    if str(id) in carrinho:
        carrinho[str(id)] += 1
    else:
        carrinho[str(id)] = 1

    session['carrinho'] = carrinho  # salva de volta na sessão
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    print(carrinho)
    return redirect(request.referrer or url_for('todos_produtos'))

@app.route('/carrinho')
def cart():
    carrinho = session.get('carrinho', {})
    produtos_carrinho = []

    total = 0
    for id_str, quantidade in carrinho.items():
        produto = Produto.query.get(int(id_str))
        if produto:
            subtotal = produto.preco * quantidade
            total += subtotal
            produtos_carrinho.append({
                'id': produto.id,
                'nome': produto.nome,
                'imagem': produto.imagem,
                'preco': produto.preco,
                'quantidade': quantidade,
                'subtotal': subtotal
            })

    return render_template('cart.html', produtos_carrinho=produtos_carrinho, total=total)

@app.context_processor
def inject_cart_count():
    """Deixa a quantidade de itens no carrinho disponível em todos os templates"""
    carrinho = session.get('carrinho', {})
    cart_count = sum(carrinho.values())  # soma todas as quantidades
    return dict(cart_count=cart_count)

@app.route('/remover_do_carrinho/<int:id>')
def remover_do_carrinho(id):
    carrinho = session.get('carrinho', {})
    carrinho.pop(str(id), None)
    session['carrinho'] = carrinho
    flash('Produto removido do carrinho!', 'info')
    return redirect(url_for('cart'))

@app.route('/remover_do_carrinho_nav/<int:id>')
def remover_do_carrinho_nav(id):
    carrinho = session.get('carrinho', {})
    carrinho.pop(str(id), None)
    session['carrinho'] = carrinho
    flash('Produto removido do carrinho!', 'info')
    referer = request.referrer or url_for('cart')
    return redirect(referer)
    

@app.route('/update_cart/<int:id>/<int:quantidade>', methods=['POST'])
def update_cart(id, quantidade):
    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']
    if quantidade < 1:
        # Remove do carrinho se quantidade for menor que 1
        carrinho.pop(str(id), None)
    else:
        carrinho[str(id)] = quantidade
    
    session['carrinho'] = carrinho

    # Calcula subtotal do produto e total do carrinho
    produto = Produto.query.get_or_404(id)
    subtotal = produto.preco * quantidade
    total = sum(Produto.query.get(int(pid)).preco * q for pid, q in carrinho.items())

    return {'subtotal': subtotal, 'total': total}

@app.context_processor
def inject_cart_data():
    carrinho = session.get('carrinho', {})
    produtos_carrinho = []
    total = 0

    for id_str, quantidade in carrinho.items():
        produto = Produto.query.get(int(id_str))
        if produto:
            subtotal = produto.preco * quantidade
            total += subtotal
            produtos_carrinho.append({
                'id': produto.id,
                'nome': produto.nome,
                'imagem': produto.imagem,
                'preco': produto.preco,
                'quantidade': quantidade,
                'subtotal': subtotal
            })

    return dict(produtos_carrinho=produtos_carrinho, total=total)


# ----------------- LISTA DE DESEJOS -----------------
@app.route('/add_to_wishlist/<int:id>')
def add_to_wishlist(id):
    produto = Produto.query.get_or_404(id)

    # inicializa a wishlist se não existir
    if 'wishlist' not in session:
        session['wishlist'] = []

    wishlist = session['wishlist']

    # evita duplicados
    if id not in wishlist:
        wishlist.append(id)
        flash(f'{produto.nome} foi adicionado à sua lista de desejos!', 'success')
    else:
        flash(f'{produto.nome} já está na sua lista de desejos.', 'info')

    session['wishlist'] = wishlist
    return redirect(request.referrer or url_for('todos_produtos'))


@app.route('/wishlist')
def wishlist():
    wishlist_ids = session.get('wishlist', [])
    produtos = Produto.query.filter(Produto.id.in_(wishlist_ids)).all()
    return render_template('wish_list.html', produtos=produtos)

@app.context_processor
def inject_wishlist_count():
    wishlist_count = len(session.get('wishlist', []))
    return dict(wishlist_count=wishlist_count)

@app.route('/toggle_wishlist/<int:id>')
def toggle_wishlist(id):
    produto = Produto.query.get_or_404(id)
    wishlist = session.get('wishlist', [])

    if id in wishlist:
        wishlist.remove(id)
        flash(f'{produto.nome} foi removido da sua lista de desejos.', 'info')
    else:
        wishlist.append(id)
        flash(f'{produto.nome} foi adicionado à sua lista de desejos!', 'success')

    session['wishlist'] = wishlist
    return redirect(request.referrer or url_for('todos_produtos'))


@app.route('/remover_da_wishlist/<int:id>')
def remover_da_wishlist(id):
    wishlist = session.get('wishlist', [])
    if id in wishlist:
        wishlist.remove(id)
        flash('Produto removido da lista de desejos!', 'info')

    session['wishlist'] = wishlist
    return redirect(url_for('wishlist'))


@app.route("/blog")
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()  # lista todos, do mais recente ao mais antigo
    return render_template("blog.html", posts=posts)

@app.route("/post_blog/<int:post_id>")
def blog_post(post_id):
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("post_blog.html", post=post, posts=posts)

@app.route("/contato")
def contact():
    return render_template("contact.html")

@app.route("/sobre")
def lading_page():
    return render_template("lading_page/index.html")

@app.route('/user')
def user_info():
    # Verifica se o usuário está logado
    user_email = session.get('usuario')
    if not user_email:
        return redirect(url_for('login'))
    
    # Busca o usuário no banco
    user = Usuario.query.filter_by(email=user_email).first()
    if not user:
        return redirect(url_for('login'))
    
    pedidos = Pedido.query.filter_by(usuario_id=user.id).order_by(Pedido.data.desc()).all()
    
    return render_template('user_info.html', user=user, pedidos=pedidos)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    # código para editar perfil
    return "Página de edição de perfil"

@app.route("/edit_address", methods=["GET", "POST"])
def edit_address():
    # código para editar endereço
    return "Editar endereço"

@app.route('/order/<int:id>')
def order_details(id):
    # Verifica se o usuário está logado
    user_email = session.get('usuario')
    if not user_email:
        return redirect(url_for('login'))

    # Busca o usuário no banco
    user = Usuario.query.filter_by(email=user_email).first()
    if not user:
        return redirect(url_for('login'))

    # Busca o pedido pelo ID
    pedido = Pedido.query.filter_by(id=id, usuario_id=user.id).first()
    if not pedido:
        return "Pedido não encontrado ou você não tem permissão para ver este pedido.", 404

    # Busca os produtos do pedido
    produtos_pedido = PedidoProduto.query.filter_by(pedido_id=pedido.id).all()

    return render_template('order_details.html', pedido=pedido, produtos_pedido=produtos_pedido)

# -------------------- ROTA ADMIN --------------------
@app.route("/admin")
def admin():
    aba = request.args.get("aba", "usuarios")  # padrão: 'usuarios'
    
    usuarios = Usuario.query.all()
    produtos = Produto.query.all()
    pedidos = Pedido.query.all()
    posts = Post.query.all()

    return render_template(
        "admin.html",
        aba=aba,
        usuarios=usuarios,
        produtos=produtos,
        pedidos=pedidos,
        posts=posts
    )

# -------------------- CRUD USUARIO --------------------
@app.route("/usuario/add", methods=["POST"])
def add_usuario():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]
    telefone = request.form["telefone"]
    data_nascimento = request.form["data_nascimento"]
    usuario = Usuario(nome=nome, email=email, senha=senha, telefone=telefone, data_nascimento=data_nascimento)
    db.session.add(usuario)
    db.session.commit()
    flash("Usuário adicionado!")
    return redirect(url_for("admin"))

@app.route("/usuario/edit/<int:id>", methods=["POST"])
def edit_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.nome = request.form["nome"]
        usuario.email = request.form["email"]
        usuario.senha = request.form["senha"]
        usuario.telefone = request.form["telefone"]
        usuario.data_nascimento = request.form["data_nascimento"]
        db.session.commit()
        flash("Usuário atualizado!")
    return redirect(url_for("admin"))

@app.route("/usuario/delete/<int:id>", methods=["POST"])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuário deletado!")
    return redirect(url_for("admin"))

# -------------------- CRUD PRODUTO --------------------
@app.route("/produto/add", methods=["POST"])
def add_produto():
    produto = Produto(
        nome=request.form["nome"],
        descricao=request.form["descricao"],
        preco=float(request.form["preco"]),
        quantidade_estoque=int(request.form["quantidade_estoque"]),
        cor=request.form["cor"],
        imagem=request.form["imagem"]
    )
    db.session.add(produto)
    db.session.commit()
    flash("Produto adicionado!")
    return redirect(url_for("admin"))

@app.route("/produto/edit/<int:id>", methods=["POST"])
def edit_produto(id):
    produto = Produto.query.get(id)
    if produto:
        produto.nome = request.form["nome"]
        produto.descricao = request.form["descricao"]
        produto.preco = float(request.form["preco"])
        produto.quantidade_estoque = int(request.form["quantidade_estoque"])
        produto.cor = request.form["cor"]
        produto.imagem = request.form["imagem"]
        db.session.commit()
        flash("Produto atualizado!")
    return redirect(url_for("admin"))

@app.route("/produto/delete/<int:id>", methods=["POST"])
def delete_produto(id):
    produto = Produto.query.get(id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
        flash("Produto deletado!")
    return redirect(url_for("admin"))

# -------------------- CRUD POST --------------------
@app.route("/post/add", methods=["POST"])
def add_post():
    post = Post(
        titulo=request.form["titulo"],
        subtitulo=request.form["subtitulo"],
        conteudo=request.form["conteudo"],
        autor=request.form["autor"],
        data_publicacao=request.form["data_publicacao"],
        imagem=request.form["imagem"]
    )
    db.session.add(post)
    db.session.commit()
    flash("Post adicionado!")
    return redirect(url_for("admin"))

@app.route("/post/edit/<int:id>", methods=["POST"])
def edit_post(id):
    post = Post.query.get(id)
    if post:
        post.titulo = request.form["titulo"]
        post.subtitulo = request.form["subtitulo"]
        post.conteudo = request.form["conteudo"]
        post.autor = request.form["autor"]
        post.data_publicacao = request.form["data_publicacao"]
        post.imagem = request.form["imagem"]
        db.session.commit()
        flash("Post atualizado!")
    return redirect(url_for("admin"))

@app.route("/post/delete/<int:id>", methods=["POST"])
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post deletado!")
    return redirect(url_for("admin"))

# -------------------- CRUD PEDIDO --------------------
@app.route("/pedido/add", methods=["POST"])
def add_pedido():
    usuario_id = int(request.form["usuario_id"])
    status = request.form.get("status", "Em processamento")
    pedido = Pedido(usuario_id=usuario_id, status=status)
    db.session.add(pedido)
    db.session.commit()
    flash("Pedido adicionado!")
    return redirect(url_for("admin"))

@app.route("/pedido/edit/<int:id>", methods=["POST"])
def edit_pedido(id):
    pedido = Pedido.query.get(id)
    if pedido:
        pedido.usuario_id = int(request.form["usuario_id"])
        pedido.status = request.form.get("status", "Em processamento")
        db.session.commit()
        flash("Pedido atualizado!")
    return redirect(url_for("admin"))

@app.route("/pedido/delete/<int:id>", methods=["POST"])
def delete_pedido(id):
    pedido = Pedido.query.get(id)
    if pedido:
        # Deletar itens do pedido
        for item in pedido.itens:
            db.session.delete(item)
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido deletado!")
    return redirect(url_for("admin"))

# ----------------- INICIALIZAR BANCO -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # cria a tabela se não existir
    app.run(debug=True)
