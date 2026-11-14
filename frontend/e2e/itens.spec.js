import { expect, test } from "@playwright/test";

const API_URL = process.env.E2E_API_URL ?? "http://localhost:8000";

// Todos os testes compartilham o mesmo banco, então cada um usa nomes únicos
// (projeto + horário) para não depender da ordem nem de dados de outros testes.
function nomeUnico(testInfo, prefixo) {
  const sufixo = `${testInfo.project.name}-${Date.now().toString(36)}-${testInfo.retry}`;
  return `${prefixo} ${sufixo}`;
}

function lista(page) {
  return page.getByRole("region", { name: "Itens" });
}

function cardDoItem(page, nome) {
  return lista(page)
    .getByRole("listitem")
    .filter({ has: page.getByRole("heading", { name: nome, exact: true }) });
}

async function abrirPagina(page) {
  await page.goto("/");
  // Espera a lista sair do estado de carregamento.
  await expect(page.getByText("Carregando itens...")).toHaveCount(0);
  await expect(page.getByRole("alert")).toHaveCount(0);
}

async function cadastrar(page, nome, descricao) {
  await page.getByLabel("Nome", { exact: true }).fill(nome);
  await page.getByLabel("Descrição", { exact: true }).fill(descricao);
  await page.getByRole("button", { name: "Adicionar item" }).click();
}

test.beforeEach(async ({ page }) => {
  await abrirPagina(page);
});

test("carrega a interface e a lista vinda da API", async ({ page }) => {
  await expect(page).toHaveTitle("Gerenciador de Itens");
  await expect(page.getByRole("heading", { name: "Gerenciador de Itens" })).toBeVisible();
  await expect(lista(page).getByText(/^\d+ ite(m|ns)$/)).toBeVisible();
});

test("item cadastrado continua na lista após recarregar a página", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Caderno");

  await cadastrar(page, nome, "Capa dura, 96 folhas");
  await expect(cardDoItem(page, nome)).toBeVisible();
  await expect(page.getByLabel("Nome", { exact: true })).toHaveValue("");

  await page.reload();
  await expect(page.getByText("Carregando itens...")).toHaveCount(0);

  const card = cardDoItem(page, nome);
  await expect(card).toBeVisible();
  await expect(card.getByText("Capa dura, 96 folhas")).toBeVisible();
});

test("a API responde ao preflight e libera a origem do frontend", async ({
  page,
  request,
}, testInfo) => {
  const origem = new URL(page.url()).origin;

  // O navegador envia este OPTIONS antes do POST com JSON (aba Network).
  const preflight = await request.fetch(`${API_URL}/items/`, {
    method: "OPTIONS",
    headers: {
      Origin: origem,
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "content-type",
    },
  });
  expect(preflight.status()).toBe(200);
  expect(preflight.headers()["access-control-allow-origin"]).toBe(origem);

  const post = page.waitForResponse(
    (res) => res.request().method() === "POST" && new URL(res.url()).pathname === "/items/",
  );
  await cadastrar(page, nomeUnico(testInfo, "Caneta"), "Azul");

  const resposta = await post;
  expect(resposta.status()).toBe(201);
  expect(resposta.headers()["access-control-allow-origin"]).toBe(origem);
});

test("cadastrar o mesmo nome de novo mostra erro", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Mochila");
  await cadastrar(page, nome, "Preta");
  await expect(cardDoItem(page, nome)).toBeVisible();

  await page.reload();
  await expect(page.getByText("Carregando itens...")).toHaveCount(0);
  await cadastrar(page, nome.toUpperCase(), "Outra");

  await expect(page.getByText("Já existe um item com esse nome.")).toBeVisible();
  await expect(cardDoItem(page, nome)).toHaveCount(1);
});

test("a API recusa nome duplicado mesmo vindo de outra aba", async ({
  page,
  context,
}, testInfo) => {
  const nome = nomeUnico(testInfo, "Estojo");
  // Outra aba cadastra o item depois que esta já carregou a lista.
  const outraAba = await context.newPage();
  await abrirPagina(outraAba);
  await cadastrar(outraAba, nome, "Azul");
  await expect(cardDoItem(outraAba, nome)).toBeVisible();

  await cadastrar(page, nome, "Vermelho");

  await expect(page.getByRole("alert")).toHaveText("Já existe um item com esse nome.");
  await expect(page.getByLabel("Nome", { exact: true })).toHaveValue(nome);
});

test("edição e remoção também persistem após recarregar", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Agenda");
  const novoNome = nomeUnico(testInfo, "Planner");

  await cadastrar(page, nome, "2027");
  await cardDoItem(page, nome)
    .getByRole("button", { name: `Editar ${nome}` })
    .click();
  await page.getByLabel("Nome", { exact: true }).fill(novoNome);
  await page.getByRole("button", { name: "Salvar alterações" }).click();
  await expect(cardDoItem(page, novoNome)).toBeVisible();

  await page.reload();
  await expect(cardDoItem(page, novoNome)).toBeVisible();
  await expect(cardDoItem(page, nome)).toHaveCount(0);

  await page.getByRole("button", { name: `Remover ${novoNome}` }).click();
  await expect(cardDoItem(page, novoNome)).toHaveCount(0);

  await page.reload();
  await expect(page.getByText("Carregando itens...")).toHaveCount(0);
  await expect(cardDoItem(page, novoNome)).toHaveCount(0);
});

test("valida os campos antes de chamar a API", async ({ page }) => {
  const posts = [];
  page.on("request", (req) => {
    if (req.method() === "POST") posts.push(req.url());
  });

  await page.getByRole("button", { name: "Adicionar item" }).click();

  await expect(page.getByText("O nome é obrigatório.")).toBeVisible();
  await expect(page.getByText("A descrição é obrigatória.")).toBeVisible();
  expect(posts).toEqual([]);
});

test("layout responsivo sem rolagem horizontal", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Texto longo");
  await cadastrar(page, nome, "x".repeat(200));
  await expect(cardDoItem(page, nome)).toBeVisible();

  const temRolagem = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(temRolagem).toBe(false);
});
