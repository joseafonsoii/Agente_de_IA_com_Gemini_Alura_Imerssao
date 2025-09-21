from pydantic import BaseModel, Field
from typing import Literal,List, Dict
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY, DATA_DIR

class TriagemOut(BaseModel):
    decisao: Literal["AUTO_RESOLVER","PEDIR_INFO","ABRIR_CHAMADO"]
    urgencia: Literal["BAIXA","MEDIA","ALTA"]
    campos_faltantes: List[str]=Field(default_factory=list)
    
TRIAGEM_PROMPT = (
    "Voce e um triador de service Desk para politicas internas da empresa SmartOPS."
    "Dada a mensagem do usuario, retorne SOMENTE um JSON com \n"
    "{\n}"
    ' "decisao": "AUTO_RESOLVER" | "PEDIR_INFO" | "ABRIR_CHAMADO",\n'
    ' "urgencia": "BAIXA" | "MEDIA" | "ALTA",\n'
    ' "campos_faltantes": ["..."]\n'
    "{\n}"
    "Regras:\n"
    '- **AUTO_RESOLVER**: Perguntas claras sobre regras ou procedimentos.\n'
    '- **PEDIR_INFO**: Mensagens vagas ou que faltam informacoes. \n'
    '- **ABRIR_CHAMADO**: Pedidos de excecao, liberacao ou aprovacao.\n'
)
    
def inicializar_llm_triagem():
    return ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY
    )

llm_triagem = inicializar_llm_triagem()

def triagem(mensagem:str) -> Dict:
    triagem_chain = llm_triagem.with_structured_output(TriagemOut)
    
    saida = triagem_chain.invoke([
        SystemMessage(content=TRIAGEM_PROMPT),
        HumanMessage(content=mensagem)
    ])
    
    return saida.model_dump()