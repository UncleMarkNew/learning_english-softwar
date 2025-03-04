import requests
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import hashlib
import sqlite3

class LLMProcessor:
    """Service for processing files using DeepSeek LLM API."""
    
    def __init__(self, api_key: Optional[str] = None, cache_db: str = "llm_cache.db"):
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
        
        # Initialize cache
        self.cache_db = cache_db
        self._init_cache()
    
    def _init_cache(self):
        """Initialize the cache database."""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS response_cache
                    (query_hash TEXT PRIMARY KEY,
                     response TEXT,
                     timestamp DATETIME)''')
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, content: str, metadata: str, query: str) -> str:
        """Generate a cache key for the given inputs."""
        combined = f"{content}{metadata}{query}{self.current_model}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get a cached response if available and not expired."""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        c.execute('''SELECT response, timestamp FROM response_cache 
                    WHERE query_hash = ?''', (cache_key,))
        result = c.fetchone()
        conn.close()
        
        if result:
            response, timestamp = result
            # Check if cache is less than 24 hours old
            cache_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - cache_time).days < 1:
                return response
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache a response."""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO response_cache 
                    (query_hash, response, timestamp) 
                    VALUES (?, ?, ?)''',
                 (cache_key, response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def set_model(self, model_type: str) -> bool:
        """Set the model type to use (chat or reasoner)."""
        if model_type in self.models:
            self.current_model = self.models[model_type]
            return True
        return False
    
    def process_file_content(self, content: str, metadata: str, query: str) -> Dict[str, Any]:
        """Process file content with the DeepSeek API."""
        # Check cache first
        cache_key = self._get_cache_key(content, metadata, query)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return {"choices": [{"message": {"content": cached_response}}]}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        system_prompt = (
            "You are an AI assistant specialized in analyzing English learning materials. "
            "You'll be provided with document content and metadata, and a query about the document. "
            "Provide clear, accurate responses focused on helping users understand and learn English effectively."
        )
        
        user_message = f"Document content:\n{content}\n\nDocument metadata:\n{metadata}\n\nQuery: {query}"
        
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
                json=payload,
                timeout=30  # Add timeout
            )
            response.raise_for_status()
            api_response = response.json()
            
            # Cache successful response
            if "choices" in api_response and len(api_response["choices"]) > 0:
                self._cache_response(
                    cache_key,
                    api_response["choices"][0]["message"]["content"]
                )
            
            return api_response
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

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
        query = (
            "Please provide a comprehensive summary of this English learning material. "
            "Focus on key vocabulary, grammar points, and main learning objectives."
        )
        api_response = self.process_file_content(content, metadata, query)
        return self.extract_response(api_response)
    
    def answer_query(self, content: str, metadata: str, query: str) -> str:
        """Answer a specific query about a document using the LLM."""
        api_response = self.process_file_content(content, metadata, query)
        return self.extract_response(api_response)
    
    def analyze_difficulty(self, content: str) -> str:
        """Analyze the difficulty level of the English content."""
        query = (
            "Please analyze the difficulty level of this English content. "
            "Consider vocabulary, grammar complexity, and overall comprehension level. "
            "Provide a CEFR level estimation and explanation."
        )
        api_response = self.process_file_content(content, "", query)
        return self.extract_response(api_response)
    
    def generate_quiz(self, content: str) -> str:
        """Generate quiz questions based on the content."""
        query = (
            "Please create 5 quiz questions based on this content. "
            "Include a mix of multiple choice and open-ended questions. "
            "Provide answers separately."
        )
        api_response = self.process_file_content(content, "", query)
        return self.extract_response(api_response)
    
    def explain_grammar(self, content: str, specific_point: Optional[str] = None) -> str:
        """Explain grammar points in the content."""
        query = (
            f"Please explain the grammar points in this content"
            f"{' focusing on ' + specific_point if specific_point else ''}. "
            "Provide clear explanations and examples."
        )
        api_response = self.process_file_content(content, "", query)
        return self.extract_response(api_response)
