function gerarIdPadrao() {
  return crypto.randomUUID();
}

export function criarItem({ nome, descricao }, gerarId = gerarIdPadrao) {
  return { id: gerarId(), nome: nome.trim(), descricao: descricao.trim() };
}

export function adicionarItem(itens, item) {
  return [...itens, item];
}

export function atualizarItem(itens, id, { nome, descricao }) {
  return itens.map((item) =>
    item.id === id ? { ...item, nome: nome.trim(), descricao: descricao.trim() } : item,
  );
}

export function removerItem(itens, id) {
  return itens.filter((item) => item.id !== id);
}
