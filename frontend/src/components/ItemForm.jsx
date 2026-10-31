import { useState } from "react";
import { DESCRICAO_MAX, NOME_MAX, possuiErros, validarItem } from "../utils/validacao";
import { CampoTexto } from "./CampoTexto";

export function ItemForm({ itens, itemEmEdicao = null, onSalvar, onCancelar }) {
  const [nome, setNome] = useState(itemEmEdicao?.nome ?? "");
  const [descricao, setDescricao] = useState(itemEmEdicao?.descricao ?? "");
  const [tentouEnviar, setTentouEnviar] = useState(false);

  const editando = itemEmEdicao !== null;
  const erros = validarItem({ nome, descricao }, itens, itemEmEdicao?.id ?? null);
  // Os erros só aparecem depois da primeira tentativa de envio, para não poluir o formulário vazio.
  const errosVisiveis = tentouEnviar ? erros : {};

  function handleSubmit(evento) {
    evento.preventDefault();
    setTentouEnviar(true);
    if (possuiErros(erros)) return;

    onSalvar({ nome, descricao });
    setNome("");
    setDescricao("");
    setTentouEnviar(false);
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-label={editando ? "Editar item" : "Novo item"}
      className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
    >
      <h2 className="text-lg font-semibold text-slate-900">
        {editando ? "Editar item" : "Novo item"}
      </h2>

      <CampoTexto
        id="nome"
        label="Nome"
        valor={nome}
        onChange={setNome}
        erro={errosVisiveis.nome}
        maximo={NOME_MAX}
      />
      <CampoTexto
        id="descricao"
        label="Descrição"
        valor={descricao}
        onChange={setDescricao}
        erro={errosVisiveis.descricao}
        maximo={DESCRICAO_MAX}
        multilinha
      />

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        {editando && (
          <button
            type="button"
            onClick={onCancelar}
            className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          className="rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white shadow-sm transition hover:bg-indigo-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
        >
          {editando ? "Salvar alterações" : "Adicionar item"}
        </button>
      </div>
    </form>
  );
}
