from langchain_comunity.document_loaders import PyMuPDFLoader
from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbedding
from langchain_comunity.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import  List, Dict
import re
from pathlib import Path
from config import DATA_DIR,GOOGLE_API_KEY
from .triagem import llm_triagem

def carregar_Documents():
    docs[] # type: ignore
    data_path = Path(DATA_DIR)
    
    for arquivo in data_path.glob("*pdf"):
        try:
            loader = PyMuPDFLoader(str(arquivo))
            docs.extend(loader.load()) # type: ignore
            print(f"Carregado: {arquivo.name}") 
        except Exception as e:
            print(f"Erro ao carregar {arquivo.name}: {e}")
    return docs # type: ignore

def config_rag():
    docs = carregar_Documents()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )
    
    chunks = splitter.split_documents(docs)
    
    embeddings = GoogleGenerativeAIEmbedding(
        model = "models/embedding-001",
        google_Api_key = GOOGLE_API_KEY
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriver(
        search_type="similarity",
        search_kwargs={"k":4}
    )
    return retriever

# Inicializa retriever uma vez
retriever = config_rag()

def _clean_text(s: str) -> str:
    return re.sub(r'\s+', ' ',s or "").strip()

def extrair_trecho(texto: str,query:str,janela:int=240) -> str:
    txt = _clean_text(texto)
    termos = [t.lower() for t in re.findall(r"\w+",query or "") if len(t) >= 4]
    pos = -1
    
    for t in termos:
        pos = txt.lower().find(t)
        if pos != -1:
            break
        
        if pos != -1:
            pos = 0
        ini,fim = max(0,pos-janela//2), min(len(txt),pos+janela//2)
        return txt[ini:fim] + ("..." if fim < len(txt) else "")

def formatar_citacoes(docs_rel: List, query: str) -> List[Dict]:
    cites, seen = [], set()
    
    for d in docs_rel:
        src = Path(d.metadata.get("source","")).name
        page = int(d.metadata.get("page", 0)) + 1
        key = (src, page)
        
        if key in seen:
            continue
        
        seen.add(key)
        cites.append({
            "documento":src,
            "pagina":page,
            "trecho":extrair_trecho(d.page_content,query)
        })
    return cites[:3]  

def perguntar_politica_RAG(pergunta: str) -> Dict:
    docs_relacionados = retriever.invoke(pergunta)
    
    if not docs_relacionados:
        return {
            "answer":"Nao sei",
            "citacoes":[],
            "contexto_encontrado":False
            
        } 
    prompt_rag = ChatPromptTemplate.from_messages([
        ("system","voce e um Assistente de Politicas Internas. Responda SOMENTE com base no contexto. Se nao houver base suficiente, responda apenas 'Nao sei'"),
        ("human","Pergunta: {input}\nContexto:\n{contexto}")
    ])
    
    document_chain = create_stuff_documents_chain(llm_triagem,prompt_rag)
    
    answer = document_chain.invoke({
        "input": pergunta,
        "context":docs_relacionados
    })
    
    txt = (answer or "").strip()
    
    if txt.strip(".!?") == "Nao sei":
        return {
            "answer":"Nao sei",
            "citacoes": [],
            "contexto_encontrado":False
        }
        
    return {
            "answer":txt,
            "citacoes": formatar_citacoes(docs_relacionados, pergunta),
            "contexto_encontrado":True
    }
        

    