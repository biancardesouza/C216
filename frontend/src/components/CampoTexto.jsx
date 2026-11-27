export default function CampoTexto({ id, rotulo, erro, ajuda, ...props }) {
  const idDaMensagem = `${id}-mensagem`;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-slate-700">
        {rotulo}
      </label>
      <input
        id={id}
        aria-invalid={erro ? "true" : undefined}
        aria-describedby={erro || ajuda ? idDaMensagem : undefined}
        className={`rounded-md border px-3 py-2 text-sm outline-none focus:ring-2 ${
          erro
            ? "border-red-400 focus:ring-red-200"
            : "border-slate-300 focus:border-slate-500 focus:ring-slate-200"
        }`}
        {...props}
      />
      {(erro || ajuda) && (
        <p id={idDaMensagem} className={`text-xs ${erro ? "text-red-600" : "text-slate-500"}`}>
          {erro || ajuda}
        </p>
      )}
    </div>
  );
}
