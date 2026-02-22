import os
from config import get_model_api_key
os.environ['MODEL_API_KEY'] = get_model_api_key()


from typing import List
from src.adapters.ai.ai_service import AbstractAIService
from langchain_text_splitters import CharacterTextSplitter

from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun
# from openrouter import OpenRouter
# from langchain.messages import AIMessage, HumanMessage, SystemMessage

import faiss
import numpy as np

from langchain_core.prompts import PromptTemplate
from langchain_unstructured import UnstructuredLoader
from sentence_transformers import SentenceTransformer


class TransformersAIService(AbstractAIService):
    def __init__(self):
        self.file_preprocessing_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150, separator="\n")
        self.MIN_CHUNKS = 5

        self.system_message = {'role': 'system', 'content': """You are a helpful file and web assistant. 
        Do not make up the answer. If you can answer on this question without using additional content, do it. 
        Owerwise, use the additional content to answer the question.
        Answer on the same language as the question."""}

        self.template = """{question}
        ---
        Additional context: {context}"""


        self.messages = []
        self.MODEL_ID = "arcee-ai/trinity-large-preview:free"
        self.client = OpenAI(
            api_key=os.environ.get('MODEL_API_KEY'),
            base_url="https://openrouter.ai/api/v1",
        )
        self.websearch_tool= DuckDuckGoSearchRun()
    

    def clear_chat_memory(self):
        self.messages.clear()
        self.messages.append(self.system_message)

    def _process_file(self, file_path: str):
        loader = UnstructuredLoader(file_path)
        documents = loader.load()
        batched_text = [documents[i].page_content for i in range(len(documents))]

        return "\n".join(batched_text)

    def get_context_from_file(self, query: str, file_path: str):
        file_text = self._process_file(file_path)
        chunks = self.text_splitter.split_text(file_text)

        embedded_chunks = np.array(self.file_preprocessing_model.encode(chunks))
        embedded_query = np.array(self.file_preprocessing_model.encode([query]))

        index = faiss.IndexFlatL2(len(self.file_preprocessing_model.encode("test text")))
        index.add(embedded_chunks)

        k = min(self.MIN_CHUNKS, len(embedded_chunks))
        _, inds = index.search(embedded_query, k)

        results = []
        for ind in inds[0]:
            results.append(chunks[ind])

        return results
    
    def _web_search(self, query: str):
        return self.websearch_tool.invoke(query)

    def _prompt_creating(self, query: str, context_file: List[str], context_web: str):
        context = " ".join(context_file)
        context += "\n\n" + context_web
        template = PromptTemplate(
            template=self.template,
            input_variables=["question", "context"]
        )
        prompt = template.format(question=query, context=context)
        return prompt

    def question_answering(self, query: str, doc_text: List[str]):
        web_results = self._web_search(query)
        prompt = self._prompt_creating(query, doc_text, web_results)

        self.messages.append({'role': 'user', 'content': prompt})

        response = self.client.chat.completions.create(
            model=self.MODEL_ID,
            messages=self.messages,
            temperature=0.7,
            max_tokens=512,
        )
        
        # with OpenRouter(api_key=os.environ.get("MODEL_API_KEY")) as client:
        #     response = client.chat.send(
        #         model=self.MODEL_ID,
        #         messages=self.messages,
        #     )
        
        self.messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        return response.choices[0].message.content
