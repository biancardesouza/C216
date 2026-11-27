import { useCallback, useEffect, useState } from "react";
import { listarMovimentacoes, registrarMovimentacao } from "../services/produtos.js";
import { formatarDataHora } from "../utils/estoque.js";
import { validarMovimentacao } from "../utils/validacao.js";
import Aviso from "./Aviso.jsx";
import CampoTexto from "./CampoTexto.jsx";

const VAZIO = { tipo: "entrada", quantidade: "", observacao: "" };

function Historico({ movimentacoes, carregando, erro }) {
  if (carregando) return <p className="text-sm text-slate-500">Carregando histórico...</p>;
  if (erro) return <Aviso tipo="erro">{erro}</Aviso>;
  if (movimentacoes.length === 0) {
    return <p className="text-sm text-slate-500">Nenhuma movimentação registrada.</p>;
  }

  return (
    <ul aria-label="Histórico de movimentações" className="divide-y divide-slate-100">
      {movimentacoes.map((m) => (
        <li key={m.id} className="flex items-start justify-between gap-3 py-2 text-sm">
          <div>
            <p className="font-medium">
              <span className={m.tipo === "entrada" ? "text-emerald-700" : "text-red-700"}>
                {m.tipo === "entrada" ? `+${m.quantidade}` : `−${m.quantidade}`}
              </span>{" "}
              {m.tipo === "entrada" ? "Entrada" : "Saída"}
            </p>
            {m.observacao && <p className="text-xs text-slate-500">{m.observacao}</p>}
          </div>
          <time dateTime={m.criado_em} className="shrink-0 text-xs text-slate-500">
            {formatarDataHora(m.criado_em)}
          </time>
        </li>
      ))}
    </ul>
  );
}

export default function PainelMovimentacoes({ produto, onRegistrada, onFechar }) {
  const [valores, setValores] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [erroApi, setErroApi] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [sucesso, setSucesso] = useState(null);

  const [movimentacoes, setMovimentacoes] = useState([]);
  const [carregandoHistorico, setCarregandoHistorico] = useState(true);
  const [erroHistorico, setErroHistorico] = useState(null);

  const carregarHistorico = useCallback(async () => {
    setErroHistorico(null);
    try {
      setMovimentacoes(await listarMovimentacoes(produto.id));
    } catch (e) {
      setErroHistorico(e.message);
    } finally {
      setCarregandoHistorico(false);
    }
  }, [produto.id]);

  useEffect(() => {
    carregarHistorico();
  }, [carregarHistorico]);

  function alterar(evento) {
    const { name, value } = evento.target;
    setValores((atuais) => ({ ...atuais, [name]: value }));
    setErros((atuais) => ({ ...atuais, [name]: undefined }));
  }

  async function enviar(evento) {
    evento.preventDefault();
    setSucesso(null);
    const encontrados = validarMovimentacao(valores);
    setErros(encontrados);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    setErroApi(null);
    try {
      await registrarMovimentacao(produto.id, valores);
      setSucesso(valores.tipo === "entrada" ? "Entrada registrada." : "Saída registrada.");
      setValores((atuais) => ({ ...VAZIO, tipo: atuais.tipo }));
      await Promise.all([carregarHistorico(), onRegistrada()]);
    } catch (e) {
      // Ex.: 409 quando a saída é maior que o saldo disponível.
      setErroApi(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section
      aria-label={`Movimentações de ${produto.nome}`}
      className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Movimentar {produto.nome}</h2>
          <p className="text-sm text-slate-500">
            <span className="font-mono">{produto.sku}</span> · Saldo atual:{" "}
            <strong data-testid="saldo-atual" className="text-slate-800">
              {produto.quantidade}
            </strong>{" "}
            unidade(s)
          </p>
        </div>
        <button
          type="button"
          onClick={onFechar}
          className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium hover:bg-slate-50"
        >
          Fechar
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <form
          onSubmit={enviar}
          noValidate
          aria-label="Registrar movimentação"
          className="space-y-4"
        >
          {erroApi && <Aviso tipo="erro">{erroApi}</Aviso>}
          {sucesso && <Aviso tipo="sucesso">{sucesso}</Aviso>}

          <fieldset className="flex gap-2">
            <legend className="mb-1 text-sm font-medium text-slate-700">Tipo</legend>
            {[
              ["entrada", "Entrada", "peer-checked:border-emerald-500 peer-checked:bg-emerald-50"],
              ["saida", "Saída", "peer-checked:border-red-500 peer-checked:bg-red-50"],
            ].map(([valor, rotulo, cores]) => (
              <label key={valor} className="flex-1 cursor-pointer">
                <input
                  type="radio"
                  name="tipo"
                  value={valor}
                  checked={valores.tipo === valor}
                  onChange={alterar}
                  className="peer sr-only"
                />
                <span
                  className={`block rounded-md border border-slate-300 px-3 py-2 text-center text-sm font-medium ${cores}`}
                >
                  {rotulo}
                </span>
              </label>
            ))}
          </fieldset>

          <CampoTexto
            id="quantidade"
            name="quantidade"
            rotulo="Quantidade"
            inputMode="numeric"
            value={valores.quantidade}
            onChange={alterar}
            erro={erros.quantidade}
          />
          <CampoTexto
            id="observacao"
            name="observacao"
            rotulo="Observação (opcional)"
            value={valores.observacao}
            onChange={alterar}
            erro={erros.observacao}
            placeholder="Ex.: compra do fornecedor, venda balcão"
          />

          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-60"
          >
            {enviando ? "Registrando..." : "Registrar"}
          </button>
        </form>

        <div>
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Histórico
          </h3>
          <Historico
            movimentacoes={movimentacoes}
            carregando={carregandoHistorico}
            erro={erroHistorico}
          />
        </div>
      </div>
    </section>
  );
}
