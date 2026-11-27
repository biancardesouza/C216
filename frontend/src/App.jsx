import { useState } from "react";
import Aviso from "./components/Aviso.jsx";
import PainelMovimentacoes from "./components/PainelMovimentacoes.jsx";
import ProdutoForm from "./components/ProdutoForm.jsx";
import ResumoEstoque from "./components/ResumoEstoque.jsx";
import TabelaProdutos from "./components/TabelaProdutos.jsx";
import { useProdutos } from "./hooks/useProdutos.js";
import { atualizarProduto, criarProduto, excluirProduto } from "./services/produtos.js";

// formulario: null (fechado), { produto: null } (novo) ou { produto } (edição).
export default function App() {
  const { produtos, carregando, erro, recarregar } = useProdutos();
  const [formulario, setFormulario] = useState(null);
  const [mensagem, setMensagem] = useState(null);
  // Guarda só o id: o produto vem da lista, então o saldo exibido no painel
  // se atualiza sozinho quando a lista é recarregada após uma movimentação.
  const [idMovimentando, setIdMovimentando] = useState(null);
  const produtoMovimentando = produtos.find((p) => p.id === idMovimentando);
  // Só mostra "Carregando" na primeira busca; nas recargas a tabela fica visível.
  const primeiraCarga = carregando && produtos.length === 0;

  function abrirFormulario(produto = null) {
    setMensagem(null);
    setIdMovimentando(null);
    setFormulario({ produto });
  }

  function abrirMovimentacoes(produto) {
    setMensagem(null);
    setFormulario(null);
    setIdMovimentando(produto.id);
  }

  async function salvar(valores) {
    const produto = formulario.produto;
    if (produto) {
      await atualizarProduto(produto.id, valores);
      setMensagem({ tipo: "sucesso", texto: "Produto atualizado." });
    } else {
      await criarProduto(valores);
      setMensagem({ tipo: "sucesso", texto: "Produto cadastrado." });
    }
    setFormulario(null);
    await recarregar();
  }

  async function excluir(produto) {
    setMensagem(null);
    try {
      await excluirProduto(produto.id);
      setMensagem({ tipo: "sucesso", texto: `${produto.nome} foi excluído.` });
      await recarregar();
    } catch (e) {
      // Ex.: 409 quando o produto ainda tem unidades em estoque.
      setMensagem({ tipo: "erro", texto: e.message });
    }
  }

  return (
    <div className="min-h-screen">
      <header className="bg-slate-800 text-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-5">
          <div>
            <h1 className="text-xl font-semibold">Controle de Estoque</h1>
            <p className="text-sm text-slate-300">Produtos, entradas e saídas</p>
          </div>
          {!formulario && (
            <button
              type="button"
              onClick={() => abrirFormulario()}
              className="rounded-md bg-white px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
            >
              Novo produto
            </button>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        {mensagem && <Aviso tipo={mensagem.tipo}>{mensagem.texto}</Aviso>}

        {formulario && (
          <ProdutoForm
            key={formulario.produto?.id ?? "novo"}
            produto={formulario.produto}
            onSalvar={salvar}
            onCancelar={() => setFormulario(null)}
          />
        )}

        {produtoMovimentando && (
          <PainelMovimentacoes
            key={produtoMovimentando.id}
            produto={produtoMovimentando}
            onRegistrada={recarregar}
            onFechar={() => setIdMovimentando(null)}
          />
        )}

        {primeiraCarga && <Aviso>Carregando produtos...</Aviso>}

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

        {!primeiraCarga && !erro && (
          <>
            <ResumoEstoque produtos={produtos} />
            <TabelaProdutos
              produtos={produtos}
              onMovimentar={abrirMovimentacoes}
              onEditar={abrirFormulario}
              onExcluir={excluir}
            />
          </>
        )}
      </main>
    </div>
  );
}
