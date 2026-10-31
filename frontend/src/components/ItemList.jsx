import { ItemCard } from "./ItemCard";

export function ItemList({ itens, idEmEdicao = null, onEditar, onRemover }) {
  return (
    <section aria-labelledby="titulo-lista" className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between gap-2">
        <h2 id="titulo-lista" className="text-lg font-semibold text-slate-900">
          Itens
        </h2>
        <span className="text-sm text-slate-500" aria-live="polite">
          {itens.length === 1 ? "1 item" : `${itens.length} itens`}
        </span>
      </div>

      {itens.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-300 bg-white/60 p-8 text-center text-slate-500">
          Nenhum item cadastrado ainda.
        </p>
      ) : (
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
      )}
    </section>
  );
}
