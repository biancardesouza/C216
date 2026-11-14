// Operações puras sobre a lista exibida, aplicadas depois que a API confirma a mudança.

export function adicionarItem(itens, item) {
  return [...itens, item];
}

export function substituirItem(itens, itemAtualizado) {
  return itens.map((item) => (item.id === itemAtualizado.id ? itemAtualizado : item));
}

export function removerItem(itens, id) {
  return itens.filter((item) => item.id !== id);
}
