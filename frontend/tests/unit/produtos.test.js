import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../src/services/api.js", () => ({ requisitar: vi.fn() }));

const { requisitar } = await import("../../src/services/api.js");
const servico = await import("../../src/services/produtos.js");

const FORMULARIO = {
  sku: "  can-001 ",
  nome: " Caneta azul ",
  categoria: "Papelaria ",
  preco: "2,50",
  estoque_minimo: "10",
};

const ESPERADO = {
  sku: "CAN-001",
  nome: "Caneta azul",
  categoria: "Papelaria",
  preco: "2.50",
  estoque_minimo: 10,
};

beforeEach(() => {
  requisitar.mockReset();
});

describe("serviço de produtos", () => {
  it("lista os produtos", () => {
    servico.listarProdutos();

    expect(requisitar).toHaveBeenCalledWith("/produtos");
  });

  it("cria produto convertendo os campos do formulário", () => {
    servico.criarProduto(FORMULARIO);

    expect(requisitar).toHaveBeenCalledWith("/produtos", { method: "POST", body: ESPERADO });
  });

  it("estoque mínimo vazio vira zero", () => {
    servico.criarProduto({ ...FORMULARIO, estoque_minimo: "" });

    expect(requisitar.mock.calls[0][1].body.estoque_minimo).toBe(0);
  });

  it("atualiza produto pelo id", () => {
    servico.atualizarProduto(7, FORMULARIO);

    expect(requisitar).toHaveBeenCalledWith("/produtos/7", { method: "PUT", body: ESPERADO });
  });

  it("exclui produto pelo id", () => {
    servico.excluirProduto(7);

    expect(requisitar).toHaveBeenCalledWith("/produtos/7", { method: "DELETE" });
  });
});

describe("serviço de movimentações", () => {
  it("lista o histórico do produto", () => {
    servico.listarMovimentacoes(3);

    expect(requisitar).toHaveBeenCalledWith("/produtos/3/movimentacoes");
  });

  it("registra movimentação com quantidade numérica", () => {
    servico.registrarMovimentacao(3, { tipo: "saida", quantidade: "4", observacao: " Venda " });

    expect(requisitar).toHaveBeenCalledWith("/produtos/3/movimentacoes", {
      method: "POST",
      body: { tipo: "saida", quantidade: 4, observacao: "Venda" },
    });
  });

  it("observação em branco é enviada como null", () => {
    servico.registrarMovimentacao(3, { tipo: "entrada", quantidade: "1", observacao: "  " });

    expect(requisitar.mock.calls[0][1].body.observacao).toBeNull();
  });
});
