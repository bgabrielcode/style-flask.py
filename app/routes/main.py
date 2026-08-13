from flask import Blueprint, jsonify, request
from app.models.user import LoginPayLoad
from pydantic import ValidationError

main_bp = Blueprint('main_bp', __name__)

# RF: O sistema deve permitir que um usuário se autentique para obter um Token
@main_bp.route('/login', methods=['POST'])
def login():
    try:
       raw_data = request.get_json()
       user_data = LoginPayLoad(**raw_data)
    except ValidationError as e:    
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        jsonify({"error": "Erro durante a requisição do dado"}), 500


    if user_data.username == 'admin' and user_data.password == '123':
        return jsonify({"message": "Login bem-sucedido!"})
    else: 
        return jsonify({"message": "Credenciais invalidas!"})


# RF: O sistema deve permitir listagem de todos os produtos
@main_bp.route('/products', methods={"GET"})
def get_products():
    return jsonify({"message":"Está é a rota de listagem de produtos"})

# RF: o sistema deve permitir a criação de um novo produto
@main_bp.route('/products', methods={"POST"})
def create_product():
    return jsonify({"message":"Está é a rota de criação de produtos"})

# RF: O sistema deve permitir a visualização dos detalhes de um unico produto
@main_bp.route('/product/<int:product_id>', methods={"GET"})
def get_product_by_id(product_id):
    return jsonify({"message":f"Está é a rota de visualização do detalhe do id do produto: {product_id}" })

# RF: O sistema deve permitir a atualização de um unico produto e produto existente
@main_bp.route('/product/<int:product_id>', methods={"PUT"})
def update_product(product_id):
    return jsonify({"message":f"Está é a rota de atualização do produto com id: {product_id}" })

# RF: O sistema deve permitir a delecao de um unico produto e produto existente
@main_bp.route('/product/<int:product_id>', methods={"DELETE"})
def delete_product(product_id):
    return jsonify({"message":f"Está é a rota de deleção do produto com id: {product_id}" })

# RF: O sistema deve permitir a importação de vendas através de um arquivo
@main_bp.route('/sales/upload', methods={"POST"})
def upload_sales():
    return jsonify({"message":"Está é a rota de upload do arquivo de vendas"})

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem vindo ao StyleSync!"})