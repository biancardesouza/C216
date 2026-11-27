import { calcularResumo, formatarMoeda } from "../utils/estoque.js";

function Cartao({ titulo, valor, destaque = false }) {
  return (
    <div
      className={`rounded-lg border bg-white p-4 shadow-sm ${
        destaque ? "border-amber-300 bg-amber-50" : "border-slate-200"
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{titulo}</p>
      <p className={`mt-1 text-2xl font-semibold ${destaque ? "text-amber-700" : ""}`}>{valor}</p>
    </div>
  );
}

export default function ResumoEstoque({ produtos }) {
  const resumo = calcularResumo(produtos);

  return (
    <section aria-label="Resumo do estoque" className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <Cartao titulo="Produtos" valor={resumo.totalProdutos} />
      <Cartao titulo="Unidades" valor={resumo.totalUnidades} />
      <Cartao
        titulo="Estoque baixo"
        valor={resumo.comEstoqueBaixo}
        destaque={resumo.comEstoqueBaixo > 0}
      />
      <Cartao titulo="Valor em estoque" valor={formatarMoeda(resumo.valorEmEstoque)} />
    </section>
  );
}
