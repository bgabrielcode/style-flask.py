from functools import wraps
from flask import request, jsonify, current_app, session, redirect, url_for, flash
import jwt


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Você precisa fazer login para acessar essa página.', 'warning')
            return redirect(url_for('main_bp.login'))
        return f(*args, **kwargs)
    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'Token Malformado '}), 400
        if not token:
            return jsonify({'error': 'Token não encontrado'}), 401

        try:
          data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token Expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        return f(data, *args, **kwargs)
                    
    return decorated