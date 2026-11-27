import Aviso from "./components/Aviso.jsx";
import ResumoEstoque from "./components/ResumoEstoque.jsx";
import TabelaProdutos from "./components/TabelaProdutos.jsx";
import { useProdutos } from "./hooks/useProdutos.js";

export default function App() {
  const { produtos, carregando, erro, recarregar } = useProdutos();

  return (
    <div className="min-h-screen">
      <header className="bg-slate-800 text-white">
        <div className="mx-auto max-w-5xl px-4 py-5">
          <h1 className="text-xl font-semibold">Controle de Estoque</h1>
          <p className="text-sm text-slate-300">Produtos, entradas e saídas</p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        {carregando && <Aviso>Carregando produtos...</Aviso>}

        {erro && (
          <Aviso
            tipo="erro"
            acao={
              <button
                type="button"
                onClick={recarregar}
                className="shrink-0 rounded-md border border-red-300 px-3 py-1 font-medium hover:bg-red-100"
              >
                Tentar novamente
              </button>
            }
          >
            {erro}
          </Aviso>
        )}

        {!carregando && !erro && (
          <>
            <ResumoEstoque produtos={produtos} />
            <TabelaProdutos produtos={produtos} />
          </>
        )}
      </main>
    </div>
  );
}
