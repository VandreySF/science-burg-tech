import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth_cliente import get_usuario_atual
from app.db import get_db
from app.schemas import ItemPedidoIn, ItemPedidoOut, PedidoCreateIn, PedidoOut

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

# A entrega é grátis no cardápio atual (é o que o carrinho do front-end já
# mostra) — se um dia isso mudar, é só calcular a taxa aqui.
TAXA_ENTREGA = 0.0


def _carregar_itens(db: sqlite3.Connection, itens_in: list[ItemPedidoIn]) -> tuple[list[dict], float]:
    itens_carregados: list[dict] = []
    subtotal = 0.0

    for item in itens_in:
        produto = db.execute(
            "SELECT * FROM produtos WHERE id = ? AND disponivel = 1", (item.produto_id,)
        ).fetchone()
        if produto is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto {item.produto_id} não existe ou não está disponível",
            )
        item_subtotal = produto["preco"] * item.quantidade
        subtotal += item_subtotal
        itens_carregados.append(
            {
                "produto_id": produto["id"],
                "nome_produto": produto["nome"],
                "preco_unitario": produto["preco"],
                "quantidade": item.quantidade,
                "subtotal": item_subtotal,
            }
        )

    return itens_carregados, subtotal


def _salvar_itens_pedido(db: sqlite3.Connection, pedido_id: int, itens: list[dict]) -> list[ItemPedidoOut]:
    itens_out: list[ItemPedidoOut] = []
    for item in itens:
        cursor = db.execute(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, nome_produto, preco_unitario, quantidade, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (pedido_id, item["produto_id"], item["nome_produto"], item["preco_unitario"], item["quantidade"], item["subtotal"]),
        )
        itens_out.append(
            ItemPedidoOut(
                id=cursor.lastrowid,
                produto_id=item["produto_id"],
                nome_produto=item["nome_produto"],
                preco_unitario=item["preco_unitario"],
                quantidade=item["quantidade"],
                subtotal=item["subtotal"],
            )
        )
    return itens_out


def _linha_para_pedido(db: sqlite3.Connection, linha: sqlite3.Row) -> PedidoOut:
    itens_linhas = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (linha["id"],)).fetchall()
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
    return PedidoOut(
        id=linha["id"],
        tipo=linha["tipo"],
        status=linha["status"],
        metodo_pagamento=linha["metodo_pagamento"],
        subtotal=linha["subtotal"],
        taxa_entrega=linha["taxa_entrega"],
        total=linha["total"],
        observacoes=linha["observacoes"],
        criado_em=linha["criado_em"],
        itens=itens,
    )


@router.post("", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def criar_pedido(
    dados: PedidoCreateIn,
    usuario: sqlite3.Row = Depends(get_usuario_atual),
    db: sqlite3.Connection = Depends(get_db),
) -> PedidoOut:
    if dados.tipo == "entrega" and dados.endereco is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pedido de entrega precisa de um endereço")

    itens_carregados, subtotal = _carregar_itens(db, dados.itens)

    endereco_id = None
    taxa_entrega = 0.0
    if dados.tipo == "entrega":
        endereco = dados.endereco
        assert endereco is not None
        cursor = db.execute(
            """
            INSERT INTO enderecos (usuario_id, rua, numero, complemento, bairro, cidade, estado, cep)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (usuario["id"], endereco.rua, endereco.numero, endereco.complemento, endereco.bairro, endereco.cidade, endereco.estado, endereco.cep),
        )
        endereco_id = cursor.lastrowid
        taxa_entrega = TAXA_ENTREGA

    total = subtotal + taxa_entrega

    cursor = db.execute(
        """
        INSERT INTO pedidos (usuario_id, tipo, endereco_id, metodo_pagamento, subtotal, taxa_entrega, total, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (usuario["id"], dados.tipo, endereco_id, dados.metodo_pagamento, subtotal, taxa_entrega, total, dados.observacoes),
    )
    pedido_id = cursor.lastrowid

    _salvar_itens_pedido(db, pedido_id, itens_carregados)
    db.commit()

    pedido = db.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    return _linha_para_pedido(db, pedido)


@router.get("/me", response_model=list[PedidoOut])
def meus_pedidos(
    usuario: sqlite3.Row = Depends(get_usuario_atual),
    db: sqlite3.Connection = Depends(get_db),
) -> list[PedidoOut]:
    linhas = db.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY criado_em DESC", (usuario["id"],)
    ).fetchall()
    return [_linha_para_pedido(db, linha) for linha in linhas]
