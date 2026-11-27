import { describe, expect, it } from "vitest";
import { calcularResumo, formatarDataHora, formatarMoeda } from "../../src/utils/estoque.js";

// O Intl usa espaço não separável entre "R$" e o valor.
const semEspacoEspecial = (texto) => texto.replace(/\s/g, " ");

describe("formatarMoeda", () => {
  it.each([
    ["2.50", "R$ 2,50"],
    [1234.5, "R$ 1.234,50"],
    [0, "R$ 0,00"],
  ])("formata %s como %s", (valor, esperado) => {
    expect(semEspacoEspecial(formatarMoeda(valor))).toBe(esperado);
  });
});

describe("calcularResumo", () => {
  it("retorna zeros para lista vazia", () => {
    expect(calcularResumo([])).toEqual({
      totalProdutos: 0,
      totalUnidades: 0,
      comEstoqueBaixo: 0,
      valorEmEstoque: 0,
    });
  });

  it("soma unidades, conta estoque baixo e calcula o valor total", () => {
    const produtos = [
      { preco: "2.50", quantidade: 10, estoque_baixo: false },
      { preco: "10.00", quantidade: 3, estoque_baixo: true },
      { preco: "7.90", quantidade: 0, estoque_baixo: true },
    ];

    expect(calcularResumo(produtos)).toEqual({
      totalProdutos: 3,
      totalUnidades: 13,
      comEstoqueBaixo: 2,
      valorEmEstoque: 55,
    });
  });
});

describe("formatarDataHora", () => {
  it("formata data e hora no padrão brasileiro", () => {
    const texto = formatarDataHora("2026-11-27T15:30:00");

    expect(texto).toMatch(/^27\/11\/2026,? 15:30$/);
  });
});
