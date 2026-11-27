import { formatarMoeda } from "../utils/estoque.js";

function SituacaoEstoque({ produto }) {
  if (produto.estoque_baixo) {
    return (
      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
        Estoque baixo
      </span>
    );
  }
  return (
    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">
      OK
    </span>
  );
}

export default function TabelaProdutos({ produtos }) {
  if (produtos.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
        Nenhum produto cadastrado ainda.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">SKU</th>
            <th className="px-4 py-3">Produto</th>
            <th className="px-4 py-3">Categoria</th>
            <th className="px-4 py-3 text-right">Preço</th>
            <th className="px-4 py-3 text-right">Qtd.</th>
            <th className="px-4 py-3 text-right">Mín.</th>
            <th className="px-4 py-3">Situação</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {produtos.map((produto) => (
            <tr key={produto.id} className={produto.estoque_baixo ? "bg-amber-50/60" : undefined}>
              <td className="px-4 py-3 font-mono text-xs">{produto.sku}</td>
              <td className="px-4 py-3 font-medium">{produto.nome}</td>
              <td className="px-4 py-3 text-slate-600">{produto.categoria}</td>
              <td className="px-4 py-3 text-right">{formatarMoeda(produto.preco)}</td>
              <td className="px-4 py-3 text-right font-semibold">{produto.quantidade}</td>
              <td className="px-4 py-3 text-right text-slate-500">{produto.estoque_minimo}</td>
              <td className="px-4 py-3">
                <SituacaoEstoque produto={produto} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
