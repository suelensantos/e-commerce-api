from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy # ORM - objeto de relação mapeador - gera uma camada de abstração para o banco de dados (fica acima do banco).
# Código interage com o ORM (onde será feita todas as alterações), que interage com o banco de dados
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
# UserMixin é utilizado para fazer o login do usuário
# LoginManager faz o gerenciamento de usuário, quem está logado ou não
# login_required permite não habilitar o acesso de usuários não logados às rotas (específicas), ou seja, ela obriga o usuário a estar autenticado nas rotas específicas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave_123' # necessário para fazer o login do usuário a partir da lib LoginManager
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' # precisa configurar o caminho do banco (banco de arquivos)

login_manager = LoginManager()
db = SQLAlchemy(app) # iniciar a conexão com o banco de dados (BD)
login_manager.init_app(app)
login_manager.login_view = 'login' # habilita a autenticação do usuário no login, criando uma sessão (Set-Cookie) no header da requisição (caso limpe o cookie, o usuário perderá o acesso do login, tendo que logar novamente)
CORS(app)

# Criar o model das tabelas do banco (produto)
# Para transformar o model em tabela no banco, basta digitar o comando 'flask shell' e, após, digitar '>>> db.create_all()'.
# '>>> db.drop_all()' -> serve para limpar todas as tabelas do banco
# '>>> db.create_all()'
# '>>> db.session.commit()'
# Com o comando '>>> db.session.commit()', temos a *session*, que é a propriedade do BD que armazena a **conexão** com o banco. Já o *commit*, envia para o banco e efetiva as mudanças feitas.
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), nullable=False, unique=True)
  password = db.Column(db.String(80), nullable=False)

class Product(db.Model):
  # colunas
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False) # não força o produto a não ter o nome
  price = db.Column(db.Float, nullable=False)
  description = db.Column(db.Text, nullable=True)

# Autenticação - essa função existe porque toda vez que eu fizer uma requisição em uma rota protegida, o @login_required vai precisar recuperar o usuário que está
# tentando acessar essa rota.
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@app.route('/login', methods=["POST"])
def login():
  data = request.json
  user = User.query.filter_by(username=data.get("username")).first()

  if user and data.get("password") == user.password:
    login_user(user)
    return jsonify({'message': "Logged in sucessfully!"})

  return jsonify({'message': "Unauthorized! Invalid credentials."}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
  logout_user()
  return jsonify({'message': "Logout sucessfully!"})

@app.route('/api/products/add', methods=["POST"])
@login_required # protege o acesso do usuário à rota (acesso liberado só quando estiver logado)
def add_products():
  data = request.json
  if 'name' in data and 'price' in data:
    product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
    db.session.add(product) # recupera a sessão com o banco e add o produto na tabela Product
    db.session.commit() # que manda o comando para o banco e efetua a alteração
    return jsonify({'message': "Product added successfully!"})
  return jsonify({'message': "Invalid product data!"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
  # Recuperar o produto da base de dados
  # Verificar se o produto existe
  # Se existe, apagar da base de dados, caso contrário, retornar 404 not found
  product = Product.query.get(product_id)
  if product:
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': "Product deleted successfully!"})
  return jsonify({'message': "Product not found!"}), 404

@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
  product = Product.query.get(product_id)
  if product:
    return jsonify({
      "id": product.id,
      "name": product.name,
      "price": product.price,
      "description": product.description
    })
  return jsonify({ 'message': "Product not found!"}), 404

@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
  product = Product.query.get(product_id)
  if not product:
    return jsonify({ 'message': "Product not found!"}), 404
  
  data = request.json
  if 'name' in data:
    product.name = data['name']
  
  if 'price' in data:
    product.price = data['price']

  if 'description' in data:
    product.description = data['description']

  db.session.commit()
  return jsonify({'message': "Product updated successfully!"})

@app.route('/api/products', methods=["GET"])
def get_products():
  products = Product.query.all()
  product_list = []

  for product in products:
    product_data = {
      "id": product.id,
      "name": product.name,
      "price": product.price
    }
    product_list.append(product_data)
  return jsonify(product_list)

@app.route('/')
def hello_world():
  return 'Hello World'

if __name__ == '__main__':
  app.run(debug=True)