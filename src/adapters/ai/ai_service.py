from abc import ABC, abstractmethod

class AbstractAIService(ABC):
    @abstractmethod
    def get_context_from_file(self, query: str, file_path: str):
        pass

    @abstractmethod
    def question_answering(self, query: str, docsearch):
        pass

    @abstractmethod
    def clear_chat_memory(self):
        pass
