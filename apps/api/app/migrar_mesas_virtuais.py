"""Aplica a migração do recurso "Network da Fome" (Mesas Virtuais) num
banco que já existe e já tem dados (ou seja: onde `inicializar_banco()` não
vai rodar o schema.sql inteiro de novo, porque a tabela `usuarios` já existe).

Rode com:
    python -m app.migrar_mesas_virtuais

Idempotente: se a tabela `mesas_virtuais` já existir, o script avisa e não
faz nada — seguro de rodar mais de uma vez (ex.: em todo deploy).

Um banco novo (branch de teste, ambiente novo) não precisa disso: o
schema.sql já inclui a seção 11 (Mesas Virtuais) desde o início, então
`inicializar_banco()` sozinho já cria tudo.
"""

from pathlib import Path

from app.config import API_DIR
from app.db import _conectar, inicializar_banco

MIGRACAO_PATH = API_DIR / "database" / "migracao_mesas_virtuais.sql"


def main() -> None:
    # Garante que o resto do schema (usuarios, produtos, etc.) existe antes
    # de tentar criar tabelas que referenciam `usuarios` e `administradores`.
    inicializar_banco()

    db = _conectar()
    try:
        ja_existe = db.execute("SELECT to_regclass('public.mesas_virtuais') AS existe").fetchone()["existe"]
        if ja_existe is not None:
            print("[burger-tech] 'mesas_virtuais' já existe — nada para migrar.")
            return

        sql = Path(MIGRACAO_PATH).read_text(encoding="utf-8")
        db.execute(sql)
        db.commit()
        print("[burger-tech] Migração 'Network da Fome' aplicada com sucesso.")
        print("  Tabelas criadas: mesas_virtuais, mesas_virtuais_participantes,")
        print("  mesas_virtuais_mensagens, mesas_virtuais_denuncias,")
        print("  mesas_virtuais_bloqueios, mesas_virtuais_banidos.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
