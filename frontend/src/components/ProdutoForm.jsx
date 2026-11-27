import { useState } from "react";
import { validarProduto } from "../utils/validacao.js";
import Aviso from "./Aviso.jsx";
import CampoTexto from "./CampoTexto.jsx";

const VAZIO = { sku: "", nome: "", categoria: "", preco: "", estoque_minimo: "0" };

function valoresIniciais(produto) {
  if (!produto) return VAZIO;
  return {
    sku: produto.sku,
    nome: produto.nome,
    categoria: produto.categoria,
    preco: String(produto.preco).replace(".", ","),
    estoque_minimo: String(produto.estoque_minimo),
  };
}

export default function ProdutoForm({ produto, onSalvar, onCancelar }) {
  const editando = Boolean(produto);
  const [valores, setValores] = useState(() => valoresIniciais(produto));
  const [erros, setErros] = useState({});
  const [erroApi, setErroApi] = useState(null);
  const [enviando, setEnviando] = useState(false);

  function alterar(evento) {
    const { name, value } = evento.target;
    setValores((atuais) => ({ ...atuais, [name]: value }));
    setErros((atuais) => ({ ...atuais, [name]: undefined }));
  }

  async function enviar(evento) {
    evento.preventDefault();
    const encontrados = validarProduto(valores);
    setErros(encontrados);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    setErroApi(null);
    try {
      await onSalvar(valores);
    } catch (e) {
      // Erros de regra da API (ex.: SKU duplicado) aparecem dentro do formulário.
      setErroApi(e.message);
      setEnviando(false);
    }
  }

  return (
    <form
      onSubmit={enviar}
      noValidate
      aria-label={editando ? "Editar produto" : "Novo produto"}
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="text-lg font-semibold">
        {editando ? `Editar ${produto.nome}` : "Novo produto"}
      </h2>

      {erroApi && <Aviso tipo="erro">{erroApi}</Aviso>}

      <div className="grid gap-4 sm:grid-cols-2">
        <CampoTexto
          id="sku"
          name="sku"
          rotulo="SKU"
          value={valores.sku}
          onChange={alterar}
          erro={erros.sku}
          placeholder="CAN-001"
        />
        <CampoTexto
          id="nome"
          name="nome"
          rotulo="Nome"
          value={valores.nome}
          onChange={alterar}
          erro={erros.nome}
          placeholder="Caneta azul"
        />
        <CampoTexto
          id="categoria"
          name="categoria"
          rotulo="Categoria"
          value={valores.categoria}
          onChange={alterar}
          erro={erros.categoria}
          placeholder="Papelaria"
        />
        <CampoTexto
          id="preco"
          name="preco"
          rotulo="Preço (R$)"
          inputMode="decimal"
          value={valores.preco}
          onChange={alterar}
          erro={erros.preco}
          placeholder="2,50"
        />
        <CampoTexto
          id="estoque_minimo"
          name="estoque_minimo"
          rotulo="Estoque mínimo"
          inputMode="numeric"
          value={valores.estoque_minimo}
          onChange={alterar}
          erro={erros.estoque_minimo}
          ajuda="Abaixo ou igual a isso, o produto aparece como estoque baixo."
        />
      </div>

      {!editando && (
        <p className="text-xs text-slate-500">
          O produto começa com quantidade zero. Use “Entrada” na tabela para abastecer.
        </p>
      )}

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancelar}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={enviando}
          className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-60"
        >
          {enviando ? "Salvando..." : editando ? "Salvar alterações" : "Cadastrar produto"}
        </button>
      </div>
    </form>
  );
}
