# StyleSync API

API REST desenvolvida em **Flask**, com validação de dados via **Pydantic**, para gerenciamento de produtos, autenticação de usuários e controle de vendas de uma loja.

> ⚠️ Projeto em desenvolvimento. As rotas de produtos e vendas atualmente retornam mensagens de exemplo (mock) e ainda não estão conectadas a um banco de dados — a persistência de dados está no roadmap.

## 🚀 Tecnologias

- **Python 3**
- **Flask** — framework web e organização por Blueprints
- **Pydantic** — validação e tipagem de dados de entrada

## 📁 Estrutura do projeto

```
style_flask2/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── models/
│   │   ├── user.py          # Model de login (LoginPayLoad)
│   │   ├── products.py      # Model de produto (Product)
│   │   └── sale.py          # Model de venda (sale)
│   └── routes/
│       └── main.py          # Blueprint principal com as rotas da API
├── run.py                   # Ponto de entrada da aplicação
├── requirements.txt
└── README.md
```

## 🔐 Autenticação

| Método | Rota      | Descrição                                  |
|--------|-----------|---------------------------------------------|
| POST   | `/login`  | Autentica o usuário via `username`/`password` |

*Validação do payload feita com o model `LoginPayLoad` (Pydantic). Credenciais atualmente fixas para fins de teste (`admin` / `123`).*

## 📦 Produtos

| Método | Rota                       | Descrição                                  |
|--------|-----------------------------|---------------------------------------------|
| GET    | `/products`                 | Lista todos os produtos                     |
| POST   | `/products`                 | Cria um novo produto                        |
| GET    | `/product/<int:product_id>` | Retorna os detalhes de um produto específico|
| PUT    | `/product/<int:product_id>` | Atualiza um produto existente               |
| DELETE | `/product/<int:product_id>` | Remove um produto existente                 |

Model `Product` (Pydantic):
```python
class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    stock: int
```

## 💰 Vendas

| Método | Rota             | Descrição                              |
|--------|-------------------|------------------------------------------|
| POST   | `/sales/upload`   | Importa vendas a partir de um arquivo    |

Model `sale` (Pydantic):
```python
class sale(BaseModel):
    sale_date: date
    product_id: str
    quantity: int
    total_valor: float
```

## ⚙️ Como rodar o projeto localmente

```bash
# Clone o repositório
git clone https://github.com/bgabrielcode/style_flask2.git
cd style_flask2

# Crie e ative o ambiente virtual
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python run.py
```

A API estará disponível em `http://127.0.0.1:5000`.

## 🗺️ Roadmap

- [ ] Persistência de dados (banco de dados)
- [ ] Implementação real do CRUD de produtos (atualmente mock)
- [ ] Autenticação com hash de senha e emissão de token (JWT)
- [ ] Processamento real do upload de vendas
- [ ] Testes automatizados

## 👤 Autor

**Bruno Gabriel Alves Luiz**
[GitHub](https://github.com/bgabrielcode)
