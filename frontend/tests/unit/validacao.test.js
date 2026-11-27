import { describe, expect, it } from "vitest";
import { validarProduto } from "../../src/utils/validacao.js";

const VALIDO = {
  sku: "CAN-001",
  nome: "Caneta azul",
  categoria: "Papelaria",
  preco: "2,50",
  estoque_minimo: "10",
};

describe("validarProduto", () => {
  it("não retorna erros para dados válidos", () => {
    expect(validarProduto(VALIDO)).toEqual({});
  });

  it.each([
    ["sku", "can-001"],
    ["preco", "2.5"],
    ["preco", "10"],
    ["estoque_minimo", ""],
    ["estoque_minimo", "0"],
  ])("aceita %s = %j", (campo, valor) => {
    expect(validarProduto({ ...VALIDO, [campo]: valor })).toEqual({});
  });

  it.each([
    ["sku", "AB"],
    ["sku", "CAN 001"],
    ["sku", "CAN_001"],
    ["nome", " "],
    ["nome", "x".repeat(101)],
    ["categoria", "A"],
    ["preco", ""],
    ["preco", "0"],
    ["preco", "-1"],
    ["preco", "2,555"],
    ["preco", "abc"],
    ["estoque_minimo", "-1"],
    ["estoque_minimo", "1,5"],
  ])("rejeita %s = %j", (campo, valor) => {
    const erros = validarProduto({ ...VALIDO, [campo]: valor });

    expect(Object.keys(erros)).toEqual([campo]);
  });
});
