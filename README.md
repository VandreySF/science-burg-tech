# Science Burger Tech 🍔🔬

Projeto acadêmico desenvolvido para aplicar conceitos de engenharia de software no contexto de um sistema para hamburgueria: site público de delivery, fluxo de pedido por mesa (QR code) e painel administrativo em tempo real.

## Estrutura do repositório

```
science-burg-tech/
│
├── .github/               # Templates de issues e pull requests
├── apps/
│   ├── api/                # Back-end (Python + FastAPI + SQLite)
│   └── web/                # Front-end (React 18 + Vite + TypeScript + Tailwind v4)
├── database/                # (dentro de apps/api/) — schema, seed e o README do banco
├── security/                # Documentação e checklist de segurança do time
├── docs/                  # Documentação do projeto (requisitos, UML, arquitetura, etc.)
├── slides/                # Apresentações do projeto
├── tests/                 # Testes de integração e de sistema (além dos testes automatizados em apps/api/tests)
├── SEGURANCA.md            # Decisões de segurança da implementação e limitações conhecidas
├── guia-para-amigos.md      # Passo a passo de como rodar o projeto, em linguagem simples
├── LICENSE
└── .gitignore
```

## Tecnologias

- **Backend:** Python + FastAPI + Uvicorn (WebSocket nativo para o painel em tempo real)
- **Frontend:** React 18 + Vite + TypeScript + Tailwind v4
- **Banco de dados:** SQLite (arquivo único, sem servidor separado — veja `apps/api/database/README.md` para o porquê)

## Como rodar o projeto

Precisa de **Node.js** (18+) e **Python** (3.11+) instalados. Os dois serviços (API e site) rodam em paralelo, em dois terminais separados — veja o passo a passo detalhado em [`guia-para-amigos.md`](./guia-para-amigos.md).

### Backend (API)

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate          # Windows (no Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Windows (no Linux/Mac: cp .env.example .env)
uvicorn app.main:app --reload
```

Na primeira vez que sobe, a API cria sozinha o banco a partir de `apps/api/database/schema.sql` e imprime no terminal os links `/m/<token>` de cada mesa. A API fica em `http://127.0.0.1:8000` (documentação interativa em `/docs`).

Crie o primeiro administrador do painel (uma vez só): `python -m app.criar_admin`

### Frontend (web)

Num segundo terminal, a partir da raiz do repositório:

```bash
npm install
npm run dev
```

Abre em `http://localhost:5173`. O Vite já redireciona `/api/*`, `/ws/*` e `/uploads/*` para a API — não precisa mexer em CORS nem URLs durante o desenvolvimento.

## Segurança

As decisões de segurança da implementação (hash de senha, limite de tentativas de login/registo, separação de tokens entre cliente e administrador, validação de upload por magic bytes, etc.) estão documentadas em [`SEGURANCA.md`](./SEGURANCA.md). O checklist do time está em [`security/security-checklist.md`](./security/security-checklist.md).

## Documentação

A documentação do projeto (requisitos, diagramas UML, arquitetura, protótipos, plano de testes e atas de reunião) está em [`docs/`](./docs). As apresentações ficam em [`slides/`](./slides).

## Testes

```bash
cd apps/api
.venv\Scripts\activate
pytest
```

## Equipe

- Nome 1 — Função
- Nome 2 — Função
- Nome 3 — Função

## Licença

Este projeto está sob a licença MIT. Veja [LICENSE](./LICENSE) para mais detalhes.
