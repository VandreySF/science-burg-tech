# Science Burger Tech 🍔🔬

Projeto acadêmico desenvolvido para aplicar conceitos de engenharia de software no contexto de um sistema para hamburgueria.

## Estrutura do repositório

```
science-burger-tech/
│
├── .github/              # Templates de issues e pull requests
├── backend/               # API e lógica de negócio (Python/Flask)
├── frontend/               # Interface do usuário
├── database/               # Schema, migrations e seeds
├── security/               # Documentação e checklist de segurança
├── docs/                  # Documentação do projeto (requisitos, UML, arquitetura, etc.)
├── slides/                # Apresentações do projeto
├── tests/                 # Testes de integração e de sistema
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore
└── LICENSE
```

## Tecnologias

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **Banco de dados:** PostgreSQL (ou outro à escolha da equipe)

## Como rodar o projeto

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
python run.py
```

### Banco de dados

1. Crie o banco de dados.
2. Rode `database/schema.sql` para criar as tabelas.
3. (Opcional) Popule com os seeds em `database/seeds/`.

## Documentação

A documentação completa do projeto (requisitos, diagramas UML, arquitetura, protótipos, plano de testes e atas de reunião) está disponível em [`docs/`](./docs).

## Equipe

- Nome 1 — Função
- Nome 2 — Função
- Nome 3 — Função

## Licença

Este projeto está sob a licença MIT. Veja [LICENSE](./LICENSE) para mais detalhes.
