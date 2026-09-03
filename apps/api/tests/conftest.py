import os
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

# Precisa estar definido antes de "app.config" ser importado pela primeira
# vez (ele lê as variáveis de ambiente no import). O valor exato não
# importa — cada teste troca o caminho de verdade via monkeypatch, veja a
# fixture "db" abaixo.
os.environ.setdefault("DATABASE_PATH", "database/nao-usado-nos-testes.db")
# Precisam ter 32+ caracteres e ser diferentes entre si — as mesmas regras
# que o config.py exige de qualquer ambiente.
os.environ["JWT_SECRET_CLIENTE"] = "segredo-de-teste-do-cliente-com-tamanho-suficiente"
os.environ["JWT_SECRET_ADMIN"] = "segredo-de-teste-do-admin-com-tamanho-suficiente"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

import app.db as app_db  # noqa: E402
from app.auth_cliente import hash_senha  # noqa: E402
from app.limite_tentativas import limpar_tudo  # noqa: E402
from app.main import app  # noqa: E402

_diretorio_temp = Path(tempfile.mkdtemp(prefix="burger_tech_test_"))


@pytest.fixture(autouse=True)
def _zerar_limite_de_tentativas():
    """O contador de tentativas de login vive na memória do processo, então
    é compartilhado por todos os testes. Sem zerar entre um teste e outro,
    um teste que erra a senha de propósito acabaria bloqueando o login de
    outro teste que roda depois."""
    limpar_tudo()
    yield
    limpar_tudo()


@pytest.fixture()
def db(monkeypatch):
    """Cada teste ganha o seu próprio arquivo .db novo, isolado dos outros
    testes e do banco usado em desenvolvimento."""
    caminho = _diretorio_temp / f"{uuid.uuid4().hex}.db"
    monkeypatch.setattr(app_db, "DATABASE_PATH", caminho)

    app_db.inicializar_banco()
    conn = app_db._conectar()
    yield conn
    conn.close()


@pytest.fixture()
def client(db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_ativo(db):
    db.execute(
        "INSERT INTO administradores (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)",
        ("Admin de Teste", "admin@teste.com", hash_senha("senha-admin-123"), "admin"),
    )
    db.commit()
    return {"email": "admin@teste.com", "senha": "senha-admin-123"}
