import { describe, expect, it } from "vitest";
import {
  DESCRICAO_MAX,
  NOME_MAX,
  NOME_MIN,
  possuiErros,
  validarDescricao,
  validarItem,
  validarNome,
} from "../../src/utils/validacao";

const itens = [{ id: "1", nome: "Caderno", descricao: "Capa dura" }];

describe("validarNome", () => {
  it("aceita um nome válido", () => {
    expect(validarNome("Caneta")).toBeNull();
  });

  it.each([
    ["vazio", ""],
    ["apenas espaços", "   "],
    ["indefinido", undefined],
  ])("rejeita nome %s", (_caso, nome) => {
    expect(validarNome(nome)).toBe("O nome é obrigatório.");
  });

  it("rejeita nome menor que o mínimo, ignorando espaços nas pontas", () => {
    expect(validarNome(`  ${"a".repeat(NOME_MIN - 1)}  `)).toMatch(/pelo menos/);
  });

  it("aceita nome com exatamente os limites mínimo e máximo", () => {
    expect(validarNome("a".repeat(NOME_MIN))).toBeNull();
    expect(validarNome("a".repeat(NOME_MAX))).toBeNull();
  });

  it("rejeita nome maior que o máximo", () => {
    expect(validarNome("a".repeat(NOME_MAX + 1))).toMatch(/no máximo/);
  });

  it("rejeita nome duplicado sem diferenciar maiúsculas", () => {
    expect(validarNome("  CADERNO ", itens)).toBe("Já existe um item com esse nome.");
  });

  it("permite manter o próprio nome ao editar", () => {
    expect(validarNome("Caderno", itens, "1")).toBeNull();
  });
});

describe("validarDescricao", () => {
  it("aceita uma descrição válida", () => {
    expect(validarDescricao("Azul, ponta fina")).toBeNull();
  });

  it("rejeita descrição vazia", () => {
    expect(validarDescricao("  ")).toBe("A descrição é obrigatória.");
  });

  it("respeita o limite de caracteres", () => {
    expect(validarDescricao("a".repeat(DESCRICAO_MAX))).toBeNull();
    expect(validarDescricao("a".repeat(DESCRICAO_MAX + 1))).toMatch(/no máximo/);
  });
});

describe("validarItem", () => {
  it("retorna objeto vazio para item válido", () => {
    const erros = validarItem({ nome: "Caneta", descricao: "Azul" }, itens);
    expect(erros).toEqual({});
    expect(possuiErros(erros)).toBe(false);
  });

  it("retorna os erros de cada campo inválido", () => {
    const erros = validarItem({ nome: "", descricao: "" });
    expect(Object.keys(erros)).toEqual(["nome", "descricao"]);
    expect(possuiErros(erros)).toBe(true);
  });
});
