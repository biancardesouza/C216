import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

async function cadastrar(page, nome, descricao) {
  await page.getByLabel("Nome").fill(nome);
  await page.getByLabel("Descrição").fill(descricao);
  await page.getByRole("button", { name: "Adicionar item" }).click();
}

test("exibe a página inicial vazia", async ({ page }) => {
  await expect(page).toHaveTitle("Gerenciador de Itens");
  await expect(page.getByRole("heading", { name: "Gerenciador de Itens" })).toBeVisible();
  await expect(page.getByText("Nenhum item cadastrado ainda.")).toBeVisible();
});

test("fluxo completo: cadastrar, editar e remover um item", async ({ page }) => {
  const lista = page.getByRole("region", { name: "Itens" });

  await cadastrar(page, "Caderno", "Capa dura, 96 folhas");
  await expect(lista.getByRole("listitem")).toHaveCount(1);
  await expect(lista.getByRole("heading", { name: "Caderno" })).toBeVisible();
  await expect(lista.getByText("1 item")).toBeVisible();

  await page.getByRole("button", { name: "Editar Caderno" }).click();
  await expect(page.getByLabel("Nome")).toHaveValue("Caderno");
  await page.getByLabel("Nome").fill("Caderno universitário");
  await page.getByRole("button", { name: "Salvar alterações" }).click();
  await expect(lista.getByRole("heading", { name: "Caderno universitário" })).toBeVisible();

  await page.getByRole("button", { name: "Remover Caderno universitário" }).click();
  await expect(lista.getByRole("listitem")).toHaveCount(0);
  await expect(page.getByText("Nenhum item cadastrado ainda.")).toBeVisible();
});

test("valida os campos antes de cadastrar", async ({ page }) => {
  await page.getByRole("button", { name: "Adicionar item" }).click();
  await expect(page.getByText("O nome é obrigatório.")).toBeVisible();
  await expect(page.getByText("A descrição é obrigatória.")).toBeVisible();

  await cadastrar(page, "Caneta", "Azul");
  await cadastrar(page, "CANETA", "Preta");
  await expect(page.getByText("Já existe um item com esse nome.")).toBeVisible();
  await expect(page.getByRole("listitem")).toHaveCount(1);
});

test("não faz requisições ao backend", async ({ page }) => {
  const requisicoes = [];
  page.on("request", (requisicao) => {
    if (["fetch", "xhr"].includes(requisicao.resourceType())) requisicoes.push(requisicao.url());
  });

  await cadastrar(page, "Caderno", "Capa dura");
  await page.getByRole("button", { name: "Remover Caderno" }).click();

  expect(requisicoes).toEqual([]);
});

test("layout responsivo sem rolagem horizontal", async ({ page }) => {
  await cadastrar(page, "Item com descrição longa", "x".repeat(200));
  const temRolagem = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(temRolagem).toBe(false);
});
