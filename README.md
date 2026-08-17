# Painel StyleSync

Sistema de gerenciamento de produtos e vendas desenvolvido em Flask, com **duas formas de acesso**: uma interface web completa (login, dashboard, CRUD de produtos, upload de vendas) e uma API REST pura, autenticada via JWT, pensada para consumo por outras aplicações (testável via Postman).

## Funcionalidades

- **Autenticação dupla**: login por sessão (interface web) e login via JWT (API)
- **Dashboard** com métricas em tempo real (total de produtos, vendas do mês)
- **CRUD completo de produtos**: listar, criar, editar e excluir
- **Relatório de vendas** com totalização
- **Importação de vendas em massa** via upload de arquivo CSV
- Validação de dados com **Pydantic**
- Persistência em **MongoDB**

## Tecnologias

- Python 3
- Flask
- MongoDB (PyMongo)
- Pydantic
- PyJWT
- Bootstrap 5 (interface)
- python-dotenv

## Como rodar o projeto

### Pré-requisitos
- Python 3.10+
- MongoDB rodando localmente (ou uma connection string de um cluster remoto)

### Passo a passo

1. Clone o repositório
```bash
git clone https://github.com/bgabrielcode/style-flask.py.git
cd style-flask.py
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto com:
```
MONGO_URI=sua_connection_string_do_mongodb
SECRET_KEY=uma_chave_secreta_qualquer
```

5. Rode a aplicação
```bash
python .\run.py
```

6. Acesse: `http://127.0.0.1:5000`

## Credenciais de teste

```
Usuário: admin
Senha: supersecret
```

---

## Interface Web

Voltada para uso humano, via navegador, com autenticação por sessão.

| Rota | Descrição |
|---|---|
| `/login` | Tela de login |
| `/dashboard` | Painel com métricas gerais |
| `/products/view` | Listagem de produtos |
| `/products/add` | Formulário de cadastro de produto |
| `/products/edit/<id>` | Formulário de edição de produto |
| `/products/delete/<id>` | Exclusão de produto (POST) |
| `/sales/upload` | Upload de arquivo CSV com vendas |
| `/sales/report` | Relatório de vendas do mês |
| `/logout` | Encerra a sessão |

### Fluxo de uso
1. Acesse `/login` e entre com as credenciais de teste
2. No dashboard, acompanhe o total de produtos e vendas do mês
3. Gerencie produtos pela aba "Produtos"
4. Importe vendas em massa enviando um arquivo `.csv` na aba "Upload de Vendas"
5. Consulte o relatório consolidado em "Ver Relatórios"

---

## API REST

Voltada para consumo programático, autenticada via **JWT** (Bearer Token). Ideal para testar no Postman ou integrar com outro sistema/frontend.

### Autenticação

**POST** `/api/login`

```json
{
  "username": "admin",
  "password": "supersecret"
}
```

Retorna:
```json
{
  "acess_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

Use esse token no header `Authorization: Bearer <token>` nas rotas protegidas.

### Endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/api/login` | Não | Autentica e retorna um token JWT |
| GET | `/products` | Não | Lista todos os produtos |
| POST | `/products` | Sim | Cria um novo produto |
| GET | `/product/<id>` | Não | Detalha um produto específico |
| PUT | `/product/<id>` | Sim | Atualiza um produto existente |
| DELETE | `/product/<id>` | Sim | Remove um produto |
| POST | `/api/sales/upload` | Sim | Importa vendas via arquivo CSV |

### Exemplo de corpo para criação de produto (POST /products)

```json
{
  "name": "Placa de vídeo RTX 9090",
  "description": "A placa de vídeo mais potente para jogos e IA",
  "price": 15999.99,
  "stock": 50
}
```

### Formato esperado do CSV de vendas

```csv
sale_date,product_id,quantity,total_valor
2026-08-10,66b15092d6e04f447f5b3f2a,2,97.26
2026-08-11,66b15092d6e04f447f5b3f2c,3,83.10
```

---

## Estrutura do projeto

```
style_flask2/
├── app/
│   ├── models/          # Modelos Pydantic (Product, Sale, User)
│   ├── routes/          # Rotas da aplicação (web + API)
│   ├── templates/       # Templates HTML (Bootstrap 5)
│   ├── decorators.py    # Decorators de autenticação (JWT e sessão)
│   └── __init__.py      # Factory da aplicação Flask
├── test/                # Testes do projeto
├── run.py               # Ponto de entrada da aplicação
└── requirements.txt      # Dependências do projeto
```

## Autor

Bruno Gabriel Alves Luiz
[github.com/bgabrielcode](https://github.com/bgabrielcode)
