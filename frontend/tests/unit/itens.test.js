import { describe, expect, it } from "vitest";
import { adicionarItem, removerItem, substituirItem } from "../../src/utils/itens";

const caderno = { id: 1, nome: "Caderno", descricao: "Capa dura" };
const caneta = { id: 2, nome: "Caneta", descricao: "Azul" };

describe("adicionarItem", () => {
  it("adiciona ao final sem alterar a lista original", () => {
    const original = [caderno];
    const resultado = adicionarItem(original, caneta);
    expect(resultado).toEqual([caderno, caneta]);
    expect(original).toEqual([caderno]);
  });
});

describe("substituirItem", () => {
  it("troca apenas o item com o mesmo id pela versão devolvida pela API", () => {
    const atualizado = { id: 2, nome: "Caneta preta", descricao: "Ponta fina" };
    expect(substituirItem([caderno, caneta], atualizado)).toEqual([caderno, atualizado]);
  });

  it("mantém a lista igual se o id não existir", () => {
    expect(substituirItem([caderno], { id: 9, nome: "Y", descricao: "Z" })).toEqual([caderno]);
  });
});

describe("removerItem", () => {
  it("remove o item com o id informado", () => {
    expect(removerItem([caderno, caneta], 1)).toEqual([caneta]);
  });

  it("não altera a lista se o id não existir", () => {
    expect(removerItem([caderno], 9)).toEqual([caderno]);
  });
});
