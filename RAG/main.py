# NOTEs
# 1.at line 28 , update the path to store the vector db
# 2. No memory BOT
# 3. modify testing and dot env
from typing import Sequence,Annotated,TypedDict

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from langchain_core.messages import BaseMessage, AIMessage,HumanMessage,ToolMessage,SystemMessage
from langgraph.graph.message import add_messages

from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv()

# INPUT - pdf path ; OUTUT - a message
# pdf -> chunking -> embedding
def create_db(path):
    # load pdf
    pdf_loader = PyPDFLoader(path)
    pdf = pdf_loader().load()
    print(f'---PDF loaded successfully---')

    # chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 400 ,
        chunk_overlap = 50
    )
    chunks = text_splitter.split_documents(pdf)

    # embedding
    embedding_model = GoogleGenerativeAIEmbeddings(model = 'gemini-embedding-2')
    vector_db = Chroma.from_documents(
        embedding=embedding_model ,
        documents= chunks ,
        persist_directory= 'MY_PROJECTS-main/RAG' ,
        collection_name= 'pdf_data'
    )
    print(f' vector db is created..')
    return vector_db

# def respond(query):
#     msg = query
#     response = app.invoke({'message' : msg})
#     return response.content
#
path = ''
db = create_db(path)

# embedding_model = GoogleGenerativeAIEmbeddings(model = 'gemini-embedding-2')

# AGENT ARCHITECTURE
# 1.create agentstate
class AgentState(TypedDict):
    message : Annotated[Sequence[BaseMessage],add_messages]

#----------helper for testing----------------------
db_testing = Chroma(
    collection_name= 'banking',
    persist_directory = 'C:/VKY/02_SKILLS/LANGHAIN/LEVEL-2/chroma_db' ,
    embedding_function= GoogleGenerativeAIEmbeddings(model = 'gemini-embedding-2')
)
path_env = r'C:\VKY\02_SKILLS\LANGHAIN\LEVEL-2\.env'

#-------------------------------
# 2.create tools
@tool
def retrieve_tool(query:str) -> str:
    '''This tool is used to retrieve related information for a given query.'''
    retriever = db.as_retriever(
        search_type = 'similarity' ,
        search_kwargs = {'k' : 4}
    )
    data = retriever.invoke(query)

    if not data:
        return 'DATA NOT FOUND.'
    if data:
        print('\n==data retrieved successfully==')

    res = []
    for i,chunk in enumerate(data):
        res.append(f'Document : {i+1}\n{chunk.page_content}\n')
    return '\n\n'.join(res)

# 3.CREATE NODE , GRAPH