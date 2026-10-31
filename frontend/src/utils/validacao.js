export const NOME_MIN = 3;
export const NOME_MAX = 50;
export const DESCRICAO_MAX = 200;

function normalizar(texto) {
  return (texto ?? "").trim();
}

export function validarNome(nome, itens = [], idIgnorado = null) {
  const valor = normalizar(nome);

  if (!valor) return "O nome é obrigatório.";
  if (valor.length < NOME_MIN) return `O nome deve ter pelo menos ${NOME_MIN} caracteres.`;
  if (valor.length > NOME_MAX) return `O nome deve ter no máximo ${NOME_MAX} caracteres.`;

  const duplicado = itens.some(
    (item) => item.id !== idIgnorado && item.nome.toLowerCase() === valor.toLowerCase(),
  );
  if (duplicado) return "Já existe um item com esse nome.";

  return null;
}

export function validarDescricao(descricao) {
  const valor = normalizar(descricao);

  if (!valor) return "A descrição é obrigatória.";
  if (valor.length > DESCRICAO_MAX) {
    return `A descrição deve ter no máximo ${DESCRICAO_MAX} caracteres.`;
  }

  return null;
}

// Retorna um objeto apenas com os campos inválidos; vazio significa que o item é válido.
export function validarItem({ nome, descricao }, itens = [], idIgnorado = null) {
  const erros = {};

  const erroNome = validarNome(nome, itens, idIgnorado);
  if (erroNome) erros.nome = erroNome;

  const erroDescricao = validarDescricao(descricao);
  if (erroDescricao) erros.descricao = erroDescricao;

  return erros;
}

export function possuiErros(erros) {
  return Object.keys(erros).length > 0;
}
