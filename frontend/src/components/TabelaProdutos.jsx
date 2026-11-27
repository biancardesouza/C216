import { useState } from "react";
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

const BOTAO = "rounded-md px-2 py-1 text-xs font-medium";

function Acoes({ produto, onEditar, onExcluir }) {
  // A exclusão pede confirmação na própria linha, sem janelas do navegador.
  const [confirmando, setConfirmando] = useState(false);

  if (confirmando) {
    return (
      <div className="flex justify-end gap-1">
        <span className="self-center text-xs text-slate-600">Excluir?</span>
        <button
          type="button"
          onClick={() => {
            setConfirmando(false);
            onExcluir(produto);
          }}
          className={`${BOTAO} bg-red-600 text-white hover:bg-red-700`}
        >
          Sim
        </button>
        <button
          type="button"
          onClick={() => setConfirmando(false)}
          className={`${BOTAO} border border-slate-300 hover:bg-slate-50`}
        >
          Não
        </button>
      </div>
    );
  }

  return (
    <div className="flex justify-end gap-1">
      <button
        type="button"
        onClick={() => onEditar(produto)}
        aria-label={`Editar ${produto.nome}`}
        className={`${BOTAO} border border-slate-300 hover:bg-slate-50`}
      >
        Editar
      </button>
      <button
        type="button"
        onClick={() => setConfirmando(true)}
        aria-label={`Excluir ${produto.nome}`}
        className={`${BOTAO} border border-red-200 text-red-700 hover:bg-red-50`}
      >
        Excluir
      </button>
    </div>
  );
}

export default function TabelaProdutos({ produtos, onEditar, onExcluir }) {
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
            <th className="px-4 py-3 text-right">Ações</th>
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
              <td className="px-4 py-3">
                <Acoes produto={produto} onEditar={onEditar} onExcluir={onExcluir} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
