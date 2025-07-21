import faiss
import numpy as np
import os
from typing import List, Tuple, Optional

DIMENSAO_VETOR = 1536

def load_index(caminho: str) -> faiss.IndexFlatL2:

    try:
        if not os.path.exists(caminho):
            print(f"Arquivo {caminho} não encontrado. Criando novo índice vazio.")
            return faiss.IndexFlatL2(DIMENSAO_VETOR)
        
        indice = faiss.read_index(caminho)
        print(f"Índice carregado com sucesso de {caminho}")
        return indice
        
    except Exception as erro:
        raise Exception(f"Erro ao carregar índice: {str(erro)}")

def save_index(indice: faiss.IndexFlatL2, caminho: str) -> None:

    try:
        diretorio = os.path.dirname(caminho)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio)
        
        faiss.write_index(indice, caminho)
        print(f"Índice salvo com sucesso em {caminho}")
        
    except Exception as erro:
        raise Exception(f"Erro ao salvar índice: {str(erro)}")

def add_to_index(indice: faiss.IndexFlatL2, vetores: List[List[float]], ids: List[int]) -> None:

    try:
        if len(vetores) != len(ids):
            raise ValueError("Número de vetores deve ser igual ao número de IDs")
        
        if not vetores:
            raise ValueError("Lista de vetores não pode estar vazia")

        vetores_np = np.array(vetores, dtype=np.float32)

        if vetores_np.shape[1] != DIMENSAO_VETOR:
            raise ValueError(f"Dimensão dos vetores deve ser {DIMENSAO_VETOR}")

        indice.add(vetores_np)
        
        print(f"Adicionados {len(vetores)} vetores ao índice")
        
    except Exception as erro:
        raise Exception(f"Erro ao adicionar vetores ao índice: {str(erro)}")

def search_index(indice: faiss.IndexFlatL2, vetor: List[float], k: int) -> List[int]:

    try:
        if indice.ntotal == 0:
            raise ValueError("Índice está vazio. Adicione vetores antes de buscar.")
        
        if len(vetor) != DIMENSAO_VETOR:
            raise ValueError(f"Dimensão do vetor deve ser {DIMENSAO_VETOR}")
        
        if k <= 0:
            raise ValueError("Valor de k deve ser maior que zero")
        
        if k > indice.ntotal:
            k = indice.ntotal
            print(f"Valor de k ajustado para {k} (total de vetores no índice)")
        
        vetor_np = np.array([vetor], dtype=np.float32)

        distancias, indices = indice.search(vetor_np, k)

        return indices[0].tolist()
        
    except Exception as erro:
        raise Exception(f"Erro ao buscar no índice: {str(erro)}")