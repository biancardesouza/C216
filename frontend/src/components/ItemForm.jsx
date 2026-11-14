import { useState } from "react";
import { DESCRICAO_MAX, NOME_MAX, possuiErros, validarItem } from "../utils/validacao";
import { CampoTexto } from "./CampoTexto";

export function ItemForm({ itens, itemEmEdicao = null, onSalvar, onCancelar }) {
  const [nome, setNome] = useState(itemEmEdicao?.nome ?? "");
  const [descricao, setDescricao] = useState(itemEmEdicao?.descricao ?? "");
  const [tentouEnviar, setTentouEnviar] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erroEnvio, setErroEnvio] = useState(null);

  const editando = itemEmEdicao !== null;
  const erros = validarItem({ nome, descricao }, itens, itemEmEdicao?.id ?? null);
  // Os erros só aparecem depois da primeira tentativa de envio, para não poluir o formulário vazio.
  const errosVisiveis = tentouEnviar ? erros : {};

  function alterarNome(valor) {
    setNome(valor);
    setErroEnvio(null);
  }

  function alterarDescricao(valor) {
    setDescricao(valor);
    setErroEnvio(null);
  }

  async function handleSubmit(evento) {
    evento.preventDefault();
    setTentouEnviar(true);
    if (possuiErros(erros) || enviando) return;

    setEnviando(true);
    setErroEnvio(null);
    try {
      await onSalvar({ nome, descricao });
      setNome("");
      setDescricao("");
      setTentouEnviar(false);
    } catch (falha) {
      // Mantém o que foi digitado para o usuário corrigir e tentar de novo.
      setErroEnvio(falha.message);
    } finally {
      setEnviando(false);
    }
  }

  const textoBotao = editando ? "Salvar alterações" : "Adicionar item";

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-label={editando ? "Editar item" : "Novo item"}
      aria-busy={enviando}
      className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
    >
      <h2 className="text-lg font-semibold text-slate-900">
        {editando ? "Editar item" : "Novo item"}
      </h2>

      <CampoTexto
        id="nome"
        label="Nome"
        valor={nome}
        onChange={alterarNome}
        erro={errosVisiveis.nome}
        maximo={NOME_MAX}
      />
      <CampoTexto
        id="descricao"
        label="Descrição"
        valor={descricao}
        onChange={alterarDescricao}
        erro={errosVisiveis.descricao}
        maximo={DESCRICAO_MAX}
        multilinha
      />

      {erroEnvio && (
        <p
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {erroEnvio}
        </p>
      )}

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        {editando && (
          <button
            type="button"
            onClick={onCancelar}
            disabled={enviando}
            className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Cancelar
          </button>
        )}
        {/* O nome acessível não muda durante o envio; apenas o texto visível. */}
        <button
          type="submit"
          disabled={enviando}
          aria-label={textoBotao}
          className="rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white shadow-sm transition hover:bg-indigo-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {enviando ? "Salvando..." : textoBotao}
        </button>
      </div>
    </form>
  );
}
