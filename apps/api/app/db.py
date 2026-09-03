import secrets
import sqlite3
from collections.abc import Generator

from app.config import DATABASE_PATH, SCHEMA_PATH


def _conectar() -> sqlite3.Connection:
    # check_same_thread=False: o FastAPI roda a dependency get_db() (síncrona)
    # numa thread do threadpool, mas os endpoints "async def" que a usam
    # rodam na thread do event loop — a mesma conexão acaba sendo usada em
    # threads diferentes dentro da mesma requisição. Como cada requisição
    # abre e fecha a sua própria conexão (nunca é compartilhada entre
    # requisições concorrentes), isso é seguro.
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_banco() -> None:
    """Cria o arquivo .db a partir do schema.sql se ele ainda não existir.

    As tabelas nunca são criadas via ORM — sempre a partir do schema.sql,
    que é a única fonte da verdade (contém os triggers e os índices únicos
    parciais que implementam as regras de negócio do sistema de mesas).
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    banco_novo = not DATABASE_PATH.exists()
    conn = _conectar()
    try:
        if banco_novo:
            schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
            conn.executescript(schema_sql)
            conn.commit()
            _rotacionar_qr_tokens_do_seed(conn)
    finally:
        conn.close()


def _rotacionar_qr_tokens_do_seed(conn: sqlite3.Connection) -> None:
    """Os qr_token inseridos pelo seed do schema.sql são só exemplo
    (previsíveis de propósito, tipo "mesa-01-a1b2c3") — antes de considerar o
    banco pronto pra uso real, trocamos cada um por um token aleatório longo,
    para que ninguém consiga "adivinhar" o link de uma mesa que não é a dela.
    """
    mesas = conn.execute("SELECT id, numero FROM mesas").fetchall()
    print("\n[burger-tech] Mesas criadas — links de QR code (rota /m/<token> no front-end):")
    for mesa in mesas:
        token = secrets.token_urlsafe(24)
        conn.execute("UPDATE mesas SET qr_token = ? WHERE id = ?", (token, mesa["id"]))
        print(f"  Mesa {mesa['numero']:>2}: /m/{token}")
    conn.commit()
    print()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependency do FastAPI: abre uma conexão nova por requisição e fecha no final."""
    conn = _conectar()
    try:
        yield conn
    finally:
        conn.close()
