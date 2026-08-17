from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for, session, flash
from app.models.user import LoginPayLoad
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.products import *
from app.models.sale import Sale
from app.decorators import token_required, login_required
from datetime import datetime, timedelta, timezone, time
import jwt
import csv
import os
import io

main_bp = Blueprint('main_bp', __name__)

# RF: O sistema deve permitir que um usuário se autentique para obter um Token
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'supersecret':
        session['user'] = username
        return redirect(url_for('main_bp.dashboard'))

    flash('Credenciais inválidas!', 'danger')
    return redirect(url_for('main_bp.login'))


# ROTA PARA A API (JSON) - usada pelo Postman/JWT
# RF: O sistema deve permitir que um usuário se autentique para obter um Token
@main_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
       raw_data = request.get_json()
       user_data = LoginPayLoad(**raw_data)

    except ValidationError as e:    
        return jsonify({"error": e.errors()}), 400
    except Exception:
        return jsonify({"error": "Corpo da requisição inválido ou não é um JSON."}), 500


    if user_data.username == 'admin' and user_data.password == 'supersecret':
        token = jwt.encode(
            {
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
            },
            current_app.config['SECRET_KEY'],
            algorithm = 'HS256'
        )

        return jsonify({'acess_token': token}), 200
    
    return jsonify({"message": "Credenciais inválidas!"}), 401


# RF: O sistema deve permitir listagem de todos os produtos
@main_bp.route('/products', methods={"GET"})
def get_products():
    products_cursor = db.products.find({})
    products_list = [ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor]
    return jsonify(products_list)


# ROTA WEB (HTML) - lista de produtos com interface
@main_bp.route('/products/view')
@login_required
def products_view():
    products_cursor = db.products.find({})
    products_list = [ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor]
    return render_template('products.html', products=products_list)


# RF: o sistema deve permitir a criação de um novo produto
@main_bp.route('/products', methods={"POST"})
@token_required
def create_product(token):
    try: 
        product = Product(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()})

    result = db.products.insert_one(product.model_dump())
    
    return jsonify({"message":"Está é a rota de criação de produtos",
                    "id": str(result.inserted_id)}), 201


# ROTA WEB (HTML) - formulário de criação de produto
@main_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'GET':
        return render_template('add_product.html')

    try:
        product_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'stock': int(request.form.get('stock'))
        }
        product = Product(**product_data)
    except ValidationError as e:
        flash('Dados inválidos. Verifique os campos e tente novamente.', 'danger')
        return redirect(url_for('main_bp.add_product'))
    except (ValueError, TypeError):
        flash('Preço e estoque devem ser números válidos.', 'danger')
        return redirect(url_for('main_bp.add_product'))

    db.products.insert_one(product.model_dump())
    flash('Produto adicionado com sucesso!', 'success')
    return redirect(url_for('main_bp.products_view'))
    

# RF: O sistema deve permitir a visualização dos detalhes de um unico produto
@main_bp.route('/product/<string:product_id>', methods={"GET"})
def get_product_by_id(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception as e:
        return jsonify({"erro":f"Erro ao transformar o {product_id} em ObjectID: {e}" })

    product = db.products.find_one({'_id':oid})

    if product:
       product_model = ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
       return jsonify(product_model)
    else:
        return jsonify({"error":f"Produto com o id: {product_id} - Não encontrado" })

# RF: O sistema deve permitir a atualização de um unico produto e produto existente
@main_bp.route('/product/<string:product_id>', methods={"PUT"})
@token_required
def update_product(token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
         return jsonify({"error": e.errors()})

    update_result = db.products.update_one(
        {"_id": oid},
        {"$set": update_data.model_dump(exclude_unset=True)}
    )

    if update_result.matched_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404

    
    updated_product = db.products.find_one({"_id": oid})
    return jsonify(ProductDBModel(**update_product).model_dump(by_alias=True, exclude=True))

# ROTA WEB (HTML) - editar produto existente
@main_bp.route('/products/edit/<string:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        flash('ID de produto inválido.', 'danger')
        return redirect(url_for('main_bp.products_view'))

    if request.method == 'GET':
        product = db.products.find_one({"_id": oid})
        if not product:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('main_bp.products_view'))
        product_data = ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
        return render_template('edit_product.html', product=product_data)

    try:
        update_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'stock': int(request.form.get('stock'))
        }
    except (ValueError, TypeError):
        flash('Preço e estoque devem ser números válidos.', 'danger')
        return redirect(url_for('main_bp.edit_product', product_id=product_id))

    db.products.update_one({"_id": oid}, {"$set": update_data})
    flash('Produto atualizado com sucesso!', 'success')
    return redirect(url_for('main_bp.products_view'))


# RF: O sistema deve permitir a delecao de um unico produto e produto existente
@main_bp.route('/product/<string:product_id>', methods={"DELETE"})
@token_required
def delete_product(token, product_id):
    try:
        oid = ObjectId(product_id)
    except:
         return jsonify({"error":"id do produto inválido"}), 400

    delete_product = db.products.delete_one({"_id": oid})

    if delete_product.deleted_count == 0:
        return jsonify({"error": "Produto não foi encontrado"}), 404

    return "", 204


# ROTA WEB (HTML) - excluir produto direto
@main_bp.route('/products/delete/<string:product_id>', methods=['POST'])
@login_required
def delete_product_view(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        flash('ID de produto inválido.', 'danger')
        return redirect(url_for('main_bp.products_view'))

    result = db.products.delete_one({"_id": oid})

    if result.deleted_count == 0:
        flash('Produto não encontrado.', 'danger')
    else:
        flash('Produto excluído com sucesso!', 'success')

    return redirect(url_for('main_bp.products_view'))

# RF: O sistema deve permitir a importação de vendas através de um arquivo
@main_bp.route('/sales/upload', methods={"GET","POST"})
@login_required
def upload_sales():
    if request.method == 'GET':
        return render_template('upload_sales.html')

    if 'file' not in request.files:
        flash('Nenhum arquivo foi enviado', 'danger')
        return redirect(url_for('main_bp.upload_sales'))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo foi selecionado', 'danger')
        return redirect(url_for('main_bp.upload_sales'))

    if file and file.filename.endswith('.csv'):
        csv_stream = io.StringIO(file.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(csv_stream)

        sales_to_insert = []
        error = []

        for row_run, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)
                sale_dict = sale_data.model_dump()
                sale_dict['sale_date'] = datetime.combine(sale_dict['sale_date'], time.min)
                sales_to_insert.append(sale_dict)
            except ValidationError:
                error.append(f'Linha {row_run} com dados inválidos')
            except Exception:
                error.append(f'Linha {row_run} com erro inesperado nos dados')

        if sales_to_insert:
            try:
                db.sale.insert_many(sales_to_insert)
            except Exception as e:
                flash(f'Erro ao salvar no banco: {e}', 'danger')
                return redirect(url_for('main_bp.upload_sales'))

        flash(f'{len(sales_to_insert)} vendas importadas com sucesso! Erros: {len(error)}', 'success')
        return redirect(url_for('main_bp.upload_sales'))

    flash('Arquivo inválido. Envie um .csv', 'danger')
    return redirect(url_for('main_bp.upload_sales'))


# ROTA WEB (HTML) - relatório de vendas do mês
@main_bp.route('/sales/report')
@login_required
def sales_report():
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    sales_cursor = db.sale.find({"sale_date": {"$gte": start_of_month}}).sort("sale_date", 1)
    sales_list = list(sales_cursor)

    total_geral = sum(sale.get('total_valor', 0) for sale in sales_list)

    return render_template('sales_report.html', sales=sales_list, total_geral=total_geral)


# ROTA API (JSON) - usada pelo Postman/JWT
# RF: O sistema deve permitir a importação de vendas através de um arquivo
@main_bp.route('/api/sales/upload', methods=["POST"])
@token_required
def api_upload_sales(token):
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo foi selecionado"}), 400

    if file and file.filename.endswith('.csv'):
        csv_stream = io.StringIO(file.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(csv_stream)

        sales_to_insert = []
        error = []

        for row_run, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)
                sale_dict = sale_data.model_dump()
                sale_dict['sale_date'] = datetime.combine(sale_dict['sale_date'], time.min)
                sales_to_insert.append(sale_dict)
            except ValidationError as e:
                error.append(f'Linha {row_run} com dados inválidos')
            except Exception:
                error.append(f'Linha {row_run} com erro inesperado nos dados')

        if sales_to_insert:
            try:
                db.sale.insert_many(sales_to_insert)
            except Exception as e:
                return jsonify({'error': f'{e}'})
        return jsonify({
            "message": "Upload realizado com sucesso",
            "vendas importadas": len(sales_to_insert),
            "erros encontrados": error
        }), 200

    return jsonify({"message": "Está é a rota de upload do arquivo de vendas"})

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem vindo ao StyleSync!"})

@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_products = db.products.count_documents({})

    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    sales_this_month = db.sale.count_documents({
        "sale_date": {"$gte": start_of_month}
    })

    return render_template(
        'dashboard.html',
        total_products=total_products,
        sales_this_month=sales_this_month
    )

@main_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main_bp.login'))