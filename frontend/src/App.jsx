import { useState } from "react";
import { ItemForm } from "./components/ItemForm";
import { ItemList } from "./components/ItemList";
import { useItens } from "./hooks/useItens";

export default function App({ itensIniciais = [] }) {
  const { itens, adicionar, atualizar, remover } = useItens(itensIniciais);
  const [itemEmEdicao, setItemEmEdicao] = useState(null);

  function handleSalvar(dados) {
    if (itemEmEdicao) {
      atualizar(itemEmEdicao.id, dados);
      setItemEmEdicao(null);
    } else {
      adicionar(dados);
    }
  }

  function handleRemover(item) {
    remover(item.id);
    if (itemEmEdicao?.id === item.id) setItemEmEdicao(null);
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-5 sm:px-6">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Gerenciador de Itens</h1>
          <p className="mt-1 text-sm text-slate-600">
            Cadastre, edite e remova itens com nome e descrição.
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-5xl grid-cols-1 gap-6 px-4 py-6 sm:px-6 md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] md:items-start">
        <div className="md:sticky md:top-6">
          {/* A key remonta o formulário ao trocar o item em edição, reiniciando os campos. */}
          <ItemForm
            key={itemEmEdicao?.id ?? "novo"}
            itens={itens}
            itemEmEdicao={itemEmEdicao}
            onSalvar={handleSalvar}
            onCancelar={() => setItemEmEdicao(null)}
          />
        </div>
        <ItemList
          itens={itens}
          idEmEdicao={itemEmEdicao?.id ?? null}
          onEditar={setItemEmEdicao}
          onRemover={handleRemover}
        />
      </main>
    </div>
  );
}
