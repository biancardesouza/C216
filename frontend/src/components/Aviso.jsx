const ESTILOS = {
  erro: "border-red-200 bg-red-50 text-red-800",
  sucesso: "border-emerald-200 bg-emerald-50 text-emerald-800",
  info: "border-slate-200 bg-white text-slate-600",
};

// Caixa de mensagem usada para carregamento, erros e confirmações.
export default function Aviso({ tipo = "info", children, acao }) {
  return (
    <div
      role={tipo === "erro" ? "alert" : "status"}
      className={`flex items-center justify-between gap-4 rounded-lg border px-4 py-3 text-sm ${ESTILOS[tipo]}`}
    >
      <span>{children}</span>
      {acao}
    </div>
  );
}
