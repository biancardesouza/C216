import { vi } from "vitest";

// Imita o objeto Response devolvido pelo fetch, apenas com o que o serviço usa.
export function resposta(status, corpo) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => {
      if (corpo === undefined) throw new SyntaxError("Unexpected end of JSON input");
      return corpo;
    },
  };
}

// Promessa que nunca resolve: mantém a tela no estado de carregamento.
export function pendente() {
  return new Promise(() => {});
}

// fetch falso que se comporta como a API /items/ do backend, guardando os itens em memória.
export function criarApiFalsa(itensIniciais = []) {
  let itens = itensIniciais.map((item) => ({ ...item }));
  let proximoId = itens.reduce((maior, item) => Math.max(maior, item.id), 0) + 1;

  const nomeEmUso = (nome, idIgnorado = null) =>
    itens.some((item) => item.id !== idIgnorado && item.nome.toLowerCase() === nome.toLowerCase());

  return vi.fn(async (url, opcoes = {}) => {
    const { pathname } = new URL(url);
    const metodo = opcoes.method ?? "GET";
    const corpo = opcoes.body ? JSON.parse(opcoes.body) : null;

    if (pathname === "/items/") {
      if (metodo === "GET") return resposta(200, itens);
      if (metodo === "POST") {
        if (nomeEmUso(corpo.nome)) {
          return resposta(409, { detail: "Já existe um item com esse nome." });
        }
        const item = { id: proximoId++, ...corpo };
        itens = [...itens, item];
        return resposta(201, item);
      }
    }

    const id = Number(pathname.split("/")[2]);
    if (!itens.some((item) => item.id === id)) {
      return resposta(404, { detail: `Item ${id} não encontrado` });
    }
    if (metodo === "PUT") {
      if (nomeEmUso(corpo.nome, id)) {
        return resposta(409, { detail: "Já existe um item com esse nome." });
      }
      const item = { id, ...corpo };
      itens = itens.map((atual) => (atual.id === id ? item : atual));
      return resposta(200, item);
    }
    if (metodo === "DELETE") {
      itens = itens.filter((item) => item.id !== id);
      return resposta(204);
    }
    return resposta(405, { detail: "Method Not Allowed" });
  });
}
