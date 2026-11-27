// Endereço da API visto pelo navegador, definido no build pela VITE_API_URL.
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

const MENSAGEM_PADRAO_POR_STATUS = {
  404: "Registro não encontrado.",
  409: "A operação conflita com os dados atuais.",
  422: "Dados inválidos. Confira os campos e tente de novo.",
};

async function extrairMensagem(resposta) {
  try {
    const corpo = await resposta.json();
    // Regras de negócio da API respondem { detail: "mensagem em português" }.
    if (typeof corpo?.detail === "string") return corpo.detail;
  } catch {
    // Sem corpo JSON: cai na mensagem padrão do status.
  }
  return (
    MENSAGEM_PADRAO_POR_STATUS[resposta.status] ?? `Erro inesperado na API (${resposta.status}).`
  );
}

export async function requisitar(caminho, { method = "GET", body } = {}) {
  const opcoes = { method, headers: { Accept: "application/json" } };
  if (body !== undefined) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(body);
  }

  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  } catch {
    throw new ApiError("Não foi possível conectar à API. Verifique se ela está no ar.", 0);
  }

  if (!resposta.ok) throw new ApiError(await extrairMensagem(resposta), resposta.status);
  return resposta.status === 204 ? null : resposta.json();
}
