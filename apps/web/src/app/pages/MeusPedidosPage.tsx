import { useEffect, useState } from "react";
import { Link } from "react-router";
import { LogIn, PackageSearch } from "lucide-react";
import { FadeUp } from "@/app/components/common/FadeUp";
import { useClienteAuth } from "@/app/hooks/useClienteAuth";
import { meusPedidos } from "@/app/lib/api";
import type { PedidoApi, StatusPedido } from "@/app/types";

const STATUS_LABEL: Record<StatusPedido, string> = {
  pendente: "Pendente",
  confirmado: "Confirmado",
  em_preparo: "Em preparo",
  saiu_para_entrega: "Saiu para entrega",
  pronto: "Pronto",
  entregue: "Entregue",
  cancelado: "Cancelado",
};

const TIPO_LABEL: Record<string, string> = { entrega: "Entrega", retirada: "Retirada", local: "Mesa" };

export function MeusPedidosPage() {
  const { usuario, token, carregando: carregandoAuth } = useClienteAuth();
  const [pedidos, setPedidos] = useState<PedidoApi[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    meusPedidos(token)
      .then(setPedidos)
      .catch(() => setErro("Não foi possível carregar os seus pedidos."));
  }, [token]);

  if (carregandoAuth) return null;

  return (
    <section className="py-20 min-h-[60vh]">
      <div className="max-w-3xl mx-auto px-6">
        <FadeUp className="text-center mb-12">
          <p className="text-xs text-accent mb-2" style={{ fontFamily: "'JetBrains Mono',monospace" }}>
            // meus_pedidos.log
          </p>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground" style={{ fontFamily: "'Bricolage Grotesque',sans-serif" }}>
            Meus <span className="text-primary">Pedidos</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-3 max-w-md mx-auto">
            Acompanhe aqui o histórico e o status dos seus pedidos.
          </p>
        </FadeUp>

        {!usuario ? (
          <FadeUp className="flex flex-col items-center justify-center py-16 text-center bg-card border border-border rounded-3xl">
            <LogIn size={44} className="text-muted-foreground/30 mb-4" />
            <p className="text-sm text-muted-foreground mb-4">Entre na sua conta para ver o histórico de pedidos.</p>
            <Link
              to="/login"
              className="px-6 py-3 bg-primary text-white font-bold text-sm rounded-xl hover:bg-primary/90 transition-colors"
              style={{ fontFamily: "'Bricolage Grotesque',sans-serif" }}
            >
              Entrar
            </Link>
          </FadeUp>
        ) : erro ? (
          <p className="text-center text-sm text-destructive">{erro}</p>
        ) : pedidos === null ? (
          <p className="text-center text-sm text-muted-foreground py-12">Carregando…</p>
        ) : pedidos.length === 0 ? (
          <FadeUp className="flex flex-col items-center justify-center py-16 text-center bg-card border border-border rounded-3xl">
            <PackageSearch size={44} className="text-muted-foreground/30 mb-4" />
            <p className="text-sm text-muted-foreground">Você ainda não fez nenhum pedido.</p>
            <p className="text-xs text-accent mt-1.5" style={{ fontFamily: "'JetBrains Mono',monospace" }}>
              // status: aguardando primeiro commit
            </p>
          </FadeUp>
        ) : (
          <div className="space-y-4">
            {pedidos.map((pedido) => (
              <FadeUp key={pedido.id} className="bg-card border border-border rounded-3xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xs text-muted-foreground font-mono" style={{ fontFamily: "'JetBrains Mono',monospace" }}>
                      #{pedido.id} · {TIPO_LABEL[pedido.tipo] ?? pedido.tipo} · {new Date(pedido.criado_em).toLocaleString("pt-BR")}
                    </p>
                  </div>
                  <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-secondary border border-border text-foreground" style={{ fontFamily: "'Bricolage Grotesque',sans-serif" }}>
                    {STATUS_LABEL[pedido.status] ?? pedido.status}
                  </span>
                </div>
                <ul className="space-y-3">
                  {pedido.itens.map((item) => (
                    <li key={item.id} className="flex items-center justify-between text-sm border-b border-border/50 pb-3">
                      <span className="text-foreground font-medium">
                        {item.quantidade}x {item.nome_produto}
                      </span>
                      <span className="text-primary font-bold">R$ {item.subtotal.toFixed(2).replace(".", ",")}</span>
                    </li>
                  ))}
                </ul>
                <div className="flex justify-between font-bold pt-4">
                  <span style={{ fontFamily: "'Bricolage Grotesque',sans-serif" }}>Total</span>
                  <span className="text-primary text-xl" style={{ fontFamily: "'Bricolage Grotesque',sans-serif" }}>
                    R$ {pedido.total.toFixed(2).replace(".", ",")}
                  </span>
                </div>
              </FadeUp>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
