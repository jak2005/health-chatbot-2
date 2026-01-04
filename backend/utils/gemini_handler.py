# backend/utils/gemini_handler.py
import google.generativeai as genai
from typing import Dict, List, Optional
from utils.rag_handler import RAGHandler
from utils.query_decomposer import QueryDecomposer
from utils.search_controller import SearchController
from utils.response_generator import ResponseGenerator
from utils.context_manager import ContextManager

class GeminiHandler:
    def __init__(self, config):
        self.config = config
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize components
        self.query_decomposer = QueryDecomposer(config.GOOGLE_API_KEY)
        self.search_controller = SearchController(config.SONAR_API_KEY)
        self.response_generator = ResponseGenerator(config.GOOGLE_API_KEY)
        self.rag_handler = None
        self.context_manager = ContextManager()
        
        # Initialize chat sessions
        self.chat_sessions: Dict[str, any] = {}

    def set_managers(self, db_manager):
        """Set RAG handler"""
        self.rag_handler = RAGHandler(db_manager)

    async def get_response(self, user_id: str, message: str) -> str:
        """Process user message and generate response"""
        try:
            print(f"\n=== Processing Message for User: {user_id} ===")
            print(f"Original Message: {message}")
            
            # Get session context
            context = self.context_manager.get_context(user_id)
            print(f"Retrieved context length: {len(context)}")
            
            # Step 1: Decompose query and check if research needed
            decomposition_result = await self.query_decomposer.decompose_query(message)
            needs_research = decomposition_result['needs_research']
            sub_queries = decomposition_result['sub_queries']
            
            # Step 2: Get research results if needed (ONLY if Sonar API is configured)
            research_results = {}
            if needs_research and sub_queries and self.config.SONAR_API_KEY:
                print("\n=== Conducting Research ===")
                research_results = await self.search_controller.search_research(sub_queries)
            elif needs_research and not self.config.SONAR_API_KEY:
                print("\n=== Skipping Research (No SONAR_API_KEY configured) ===")
            
            # Step 3: Get RAG context
            rag_context = ""
            if self.rag_handler:
                print("\n=== Getting RAG Context ===")
                rag_context = self.rag_handler.get_relevant_context(message)
            
            # Step 4: Generate comprehensive response
            print("\n=== Generating Response ===")
            response = await self.response_generator.generate_response(
                original_query=message,
                sub_queries=sub_queries,
                research_results=research_results,
                rag_context=rag_context
            )
            
            # Step 5: Update context
            self.context_manager.update_context(user_id, message, response)
            
            print("\n=== Response Generation Complete ===")
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in getting response: {str(e)}")
            traceback.print_exc()
            return self.config.DEFAULT_RESPONSE

    def clear_context(self, user_id: str):
        """Clear context for a user"""
        self.context_manager.clear_context(user_id)
