import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Caminhos
PDF_PATH = os.path.join("data", "protocolo_sesab.pdf")
CHROMA_PATH = "chroma_db"

def processar_protocolo():
    if not os.path.exists(PDF_PATH):
        print(f"Erro: O arquivo {PDF_PATH} não foi encontrado. Coloque o PDF na pasta 'data/'.")
        return

    print("1. Lendo o PDF do Protocolo SESAB...")
    loader = PyPDFLoader(PDF_PATH)
    documentos = loader.load()

    print("2. Dividindo o documento em fragmentos (chunks)...")
    # Quebra o documento em trechos de 1000 caracteres com sobreposição de 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"-> Total de fragmentos gerados: {len(chunks)}")

    print("3. Gerando Embeddings e salvando no ChromaDB via Ollama...")
    # Utiliza o modelo de embeddings do Ollama (nomic-embed-text ou llama3.1)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Salva os vetores no diretório local /chroma_db
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print("✅ Ingestão concluída com sucesso! O banco vetorial ChromaDB está pronto para uso.")

if __name__ == "__main__":
    processar_protocolo()