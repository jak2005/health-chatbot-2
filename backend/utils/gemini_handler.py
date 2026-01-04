# backend/utils/gemini_handler.py
import google.generativeai as genai
from typing import Dict, List, Optional
from utils.rag_handler import RAGHandler
from utils.query_decomposer import QueryDecomposer
from utils.search_controller import SearchController
from utils.response_generator import ResponseGenerator
from utils.context_manager import ContextManager
from utils.user_profile_manager import UserProfileManager

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
        self.user_profile_manager = None
        
        # Initialize chat sessions
        self.chat_sessions: Dict[str, any] = {}

    def set_managers(self, db_manager):
        """Set RAG handler and User Profile Manager"""
        self.rag_handler = RAGHandler(db_manager)
        self.user_profile_manager = UserProfileManager(db_manager)

    async def get_response(
        self, 
        user_id: str, 
        message: str, 
        is_whatsapp: bool = False
    ) -> str:
        """Process user message and generate response"""
        try:
            print(f"\n=== Processing Message for User: {user_id} ===")
            print(f"Original Message: {message}")
            print(f"Platform: {'WhatsApp' if is_whatsapp else 'Streamlit'}")
            
            # Get user profile for WhatsApp users
            user_profile = None
            if is_whatsapp and self.user_profile_manager:
                user_profile = await self.user_profile_manager.get_user_profile(user_id)
            
            # Get session context
            context = self.context_manager.get_context(user_id)
            print(f"Retrieved context length: {len(context)}")
            
            # Step 1: Decompose query and check if research needed
            decomposition_result = await self.query_decomposer.decompose_query(message)
            needs_research = decomposition_result['needs_research']
            sub_queries = decomposition_result['sub_queries']
            
            # Step 2: Get research results if needed
            research_results = {}
            if needs_research and sub_queries:
                print("\n=== Conducting Research ===")
                research_results = await self.search_controller.search_research(sub_queries)
            
            # Step 3: Get RAG context
            rag_context = ""
            if self.rag_handler:
                print("\n=== Getting RAG Context ===")
                rag_context = self.rag_handler.get_relevant_context(
                    message,
                    user_profile=user_profile
                )
            
            # Step 4: Generate comprehensive response
            print("\n=== Generating Response ===")
            response = await self.response_generator.generate_response(
                original_query=message,
                sub_queries=sub_queries,
                research_results=research_results,
                rag_context=rag_context,
                user_profile=user_profile
            )
            
            # Step 5: Update context and user profile
            self.context_manager.update_context(user_id, message, response)
            
            if is_whatsapp and self.user_profile_manager:
                context_summary = self.context_manager.get_context_summary(user_id)
                await self.user_profile_manager.update_profile(
                    user_id,
                    message,
                    response,
                    context_summary
                )
            
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




