import { useCallback, useEffect, useState } from "react";
import { createItem, deleteItem, listItems, updateItem } from "../services/items";
import { adicionarItem, removerItem, substituirItem } from "../utils/itens";

// Estado dos itens sincronizado com a API: a lista só muda depois que o backend confirma.
export function useItens() {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erroCarregamento, setErroCarregamento] = useState(null);
  const [erroRemocao, setErroRemocao] = useState(null);

  const carregar = useCallback(async (sinal) => {
    setCarregando(true);
    setErroCarregamento(null);
    try {
      const lista = await listItems();
      if (!sinal?.cancelado) setItens(lista);
    } catch (falha) {
      if (!sinal?.cancelado) setErroCarregamento(falha.message);
    } finally {
      if (!sinal?.cancelado) setCarregando(false);
    }
  }, []);

  useEffect(() => {
    // Ignora a resposta se o componente for desmontado antes de ela chegar.
    const sinal = { cancelado: false };
    carregar(sinal);
    return () => {
      sinal.cancelado = true;
    };
  }, [carregar]);

  const recarregar = useCallback(() => carregar(), [carregar]);

  // adicionar e atualizar deixam o erro subir para o formulário exibi-lo.
  const adicionar = useCallback(async (dados) => {
    const item = await createItem(dados);
    setItens((atuais) => adicionarItem(atuais, item));
    return item;
  }, []);

  const atualizar = useCallback(async (id, dados) => {
    const item = await updateItem(id, dados);
    setItens((atuais) => substituirItem(atuais, item));
    return item;
  }, []);

  const remover = useCallback(async (id) => {
    setErroRemocao(null);
    try {
      await deleteItem(id);
      setItens((atuais) => removerItem(atuais, id));
      return true;
    } catch (falha) {
      setErroRemocao(falha.message);
      return false;
    }
  }, []);

  return {
    itens,
    carregando,
    erroCarregamento,
    erroRemocao,
    recarregar,
    adicionar,
    atualizar,
    remover,
  };
}
