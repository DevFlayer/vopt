# VOPT Business — Backend Django

Backend seguro em **Django + Django REST Framework + MongoDB**.

## Instalação

```bash
# 1. Ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# 2. Dependências
pip install -r requirements.txt

# 3. Variáveis de ambiente
cp .env.example .env
# Edite o .env — gere o DJANGO_SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Migrations
python manage.py makemigrations usuarios
python manage.py migrate

# 5. Rodar
python manage.py runserver
```

## Endpoints

| Método | Rota                            | Auth | Descrição               |
|--------|---------------------------------|:----:|-------------------------|
| POST   | `/api/auth/cadastro/`           | ❌   | Criar conta PF ou PJ    |
| POST   | `/api/auth/login/`              | ❌   | Login → JWT             |
| POST   | `/api/auth/refresh/`            | ❌   | Renovar access token    |
| GET    | `/api/usuario/perfil/`          | ✅   | Dados do usuário        |
| GET    | `/api/usuario/trial/`           | ✅   | Dias restantes do trial |
| GET    | `/api/info/funcionalidades/`    | ❌   | Funcionalidades         |
| GET    | `/api/info/planos/`             | ❌   | Planos e preços         |
| GET    | `/api/info/suporte/`            | ❌   | Canais de suporte       |
| GET    | `/api/info/health/`             | ❌   | Health check            |

## Integração com o HTML do VOPT

```javascript
// Cadastro
await fetch("/api/auth/cadastro/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    nome: "Maria Silva", email: "maria@dominio.com.br",
    documento: "123.456.789-00", senha: "MinhaSenh@1"
  })
});

// Login
const { access, refresh } = await fetch("/api/auth/login/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "maria@dominio.com.br", senha: "MinhaSenh@1" })
}).then(r => r.json());

// Rota protegida
const perfil = await fetch("/api/usuario/perfil/", {
  headers: { "Authorization": `Bearer ${access}` }
}).then(r => r.json());
```

## Estrutura

```
vopt_django/
├── manage.py
├── requirements.txt
├── .env.example
├── vopt/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── usuarios/
    ├── models.py        ← model de usuário (AbstractBaseUser)
    ├── serializers.py   ← validação de entrada/saída
    ├── utils.py         ← exception handler customizado
    ├── views/
    │   ├── auth.py      ← cadastro, login, refresh
    │   ├── usuario.py   ← perfil, trial
    │   └── info.py      ← endpoints públicos
    └── urls/
        ├── auth.py
        ├── usuario.py
        └── info.py
```
