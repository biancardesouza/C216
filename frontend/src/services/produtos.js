import { requisitar } from "./api.js";

// Converte os valores do formulário (sempre texto) no formato que a API espera.
function paraApi({ sku, nome, categoria, preco, estoque_minimo }) {
  return {
    sku: sku.trim().toUpperCase(),
    nome: nome.trim(),
    categoria: categoria.trim(),
    preco: String(preco).replace(",", "."),
    estoque_minimo: Number(estoque_minimo || 0),
  };
}

export function listarProdutos() {
  return requisitar("/produtos");
}

export function criarProduto(dados) {
  return requisitar("/produtos", { method: "POST", body: paraApi(dados) });
}

export function atualizarProduto(id, dados) {
  return requisitar(`/produtos/${id}`, { method: "PUT", body: paraApi(dados) });
}

export function excluirProduto(id) {
  return requisitar(`/produtos/${id}`, { method: "DELETE" });
}

export function listarMovimentacoes(produtoId) {
  return requisitar(`/produtos/${produtoId}/movimentacoes`);
}

export function registrarMovimentacao(produtoId, { tipo, quantidade, observacao = "" }) {
  return requisitar(`/produtos/${produtoId}/movimentacoes`, {
    method: "POST",
    body: { tipo, quantidade: Number(quantidade), observacao: observacao.trim() || null },
  });
}
