import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App";

async function cadastrar(user, nome, descricao) {
  await user.type(screen.getByLabelText("Nome"), nome);
  await user.type(screen.getByLabelText("Descrição"), descricao);
  await user.click(screen.getByRole("button", { name: "Adicionar item" }));
}

function lista() {
  return screen.getByRole("region", { name: "Itens" });
}

describe("Gerenciador de itens", () => {
  const fetchSpy = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchSpy);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchSpy.mockReset();
  });

  it("exibe o estado vazio inicialmente", () => {
    render(<App />);
    expect(screen.getByText("Nenhum item cadastrado ainda.")).toBeInTheDocument();
    expect(within(lista()).getByText("0 itens")).toBeInTheDocument();
  });

  it("cadastra um item e limpa o formulário", async () => {
    const user = userEvent.setup();
    render(<App />);

    await cadastrar(user, "Caderno", "Capa dura, 96 folhas");

    const item = within(lista()).getByRole("listitem");
    expect(within(item).getByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(within(item).getByText("Capa dura, 96 folhas")).toBeInTheDocument();
    expect(within(lista()).getByText("1 item")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(screen.getByLabelText("Descrição")).toHaveValue("");
  });

  it("mostra erros de validação e não cadastra item inválido", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Adicionar item" }));

    expect(screen.getByText("O nome é obrigatório.")).toBeInTheDocument();
    expect(screen.getByText("A descrição é obrigatória.")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "true");
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
  });

  it("remove o erro assim que o campo é corrigido", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Adicionar item" }));
    await user.type(screen.getByLabelText("Nome"), "Caneta");

    expect(screen.queryByText("O nome é obrigatório.")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "false");
  });

  it("impede nomes duplicados", async () => {
    const user = userEvent.setup();
    render(<App itensIniciais={[{ id: "1", nome: "Caderno", descricao: "Capa dura" }]} />);

    await cadastrar(user, "caderno", "Outro caderno");

    expect(screen.getByText("Já existe um item com esse nome.")).toBeInTheDocument();
    expect(within(lista()).getAllByRole("listitem")).toHaveLength(1);
  });

  it("edita um item existente", async () => {
    const user = userEvent.setup();
    render(<App itensIniciais={[{ id: "1", nome: "Caderno", descricao: "Capa dura" }]} />);

    await user.click(screen.getByRole("button", { name: "Editar Caderno" }));

    const form = screen.getByRole("form", { name: "Editar item" });
    const nome = within(form).getByLabelText("Nome");
    expect(nome).toHaveValue("Caderno");

    await user.clear(nome);
    await user.type(nome, "Caderno universitário");
    await user.click(within(form).getByRole("button", { name: "Salvar alterações" }));

    expect(screen.getByRole("heading", { name: "Caderno universitário" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Caderno" })).not.toBeInTheDocument();
    expect(screen.getByRole("form", { name: "Novo item" })).toBeInTheDocument();
  });

  it("cancela a edição sem alterar o item", async () => {
    const user = userEvent.setup();
    render(<App itensIniciais={[{ id: "1", nome: "Caderno", descricao: "Capa dura" }]} />);

    await user.click(screen.getByRole("button", { name: "Editar Caderno" }));
    await user.type(screen.getByLabelText("Nome"), " alterado");
    await user.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(screen.getByRole("heading", { name: "Caderno" })).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("");
  });

  it("remove um item", async () => {
    const user = userEvent.setup();
    render(
      <App
        itensIniciais={[
          { id: "1", nome: "Caderno", descricao: "Capa dura" },
          { id: "2", nome: "Caneta", descricao: "Azul" },
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Remover Caderno" }));

    expect(screen.queryByText("Caderno")).not.toBeInTheDocument();
    expect(screen.getByText("Caneta")).toBeInTheDocument();
    expect(within(lista()).getByText("1 item")).toBeInTheDocument();
  });

  it("não faz chamadas ao backend", async () => {
    const user = userEvent.setup();
    render(<App />);

    await cadastrar(user, "Caderno", "Capa dura");
    await user.click(screen.getByRole("button", { name: "Editar Caderno" }));
    await user.click(screen.getByRole("button", { name: "Salvar alterações" }));
    await user.click(screen.getByRole("button", { name: "Remover Caderno" }));

    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
