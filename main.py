from langgraph.graphs import StateGraph,START, END
from typing import TypedDict, Optional, List
from utils.graph_nodes import (node_triagem, 
                              node_auto_auto_resolver, 
                              node_pedir_info, 
                              node_Abrir_chamadas,
                              decidir_pos_triagem,
                              decidir_pos_auto_resolver)

class AgentState(TypedDict,total=False):
    pergunta: str
    triagem: dict
    resposta: Optional[str]
    citacoes:List[dict]
    rag_sucesso: bool
    acao_final: str
    
def criar_grafo():
    workflow = StateGraph(AgentState)
    
    #Adicionar nos
    workflow.add_node("triagem", node_triagem)
    workflow.add_node("auto_resolver", node_auto_auto_resolver)
    workflow.add_node("pedir_info", node_pedir_info)
    workflow.add_node("abrir_chamado", node_Abrir_chamadas)
    
    #Configurar fluxos
    workflow.add_edge(START, "triagem", lambda state: True)
    
    workflow.add_conditional_edge("triagem", decidir_pos_triagem, {
        "auto":"auto_resolver",
        "info":"pedir_info",
        "chamado":"abrir_chamado"
    })
    
    workflow.add_conditional_edges("auto_resolver",decidir_pos_auto_resolver{
        "info":"pedir_info",
        "chamado":"abrir_chamado",
        "final":END
    })
    
    workflow.add_edge("pedir_info", END, lambda state: True)
    workflow.add_edge("abrir_chamado", END, lambda state: True)
    
    return workflow

def main():
    print("Assistente de politicas internas - iniciando...")
    
    grafo = criar_grafo()
    
    #Testes 
    testes = [
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    
    for pergunta in testes:
        print(f"\n{'=+50'}")
        print(f"?Pergunta: {pergunta}")
        
        resultado = grafo.invoke({"pergunta":pergunta})
        
        print(f"!Resposta: {resultado.get('resposta', "sem resposta")}")
        print(f"Acao final: {resultado.get('acao_final','Nenhuma')}")
        
        if resultado.get("citacoes"):
            print("Citacoes")
            for citacao in resultado["citacoes"]:
                print(f"  - {citacao['documento']} (pagina {citacao['pagina']})" )
                

if __name__ == "__main__":
    main()