// Endereço da API visto pelo navegador. Definido no build (VITE_API_URL).
export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/+$/,
  "",
);

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const MENSAGENS_POR_STATUS = {
  404: "Item não encontrado.",
  409: "Já existe um item com esse nome.",
  422: "Dados inválidos. Verifique os campos e tente novamente.",
};

async function mensagemDeErro(resposta) {
  try {
    const corpo = await resposta.json();
    // O FastAPI devolve { detail: "mensagem" } nos erros de regra de negócio.
    if (typeof corpo?.detail === "string") return corpo.detail;
  } catch {
    // Corpo vazio ou que não é JSON: usa a mensagem padrão do status.
  }
  return MENSAGENS_POR_STATUS[resposta.status] ?? `Erro inesperado na API (${resposta.status}).`;
}

async function requisitar(caminho, { method = "GET", body } = {}) {
  const opcoes = { method, headers: { Accept: "application/json" } };
  if (body !== undefined) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(body);
  }

  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  } catch {
    throw new ApiError("Não foi possível conectar à API. Tente novamente.", 0);
  }

  if (!resposta.ok) throw new ApiError(await mensagemDeErro(resposta), resposta.status);
  return resposta.status === 204 ? null : resposta.json();
}

export function listItems() {
  return requisitar("/items/");
}

export function createItem({ nome, descricao }) {
  return requisitar("/items/", {
    method: "POST",
    body: { nome: nome.trim(), descricao: descricao.trim() },
  });
}

export function updateItem(id, { nome, descricao }) {
  return requisitar(`/items/${id}`, {
    method: "PUT",
    body: { nome: nome.trim(), descricao: descricao.trim() },
  });
}

export function deleteItem(id) {
  return requisitar(`/items/${id}`, { method: "DELETE" });
}
