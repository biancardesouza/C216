import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  API_URL,
  ApiError,
  createItem,
  deleteItem,
  listItems,
  updateItem,
} from "../../src/services/items";
import { resposta } from "../helpers/api";

const caderno = { id: 1, nome: "Caderno", descricao: "Capa dura" };

describe("serviço de itens", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchMock.mockReset();
  });

  it("usa a API local por padrão", () => {
    expect(API_URL).toBe("http://localhost:8000");
  });

  describe("listItems", () => {
    it("faz GET em /items/ e devolve a lista", async () => {
      fetchMock.mockResolvedValueOnce(resposta(200, [caderno]));

      await expect(listItems()).resolves.toEqual([caderno]);
      expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/items/", {
        method: "GET",
        headers: { Accept: "application/json" },
      });
    });

    it("lança ApiError quando a API não responde", async () => {
      fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));

      const erro = await listItems().catch((falha) => falha);

      expect(erro).toBeInstanceOf(ApiError);
      expect(erro.status).toBe(0);
      expect(erro.message).toBe("Não foi possível conectar à API. Tente novamente.");
    });

    it("usa uma mensagem padrão quando o erro não tem detail", async () => {
      fetchMock.mockResolvedValueOnce(resposta(500));

      await expect(listItems()).rejects.toThrow("Erro inesperado na API (500).");
    });
  });

  describe("createItem", () => {
    it("envia POST com JSON e os campos sem espaços nas pontas", async () => {
      fetchMock.mockResolvedValueOnce(resposta(201, caderno));

      await expect(createItem({ nome: " Caderno ", descricao: "Capa dura " })).resolves.toEqual(
        caderno,
      );

      const [url, opcoes] = fetchMock.mock.calls[0];
      expect(url).toBe("http://localhost:8000/items/");
      expect(opcoes.method).toBe("POST");
      expect(opcoes.headers["Content-Type"]).toBe("application/json");
      expect(JSON.parse(opcoes.body)).toEqual({ nome: "Caderno", descricao: "Capa dura" });
    });

    it("repassa a mensagem de conflito do backend", async () => {
      fetchMock.mockResolvedValueOnce(
        resposta(409, { detail: "Já existe um item com esse nome." }),
      );

      const erro = await createItem({ nome: "Caderno", descricao: "x" }).catch((falha) => falha);

      expect(erro.status).toBe(409);
      expect(erro.message).toBe("Já existe um item com esse nome.");
    });

    it("traduz erros de validação (detail em lista) em uma mensagem legível", async () => {
      fetchMock.mockResolvedValueOnce(resposta(422, { detail: [{ loc: ["body", "nome"] }] }));

      await expect(createItem({ nome: "ab", descricao: "x" })).rejects.toThrow(
        "Dados inválidos. Verifique os campos e tente novamente.",
      );
    });
  });

  describe("updateItem", () => {
    it("envia PUT para /items/{id}", async () => {
      const atualizado = { ...caderno, nome: "Agenda" };
      fetchMock.mockResolvedValueOnce(resposta(200, atualizado));

      await expect(updateItem(1, { nome: "Agenda", descricao: "Capa dura" })).resolves.toEqual(
        atualizado,
      );
      expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:8000/items/1");
      expect(fetchMock.mock.calls[0][1].method).toBe("PUT");
    });
  });

  describe("deleteItem", () => {
    it("envia DELETE e aceita resposta 204 sem corpo", async () => {
      fetchMock.mockResolvedValueOnce(resposta(204));

      await expect(deleteItem(1)).resolves.toBeNull();
      expect(fetchMock.mock.calls[0][1]).toEqual({
        method: "DELETE",
        headers: { Accept: "application/json" },
      });
    });

    it("lança erro 404 quando o item não existe", async () => {
      fetchMock.mockResolvedValueOnce(resposta(404, { detail: "Item 9 não encontrado" }));

      await expect(deleteItem(9)).rejects.toMatchObject({
        status: 404,
        message: "Item 9 não encontrado",
      });
    });
  });
});
