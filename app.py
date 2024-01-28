from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy # ORM - objeto de relação mapeador - gera uma camada de abstração para o banco de dados (fica acima do banco).
# Código interage com o ORM (onde será feita todas as alterações), que interage com o banco de dados
from flask_cors import CORS

app = Flask(__name__)
# precisa configurar o caminho do banco (banco de arquivos)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# iniciar a conexão com o banco de dados (BD)
db = SQLAlchemy(app)
CORS(app)

# Criar o model das tabelas do banco (produto)
# Para transformar o model em tabela no banco, basta digitar o comando 'flask shell' e, após, digitar '>>> db.create_all()'.
# Com o comando '>>> db.session.commit()', temos a *session*, que é a propriedade do BD que armazena a **conexão** com o banco. Já o *commit*, envia para o banco e efetiva as mudanças feitas.

class Product(db.Model):
  # colunas
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False) # não força o produto a não ter o nome
  price = db.Column(db.Float, nullable=False)
  description = db.Column(db.Text, nullable=True)

@app.route('/api/products/add', methods=["POST"])
def add_products():
  data = request.json
  if 'name' in data and 'price' in data:
    product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
    db.session.add(product) # recupera a sessão com o banco e add o produto na tabela Product
    db.session.commit() # que manda o comando para o banco e efetua a alteração
    return jsonify({'message': "Product added successfully!"})
  return jsonify({'message': "Invalid product data!"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
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