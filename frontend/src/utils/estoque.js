const formatadorDeMoeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function formatarMoeda(valor) {
  return formatadorDeMoeda.format(Number(valor));
}

// Números exibidos nos cartões do topo da página.
export function calcularResumo(produtos) {
  return {
    totalProdutos: produtos.length,
    totalUnidades: produtos.reduce((soma, p) => soma + p.quantidade, 0),
    comEstoqueBaixo: produtos.filter((p) => p.estoque_baixo).length,
    valorEmEstoque: produtos.reduce((soma, p) => soma + Number(p.preco) * p.quantidade, 0),
  };
}
