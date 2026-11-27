import { afterEach, describe, expect, it, vi } from "vitest";
import { API_URL, ApiError, requisitar } from "../../src/services/api.js";

function respostaFalsa(status, corpo) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: corpo === undefined ? () => Promise.reject(new Error("sem corpo")) : async () => corpo,
  };
}

function simularFetch(resposta) {
  const fetchFalso = vi.fn().mockResolvedValue(resposta);
  vi.stubGlobal("fetch", fetchFalso);
  return fetchFalso;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("requisitar", () => {
  it("faz GET na URL da API e devolve o JSON", async () => {
    const fetchFalso = simularFetch(respostaFalsa(200, [{ id: 1 }]));

    const dados = await requisitar("/produtos");

    expect(dados).toEqual([{ id: 1 }]);
    expect(fetchFalso).toHaveBeenCalledWith(
      `${API_URL}/produtos`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("envia o corpo como JSON com o cabeçalho certo", async () => {
    const fetchFalso = simularFetch(respostaFalsa(201, { id: 1 }));

    await requisitar("/produtos", { method: "POST", body: { nome: "Caneta" } });

    const [, opcoes] = fetchFalso.mock.calls[0];
    expect(opcoes.headers["Content-Type"]).toBe("application/json");
    expect(opcoes.body).toBe(JSON.stringify({ nome: "Caneta" }));
  });

  it("devolve null quando a resposta é 204", async () => {
    simularFetch(respostaFalsa(204));

    await expect(requisitar("/produtos/1", { method: "DELETE" })).resolves.toBeNull();
  });

  it("usa a mensagem da API (detail) quando há erro de negócio", async () => {
    simularFetch(respostaFalsa(409, { detail: "Estoque insuficiente." }));

    await expect(requisitar("/x")).rejects.toMatchObject({
      name: "ApiError",
      status: 409,
      message: "Estoque insuficiente.",
    });
  });

  it("usa uma mensagem padrão quando o detail não é texto (422)", async () => {
    simularFetch(respostaFalsa(422, { detail: [{ msg: "campo obrigatório" }] }));

    await expect(requisitar("/x")).rejects.toThrow("Dados inválidos");
  });

  it("usa uma mensagem genérica para status desconhecido sem corpo", async () => {
    simularFetch(respostaFalsa(500));

    await expect(requisitar("/x")).rejects.toThrow("Erro inesperado na API (500).");
  });

  it("lança ApiError com status 0 quando a API está fora do ar", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const erro = await requisitar("/x").catch((e) => e);

    expect(erro).toBeInstanceOf(ApiError);
    expect(erro.status).toBe(0);
    expect(erro.message).toMatch("Não foi possível conectar");
  });
});
