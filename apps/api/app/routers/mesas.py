import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth_cliente import get_usuario_opcional
from app.db import get_db
from app.routers.pedidos import _carregar_itens, _salvar_itens_pedido
from app.schemas import ComandaOut, ItemPedidoOut, MesaComandaOut, MesaOut, PedidoMesaIn
from app.websocket import gerenciador_admin

router = APIRouter(prefix="/mesas", tags=["mesas"])


def _buscar_mesa_ou_404(db: sqlite3.Connection, qr_token: str) -> sqlite3.Row:
    mesa = db.execute("SELECT * FROM mesas WHERE qr_token = ?", (qr_token,)).fetchone()
    if mesa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesa não encontrada")
    return mesa


def _buscar_comanda_aberta(db: sqlite3.Connection, mesa_id: int) -> Optional[sqlite3.Row]:
    return db.execute(
        "SELECT * FROM comandas WHERE mesa_id = ? AND status = 'aberta'", (mesa_id,)
    ).fetchone()


def _abrir_comanda(db: sqlite3.Connection, mesa: sqlite3.Row, usuario: Optional[sqlite3.Row]) -> sqlite3.Row:
    if mesa["status"] == "inativa":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta mesa está inativa no momento")
    if mesa["status"] == "reservada":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta mesa está reservada no momento")

    cursor = db.execute(
        "INSERT INTO comandas (mesa_id, usuario_id) VALUES (?, ?)",
        (mesa["id"], usuario["id"] if usuario else None),
    )
    db.commit()
    return db.execute("SELECT * FROM comandas WHERE id = ?", (cursor.lastrowid,)).fetchone()


def _montar_comanda_out(db: sqlite3.Connection, comanda: sqlite3.Row) -> ComandaOut:
    itens_linhas = db.execute(
        """
        SELECT ip.* FROM itens_pedido ip
        JOIN pedidos p ON p.id = ip.pedido_id
        WHERE p.comanda_id = ?
        ORDER BY ip.id
        """,
        (comanda["id"],),
    ).fetchall()
    itens = [
        ItemPedidoOut(
            id=i["id"],
            produto_id=i["produto_id"],
            nome_produto=i["nome_produto"],
            preco_unitario=i["preco_unitario"],
            quantidade=i["quantidade"],
            subtotal=i["subtotal"],
        )
        for i in itens_linhas
    ]
    total = sum(i.subtotal for i in itens)
    return ComandaOut(
        id=comanda["id"],
        status=comanda["status"],
        numero_pessoas=comanda["numero_pessoas"],
        aberta_em=comanda["aberta_em"],
        itens=itens,
        total=total,
    )


def _mesa_out(mesa: sqlite3.Row) -> MesaOut:
    return MesaOut(id=mesa["id"], numero=mesa["numero"], capacidade=mesa["capacidade"], status=mesa["status"])


@router.get("/{qr_token}", response_model=MesaComandaOut)
def obter_mesa(
    qr_token: str,
    usuario: Optional[sqlite3.Row] = Depends(get_usuario_opcional),
    db: sqlite3.Connection = Depends(get_db),
) -> MesaComandaOut:
    mesa = _buscar_mesa_ou_404(db, qr_token)
    comanda = _buscar_comanda_aberta(db, mesa["id"])

    if comanda is None:
        comanda = _abrir_comanda(db, mesa, usuario)
        mesa = db.execute("SELECT * FROM mesas WHERE id = ?", (mesa["id"],)).fetchone()

    return MesaComandaOut(mesa=_mesa_out(mesa), comanda=_montar_comanda_out(db, comanda))


@router.post("/{qr_token}/pedidos", response_model=MesaComandaOut, status_code=status.HTTP_201_CREATED)
async def criar_pedido_mesa(
    qr_token: str,
    dados: PedidoMesaIn,
    usuario: Optional[sqlite3.Row] = Depends(get_usuario_opcional),
    db: sqlite3.Connection = Depends(get_db),
) -> MesaComandaOut:
    mesa = _buscar_mesa_ou_404(db, qr_token)
    comanda = _buscar_comanda_aberta(db, mesa["id"])
    if comanda is None:
        comanda = _abrir_comanda(db, mesa, usuario)

    itens_carregados, subtotal = _carregar_itens(db, dados.itens)

    cursor = db.execute(
        """
        INSERT INTO pedidos (usuario_id, tipo, comanda_id, subtotal, taxa_entrega, total, observacoes)
        VALUES (?, 'local', ?, ?, 0, ?, ?)
        """,
        (usuario["id"] if usuario else None, comanda["id"], subtotal, subtotal, dados.observacoes),
    )
    pedido_id = cursor.lastrowid
    _salvar_itens_pedido(db, pedido_id, itens_carregados)
    db.commit()

    mesa = db.execute("SELECT * FROM mesas WHERE id = ?", (mesa["id"],)).fetchone()
    comanda = db.execute("SELECT * FROM comandas WHERE id = ?", (comanda["id"],)).fetchone()
    comanda_out = _montar_comanda_out(db, comanda)

    await gerenciador_admin.broadcast(
        "pedido_criado",
        {"pedido_id": pedido_id, "mesa_numero": mesa["numero"], "comanda_id": comanda["id"]},
    )

    return MesaComandaOut(mesa=_mesa_out(mesa), comanda=comanda_out)


@router.post("/{qr_token}/fechar", status_code=status.HTTP_202_ACCEPTED)
async def pedir_conta(
    qr_token: str,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    mesa = _buscar_mesa_ou_404(db, qr_token)
    comanda = _buscar_comanda_aberta(db, mesa["id"])
    if comanda is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esta mesa não tem uma comanda aberta")

    # Isso só avisa a equipe pelo WebSocket — quem fecha de fato a comanda é
    # o painel administrativo (ver /api/admin/comandas/{id}/fechar).
    await gerenciador_admin.broadcast(
        "conta_solicitada",
        {"mesa_numero": mesa["numero"], "comanda_id": comanda["id"]},
    )

    return {"mensagem": "A equipe foi avisada e vai trazer a conta."}
