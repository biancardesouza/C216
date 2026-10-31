export function CampoTexto({ id, label, valor, onChange, erro, maximo, multilinha = false }) {
  const idErro = `${id}-erro`;
  const idContador = `${id}-contador`;
  const Elemento = multilinha ? "textarea" : "input";

  const classes = [
    "w-full rounded-lg border bg-white px-3 py-2 text-slate-900 shadow-sm outline-none transition",
    "focus:ring-2 focus:ring-indigo-500/40",
    erro ? "border-red-500 focus:border-red-500" : "border-slate-300 focus:border-indigo-500",
    multilinha ? "min-h-28 resize-y" : "",
  ].join(" ");

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between gap-2">
        <label htmlFor={id} className="text-sm font-medium text-slate-700">
          {label}
        </label>
        <span id={idContador} className="text-xs text-slate-500">
          {valor.length}/{maximo}
        </span>
      </div>
      <Elemento
        id={id}
        name={id}
        value={valor}
        onChange={(evento) => onChange(evento.target.value)}
        aria-invalid={erro ? "true" : "false"}
        aria-describedby={erro ? `${idErro} ${idContador}` : idContador}
        className={classes}
        {...(multilinha ? { rows: 4 } : { type: "text" })}
      />
      {erro && (
        <p id={idErro} className="text-sm text-red-600">
          {erro}
        </p>
      )}
    </div>
  );
}
