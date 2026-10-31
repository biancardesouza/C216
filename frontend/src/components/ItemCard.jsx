export function ItemCard({ item, emEdicao = false, onEditar, onRemover }) {
  const borda = emEdicao ? "border-indigo-400 ring-2 ring-indigo-500/20" : "border-slate-200";

  return (
    <li
      className={`flex flex-col gap-3 rounded-xl border bg-white p-4 shadow-sm sm:flex-row sm:items-start sm:justify-between ${borda}`}
    >
      <div className="min-w-0">
        <h3 className="wrap-anywhere font-semibold text-slate-900">{item.nome}</h3>
        <p className="mt-1 whitespace-pre-line wrap-anywhere text-sm text-slate-600">
          {item.descricao}
        </p>
      </div>
      <div className="flex shrink-0 gap-2">
        <button
          type="button"
          onClick={() => onEditar(item)}
          aria-label={`Editar ${item.nome}`}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
        >
          Editar
        </button>
        <button
          type="button"
          onClick={() => onRemover(item)}
          aria-label={`Remover ${item.nome}`}
          className="rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-700 transition hover:bg-red-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-500"
        >
          Remover
        </button>
      </div>
    </li>
  );
}
