import { ItemCard } from "./ItemCard";

function Conteudo({
  itens,
  carregando,
  erroCarregamento,
  onRecarregar,
  idEmEdicao,
  onEditar,
  onRemover,
}) {
  if (carregando) {
    return (
      <p
        role="status"
        className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500"
      >
        Carregando itens...
      </p>
    );
  }

  if (erroCarregamento) {
    return (
      <div
        role="alert"
        className="flex flex-col items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-6 text-center text-red-700"
      >
        <p className="font-medium">Não foi possível carregar os itens.</p>
        <p className="text-sm">{erroCarregamento}</p>
        <button
          type="button"
          onClick={onRecarregar}
          className="rounded-lg border border-red-300 bg-white px-3 py-1.5 text-sm font-medium text-red-700 transition hover:bg-red-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-500"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (itens.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-slate-300 bg-white/60 p-8 text-center text-slate-500">
        Nenhum item cadastrado ainda.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {itens.map((item) => (
        <ItemCard
          key={item.id}
          item={item}
          emEdicao={item.id === idEmEdicao}
          onEditar={onEditar}
          onRemover={onRemover}
        />
      ))}
    </ul>
  );
}

export function ItemList({
  itens,
  carregando = false,
  erroCarregamento = null,
  erroRemocao = null,
  onRecarregar,
  idEmEdicao = null,
  onEditar,
  onRemover,
}) {
  const mostrarContador = !carregando && !erroCarregamento;

  return (
    <section aria-labelledby="titulo-lista" aria-busy={carregando} className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between gap-2">
        <h2 id="titulo-lista" className="text-lg font-semibold text-slate-900">
          Itens
        </h2>
        {mostrarContador && (
          <span className="text-sm text-slate-500" aria-live="polite">
            {itens.length === 1 ? "1 item" : `${itens.length} itens`}
          </span>
        )}
      </div>

      {erroRemocao && (
        <p
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          Não foi possível remover o item. {erroRemocao}
        </p>
      )}

      <Conteudo
        itens={itens}
        carregando={carregando}
        erroCarregamento={erroCarregamento}
        onRecarregar={onRecarregar}
        idEmEdicao={idEmEdicao}
        onEditar={onEditar}
        onRemover={onRemover}
      />
    </section>
  );
}
