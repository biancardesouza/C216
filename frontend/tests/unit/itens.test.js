import { describe, expect, it } from "vitest";
import { adicionarItem, atualizarItem, criarItem, removerItem } from "../../src/utils/itens";

const caderno = { id: "1", nome: "Caderno", descricao: "Capa dura" };
const caneta = { id: "2", nome: "Caneta", descricao: "Azul" };

describe("criarItem", () => {
  it("gera um id e remove espaços das pontas", () => {
    const item = criarItem({ nome: "  Lápis ", descricao: " HB  " }, () => "abc");
    expect(item).toEqual({ id: "abc", nome: "Lápis", descricao: "HB" });
  });

  it("usa ids diferentes por padrão", () => {
    const a = criarItem({ nome: "A", descricao: "a" });
    const b = criarItem({ nome: "B", descricao: "b" });
    expect(a.id).not.toBe(b.id);
  });
});

describe("adicionarItem", () => {
  it("adiciona ao final sem alterar a lista original", () => {
    const original = [caderno];
    const resultado = adicionarItem(original, caneta);
    expect(resultado).toEqual([caderno, caneta]);
    expect(original).toEqual([caderno]);
  });
});

describe("atualizarItem", () => {
  it("atualiza apenas o item com o id informado", () => {
    const resultado = atualizarItem([caderno, caneta], "2", {
      nome: " Caneta preta ",
      descricao: "Ponta fina",
    });
    expect(resultado).toEqual([
      caderno,
      { id: "2", nome: "Caneta preta", descricao: "Ponta fina" },
    ]);
  });

  it("mantém a lista igual se o id não existir", () => {
    expect(atualizarItem([caderno], "x", { nome: "Y", descricao: "Z" })).toEqual([caderno]);
  });
});

describe("removerItem", () => {
  it("remove o item com o id informado", () => {
    expect(removerItem([caderno, caneta], "1")).toEqual([caneta]);
  });

  it("não altera a lista se o id não existir", () => {
    expect(removerItem([caderno], "x")).toEqual([caderno]);
  });
});
