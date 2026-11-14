import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App";
import { criarApiFalsa, pendente, resposta } from "../helpers/api";

const caderno = { id: 1, nome: "Caderno", descricao: "Capa dura" };
const caneta = { id: 2, nome: "Caneta", descricao: "Azul" };

function usarApi(fetchMock) {
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function renderizarCarregado() {
  render(<App />);
  await screen.findByRole("region", { name: "Itens" });
  expect(await screen.findByText(/\d+ ite(m|ns)$/)).toBeInTheDocument();
}

async function cadastrar(user, nome, descricao) {
  await user.type(screen.getByLabelText("Nome"), nome);
  await user.type(screen.getByLabelText("Descrição"), descricao);
  await user.click(screen.getByRole("button", { name: "Adicionar item" }));
}

function lista() {
  return screen.getByRole("region", { name: "Itens" });
}

function chamadas(fetchMock, metodo) {
  return fetchMock.mock.calls.filter(([, opcoes]) => (opcoes?.method ?? "GET") === metodo);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("carregamento da lista", () => {
  it("mostra o estado de carregamento enquanto a API não responde", () => {
    usarApi(vi.fn(() => pendente()));
    render(<App />);

    expect(screen.getByRole("status")).toHaveTextContent("Carregando itens...");
    expect(lista()).toHaveAttribute("aria-busy", "true");
    expect(screen.queryByText("Nenhum item cadastrado ainda.")).not.toBeInTheDocument();
  });

  it("exibe os itens devolvidos pela API", async () => {
    const fetchMock = usarApi(criarApiFalsa([caderno, caneta]));
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Caneta" })).toBeInTheDocument();
    expect(within(lista()).getByText("2 itens")).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/items/", expect.anything());
  });

  it("exibe o estado vazio quando a API não tem itens", async () => {
    usarApi(criarApiFalsa());
    render(<App />);

    expect(await screen.findByText("Nenhum item cadastrado ainda.")).toBeInTheDocument();
    expect(within(lista()).getByText("0 itens")).toBeInTheDocument();
  });

  it("mostra mensagem de erro quando a API está fora do ar e permite tentar de novo", async () => {
    const fetchMock = usarApi(vi.fn());
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    fetchMock.mockResolvedValueOnce(resposta(200, [caderno]));
    const user = userEvent.setup();
    render(<App />);

    const alerta = await screen.findByRole("alert");
    expect(alerta).toHaveTextContent("Não foi possível carregar os itens.");
    expect(alerta).toHaveTextContent("Não foi possível conectar à API.");

    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await screen.findByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("mostra a mensagem de erro devolvida pela API", async () => {
    usarApi(vi.fn().mockResolvedValue(resposta(500, { detail: "Banco indisponível" })));
    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Banco indisponível");
  });
});

describe("cadastro", () => {
  it("envia o item para a API, exibe na lista e limpa o formulário", async () => {
    const fetchMock = usarApi(criarApiFalsa());
    const user = userEvent.setup();
    await renderizarCarregado();

    await cadastrar(user, "Caderno", "Capa dura, 96 folhas");

    const item = await within(lista()).findByRole("listitem");
    expect(within(item).getByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(within(item).getByText("Capa dura, 96 folhas")).toBeInTheDocument();
    expect(within(lista()).getByText("1 item")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(screen.getByLabelText("Descrição")).toHaveValue("");

    const [[url, opcoes]] = chamadas(fetchMock, "POST");
    expect(url).toBe("http://localhost:8000/items/");
    expect(JSON.parse(opcoes.body)).toEqual({ nome: "Caderno", descricao: "Capa dura, 96 folhas" });
  });

  it("desabilita o botão enquanto salva", async () => {
    const fetchMock = usarApi(vi.fn());
    fetchMock.mockResolvedValueOnce(resposta(200, []));
    fetchMock.mockReturnValueOnce(pendente());
    const user = userEvent.setup();
    await renderizarCarregado();

    await cadastrar(user, "Caderno", "Capa dura");

    const botao = screen.getByRole("button", { name: "Adicionar item" });
    expect(botao).toBeDisabled();
    expect(botao).toHaveTextContent("Salvando...");
    expect(screen.getByRole("form", { name: "Novo item" })).toHaveAttribute("aria-busy", "true");
  });

  it("mostra o erro da API e mantém os campos preenchidos", async () => {
    const fetchMock = usarApi(vi.fn());
    fetchMock.mockResolvedValueOnce(resposta(200, []));
    fetchMock.mockResolvedValueOnce(resposta(409, { detail: "Já existe um item com esse nome." }));
    const user = userEvent.setup();
    await renderizarCarregado();

    await cadastrar(user, "Caderno", "Capa dura");

    expect(await screen.findByRole("alert")).toHaveTextContent("Já existe um item com esse nome.");
    expect(screen.getByLabelText("Nome")).toHaveValue("Caderno");
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Adicionar item" })).toBeEnabled();
  });

  it("limpa o erro da API quando o usuário altera o campo", async () => {
    const fetchMock = usarApi(vi.fn());
    fetchMock.mockResolvedValueOnce(resposta(200, []));
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    const user = userEvent.setup();
    await renderizarCarregado();

    await cadastrar(user, "Caderno", "Capa dura");
    expect(await screen.findByRole("alert")).toBeInTheDocument();

    await user.type(screen.getByLabelText("Nome"), "s");

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("valida os campos sem chamar a API", async () => {
    const fetchMock = usarApi(criarApiFalsa());
    const user = userEvent.setup();
    await renderizarCarregado();

    await user.click(screen.getByRole("button", { name: "Adicionar item" }));

    expect(screen.getByText("O nome é obrigatório.")).toBeInTheDocument();
    expect(screen.getByText("A descrição é obrigatória.")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "true");
    expect(chamadas(fetchMock, "POST")).toHaveLength(0);
  });

  it("impede nomes duplicados já carregados da API", async () => {
    const fetchMock = usarApi(criarApiFalsa([caderno]));
    const user = userEvent.setup();
    await renderizarCarregado();

    await cadastrar(user, "caderno", "Outro caderno");

    expect(screen.getByText("Já existe um item com esse nome.")).toBeInTheDocument();
    expect(within(lista()).getAllByRole("listitem")).toHaveLength(1);
    expect(chamadas(fetchMock, "POST")).toHaveLength(0);
  });
});

describe("edição e remoção", () => {
  it("edita um item pela API", async () => {
    const fetchMock = usarApi(criarApiFalsa([caderno]));
    const user = userEvent.setup();
    await renderizarCarregado();

    await user.click(screen.getByRole("button", { name: "Editar Caderno" }));
    const form = screen.getByRole("form", { name: "Editar item" });
    const nome = within(form).getByLabelText("Nome");
    expect(nome).toHaveValue("Caderno");

    await user.clear(nome);
    await user.type(nome, "Caderno universitário");
    await user.click(within(form).getByRole("button", { name: "Salvar alterações" }));

    expect(
      await screen.findByRole("heading", { name: "Caderno universitário" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("form", { name: "Novo item" })).toBeInTheDocument();
    expect(chamadas(fetchMock, "PUT")[0][0]).toBe("http://localhost:8000/items/1");
  });

  it("cancela a edição sem chamar a API", async () => {
    const fetchMock = usarApi(criarApiFalsa([caderno]));
    const user = userEvent.setup();
    await renderizarCarregado();

    await user.click(screen.getByRole("button", { name: "Editar Caderno" }));
    await user.type(screen.getByLabelText("Nome"), " alterado");
    await user.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(screen.getByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(chamadas(fetchMock, "PUT")).toHaveLength(0);
  });

  it("remove um item pela API", async () => {
    const fetchMock = usarApi(criarApiFalsa([caderno, caneta]));
    const user = userEvent.setup();
    await renderizarCarregado();

    await user.click(screen.getByRole("button", { name: "Remover Caderno" }));

    expect(await within(lista()).findByText("1 item")).toBeInTheDocument();
    expect(screen.queryByText("Caderno")).not.toBeInTheDocument();
    expect(screen.getByText("Caneta")).toBeInTheDocument();
    expect(chamadas(fetchMock, "DELETE")[0][0]).toBe("http://localhost:8000/items/1");
  });

  it("mantém o item e mostra erro quando a remoção falha", async () => {
    const fetchMock = usarApi(vi.fn());
    fetchMock.mockResolvedValueOnce(resposta(200, [caderno]));
    fetchMock.mockResolvedValueOnce(resposta(404, { detail: "Item 1 não encontrado" }));
    const user = userEvent.setup();
    await renderizarCarregado();

    await user.click(screen.getByRole("button", { name: "Remover Caderno" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível remover o item. Item 1 não encontrado",
    );
    expect(screen.getByRole("heading", { name: "Caderno" })).toBeInTheDocument();
  });
});
