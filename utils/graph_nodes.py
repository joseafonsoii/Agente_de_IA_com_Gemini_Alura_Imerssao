from typing import List, Dict
from .triagem import triagem
from .rag import perguntar_politica_RAG

KEYWORDS_ABRIR_TICKET = ["liberacao", 
                         "excecao", "aprovacao", 
                         "abrir chamado", "abrir ticket", 
                         "abrir chamado", "acesso_especial"
                         ]

def node_triagem(state: Dict) -> Dict:
    print("Executando no de triagem...")
    return {"triagem":triagem(state["pergunta"])}

def node_auto_auto_resolver(state:Dict) -> Dict:
    print("Executando no de auto resolver")
    resposta_rag = perguntar_politica_RAG(state["pergunta"])
    
    update = {
        "resposta":resposta_rag["answer"],
        "citacoes":resposta_rag.get("citacoes", []),
        "rag_sucesso": resposta_rag["contexto_encontrado"]
    }
    
    if resposta_rag["contextpo_encontrado"]:
        update["acao_final"] = "AUTO_RESOLVER="
    return update

def node_pedir_info(state:Dict) -> Dict:
    print("Executando no de pedir info")
    faltantes = state["triagem"].get("campos_faltantes")
    detalhe = ", "+join(faltantes) if faltantes else "mais detalhes"
    
    return {
        "resposta": f"Para ajudar melhor, precio que que informe: {detalhe}",
        "citacoes":[],
        "acao_final":"PEDIR_INFO"
    }
    
def node_Abrir_chamadas(state:Dict) -> Dict:
    print("Executando no de abrir chamado")
    triagem_data = state["triagem"]
    
    return {
        "resposta": f"Chamado aberto com urgencia {triagem_data["urgencia"]}, Descricao: {state['pergunta']}",
        "citacoes":[],
        "acao_final":"ABRIR_CHAMADO"
    }
    
def decidir_pos_triagem(state:Dict) -> Dict:
    print("Decidindo apos triagem...")
    decisao = state["triagem"]["decisao"]
    
    if decisao == "AUTO_RESOLVER":
        return "auto"
    elif decisao == "PEDIR_INFO":
        return "info"
    elif decisao == "ABRIR_CHAMADO":
        return "chamado"
    
def decidir_pos_auto_resolver(state:Dict) -> Dict:
    print("Decidindo apos triagem...")
    
    if state.get("rag_sucesso"):
        print("RAG teve sucesso, finalizando...")
        return "fim"
    
    pergunta = (state["pergunta"] or "").lower()  
    
    if any(kw in pergunta for kw in KEYWORDS_ABRIR_TICKET):
        print("Palavra chave para abrir chamado encontrada, indo para abrir chamado...")
        return "chamado"
    
    print("RAG falhou,indo para pedir mais informacoes...") 
    return "info"