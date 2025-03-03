import requests
import json
import os
from typing import Dict, Any, List, Optional, Union

class LLMProcessor:
    """Service for processing files using DeepSeek LLM API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM processor with API credentials."""
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.chat_endpoint = "/chat/completions"
        
        # Available models
        self.models = {
            "chat": "deepseek-chat",
            "reasoner": "deepseek-reasoner"
        }
        
        self.current_model = self.models["chat"]  # Default model
    
    def set_model(self, model_type: str):
        """Set the model type to use (chat or reasoner)."""
        if model_type in self.models:
            self.current_model = self.models[model_type]
            return True
        return False
    
    def process_file_content(self, content: str, metadata: str, query: str) -> Dict[str, Any]:
        """
        Process file content with the DeepSeek API.
        
        Args:
            content (str): The file content to process
            metadata (str): The file metadata
            query (str): User's query about the file
            
        Returns:
            Dict[str, Any]: The API response
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Construct system prompt
        system_prompt = "You are an AI assistant that helps analyze documents. "
        system_prompt += "You'll be provided with document content and metadata, and a query about the document."
        system_prompt += "Provide a concise, accurate response to the query based on the document content."
        
        # Construct user message
        user_message = f"Document content:\n{content}\n\nDocument metadata:\n{metadata}\n\nQuery: {query}"
        
        # API request payload
        payload = {
            "model": self.current_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.chat_endpoint}", 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def extract_response(self, api_response: Dict[str, Any]) -> str:
        """Extract the assistant's response from the API response."""
        try:
            if "error" in api_response:
                return f"Error: {api_response['error']}"
            
            if "choices" in api_response and len(api_response["choices"]) > 0:
                return api_response["choices"][0]["message"]["content"]
            
            return "No response was generated."
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def summarize_document(self, content: str, metadata: str) -> str:
        """Summarize a document using the LLM."""
        api_response = self.process_file_content(
            content, 
            metadata, 
            "Please provide a comprehensive summary of this document."
        )
        return self.extract_response(api_response)
    
    def answer_query(self, content: str, metadata: str, query: str) -> str:
        """Answer a specific query about a document using the LLM."""
        api_response = self.process_file_content(content, metadata, query)
        return self.extract_response(api_response)
