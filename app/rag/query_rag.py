import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langsmith import Client

load_dotenv()


def get_prompt():
    """Fetch prompt from LangSmith or fallback to default."""
    try:
        client = Client()
        return client.pull_prompt("rlm/rag-prompt")
    except Exception as e:
        print(f"⚠️ Could not fetch remote prompt: {e}")
        return ChatPromptTemplate.from_template("""
        You are a helpful assistant. Use the following context to answer the question.
        If you don’t find any relevant info, say you don’t have enough information.

        Context:
        {context}

        Question:
        {question}
        """)


def get_rag_chain():
    """Initialize and return the RAG pipeline."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.6,
        convert_system_message_to_human=True,
        streaming=True  # 👈 important for WebSocket
    )

    persist_directory = os.path.join(os.path.dirname(__file__), "rag_db")
    if not os.path.exists(persist_directory):
        raise FileNotFoundError("❌ Vector store not found. Run setup_rag.py first.")

    vectorstore = Chroma(persist_directory=persist_directory)
    retriever = vectorstore.as_retriever()

    prompt = get_prompt()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def query_rag(question: str):
    """Run a single RAG query and return result."""
    rag_chain = get_rag_chain()
    return rag_chain.invoke(question)
