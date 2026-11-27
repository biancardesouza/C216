import { useCallback, useEffect, useState } from "react";
import { listarProdutos } from "../services/produtos.js";

// Guarda a lista de produtos e os estados de carregamento e erro da busca.
export function useProdutos() {
  const [produtos, setProdutos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const recarregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setProdutos(await listarProdutos());
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    recarregar();
  }, [recarregar]);

  return { produtos, carregando, erro, recarregar };
}
