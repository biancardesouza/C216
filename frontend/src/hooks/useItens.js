import { useCallback, useState } from "react";
import { adicionarItem, atualizarItem, criarItem, removerItem } from "../utils/itens";

// Estado dos itens mantido apenas em memória, sem chamadas ao backend.
export function useItens(itensIniciais = []) {
  const [itens, setItens] = useState(itensIniciais);

  const adicionar = useCallback((dados) => {
    setItens((atuais) => adicionarItem(atuais, criarItem(dados)));
  }, []);

  const atualizar = useCallback((id, dados) => {
    setItens((atuais) => atualizarItem(atuais, id, dados));
  }, []);

  const remover = useCallback((id) => {
    setItens((atuais) => removerItem(atuais, id));
  }, []);

  return { itens, adicionar, atualizar, remover };
}
