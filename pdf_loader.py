# Importing libs
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from docling.document_converter import DocumentConverter
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Defining the PDF Loader
class DoclingPDFLoader(BaseLoader):

    def __init__(self, file_path: str | list[str]) -> None:
        self._file_paths = file_path if isinstance(file_path, list) else [file_path]
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        for source in self._file_paths:
            dl_doc = self._converter.convert(source).document
            text = dl_doc.export_to_markdown()
            yield LCDocument(page_content=text)

# PDF_PATH
FILE_PATH = "YOUR_PATH_HERE" 


loader = DoclingPDFLoader(file_path=FILE_PATH)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
docs = loader.load()
splits = text_splitter.split_documents(docs)


# Connecting with the GROQ API

api_key = 'YOUR_API_KEY'
os.environ['GROQ_API_KEY'] = api_key
chat = ChatGroq(model='llama-3.1-70b-versatile')

#Setting up the chatbot

def resposta_bot(mensagens, splits):
  mensagem_system = '''Você é um assistente amigável chamado Leo.
  Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
  mensagens_modelo = [('system', mensagem_system)]
  mensagens_modelo += mensagens
  template = ChatPromptTemplate.from_messages(mensagens_modelo)
  chain = template | chat
  return chain.invoke({'informacoes': splits}).content

print('Bem-vindo ao Leo, o assistente da receita federal')

# Chatbot loop

mensagens = []
while True:
  pergunta = input('Usuario: ')
  if pergunta.lower() == 'x':
    break
  mensagens.append(('user', pergunta))
  resposta = resposta_bot(mensagens, splits)
  mensagens.append(('assistant', resposta))
  print(f'Bot: {resposta}')

print('Muito obrigado por usar o Leo')