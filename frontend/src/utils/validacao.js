// Mesmas regras da API, checadas antes de enviar para dar retorno imediato.
// A API continua validando tudo: esta checagem é só para a experiência de uso.

const SKU_VALIDO = /^[A-Z0-9-]{3,30}$/;
const PRECO_VALIDO = /^\d+([.,]\d{1,2})?$/;

export function validarProduto({ sku, nome, categoria, preco, estoque_minimo }) {
  const erros = {};

  if (!SKU_VALIDO.test(sku.trim().toUpperCase())) {
    erros.sku = "Use de 3 a 30 letras, números ou hífen (ex.: CAN-001).";
  }
  if (nome.trim().length < 2 || nome.trim().length > 100) {
    erros.nome = "O nome deve ter entre 2 e 100 caracteres.";
  }
  if (categoria.trim().length < 2 || categoria.trim().length > 50) {
    erros.categoria = "A categoria deve ter entre 2 e 50 caracteres.";
  }
  const precoTexto = String(preco).trim();
  if (!PRECO_VALIDO.test(precoTexto) || Number(precoTexto.replace(",", ".")) <= 0) {
    erros.preco = "Informe um preço maior que zero, com até 2 casas (ex.: 12,90).";
  }
  const minimo = String(estoque_minimo).trim();
  if (minimo !== "" && !/^\d+$/.test(minimo)) {
    erros.estoque_minimo = "O estoque mínimo deve ser um número inteiro, zero ou maior.";
  }

  return erros;
}
