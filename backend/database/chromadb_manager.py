import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from datetime import datetime
from typing import Dict, List, Optional

class ChromaDBManager:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction()
        
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Create collections with embedding function
        self.health_tips = self.client.get_or_create_collection(
            name="health_tips",
            embedding_function=self.embedding_function
        )
        self.products = self.client.get_or_create_collection(
            name="products",
            embedding_function=self.embedding_function
        )
        self.chat_history = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_function
        )
        self.feedback = self.client.get_or_create_collection(
            name="feedback",
            embedding_function=self.embedding_function
        )
        self.user_profiles = self.client.get_or_create_collection(
            name="user_profiles",
            embedding_function=self.embedding_function
        )

        # Initialize collections (empty by default)
        

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database"""
        try:
            results = self.user_profiles.get(
                where={"user_id": user_id},
                limit=1
            )
            
            if results and results['metadatas']:
                return results['metadatas'][0]
            return None
            
        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return None

    def store_user_profile(self, user_id: str, profile: Dict) -> bool:
        """Store user profile in database"""
        try:
            # Convert profile to string for document
            profile_str = f"User Profile for {user_id}"
            
            # Store profile
            self.user_profiles.upsert(
                documents=[profile_str],
                metadatas=[profile],
                ids=[f"profile_{user_id}"]
            )
            return True
            
        except Exception as e:
            print(f"Error storing user profile: {str(e)}")
            return False

    def get_relevant_content(self, query: str, user_profile: Optional[Dict] = None, limit: int = 5) -> Dict:
        """Get relevant content based on query using vector similarity"""
        try:
            print(f"\n=== Getting Relevant Content for Query: {query} ===")
            
            # Use user profile topics to enhance search if available
            search_query = query
            if user_profile and user_profile.get('key_topics'):
                topics = ' '.join(user_profile['key_topics'])
                search_query = f"{query} {topics}"
            
            # Get relevant health tips
            health_results = self.health_tips.query(
                query_texts=[search_query],
                n_results=min(limit, len(self.health_tips.get()['ids']))
            )
            
            # Get relevant products
            product_results = self.products.query(
                query_texts=[search_query],
                n_results=min(limit, len(self.products.get()['ids']))
            )
            
            print(f"Found {len(health_results['documents'][0] if health_results['documents'] else [])} relevant health tips")
            print(f"Found {len(product_results['documents'][0] if product_results['documents'] else [])} relevant products")
            
            return {
                'health_tips': {
                    'documents': health_results['documents'][0] if health_results['documents'] else [],
                    'metadatas': health_results['metadatas'][0] if health_results['metadatas'] else []
                },
                'products': {
                    'documents': product_results['documents'][0] if product_results['documents'] else [],
                    'metadatas': product_results['metadatas'][0] if product_results['metadatas'] else []
                }
            }
            
        except Exception as e:
            print(f"Error getting relevant content: {str(e)}")
            return {
                'health_tips': {'documents': [], 'metadatas': []}, 
                'products': {'documents': [], 'metadatas': []}
            }

    def get_health_tips(self, category: Optional[str] = None, limit: int = 5) -> Dict:
        """Get health tips with proper error handling"""
        try:
            if category:
                results = self.health_tips.query(
                    query_texts=["health tips"],
                    where={"category": category},
                    n_results=min(limit, len(self.health_tips.get()['ids']))
                )
            else:
                results = self.health_tips.query(
                    query_texts=["health tips"],
                    n_results=min(limit, len(self.health_tips.get()['ids']))
                )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting health tips: {str(e)}")
            return {'documents': [], 'metadatas': []}

    def get_products_by_category(self, category: str) -> Dict:
        """Get products by category with proper error handling"""
        try:
            results = self.products.query(
                query_texts=[""],
                where={"category": category},
                n_results=min(5, len(self.products.get()['ids']))
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting products: {str(e)}")
            return {'documents': [], 'metadatas': []}

    def add_health_tip(self, tip_id: str, tip_text: str, category: str):
        """Add a health tip to the database"""
        try:
            self.health_tips.add(
                documents=[tip_text],
                metadatas=[{"category": category}],
                ids=[tip_id]
            )
            self.client.persist()
        except Exception as e:
            print(f"Error adding health tip: {str(e)}")

    def add_faq(self, faq_id: str, question: str, answer: str, category: str):
        """Add an FAQ to the database (using a dedicated collection if available, or health_tips)"""
        try:
            # Check if faq collection exists, if not use health_tips
            try:
                faq_collection = self.client.get_or_create_collection(
                    name="faqs",
                    embedding_function=self.embedding_function
                )
                faq_collection.add(
                    documents=[f"Q: {question}\nA: {answer}"],
                    metadatas=[{"category": category, "question": question, "answer": answer}],
                    ids=[faq_id]
                )
            except:
                self.health_tips.add(
                    documents=[f"Q: {question}\nA: {answer}"],
                    metadatas=[{"category": category, "type": "faq"}],
                    ids=[faq_id]
                )
            self.client.persist()
        except Exception as e:
            print(f"Error adding FAQ: {str(e)}")

    def add_product(self, product_id: str, name: str, description: str, category: str, price: float):
        """Add a product to the database"""
        try:
            self.products.add(
                documents=[description],
                metadatas=[{"name": name, "category": category, "price": price}],
                ids=[product_id]
            )
            self.client.persist()
        except Exception as e:
            print(f"Error adding product: {str(e)}")

    def store_chat(self, user_id: str, message: str, response: str) -> bool:
        """Store chat with proper error handling"""
        try:
            chat_id = f"chat_{user_id}_{datetime.now().timestamp()}"
            self.chat_history.add(
                documents=[f"User: {message}\nBot: {response}"],
                metadatas=[{
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[chat_id]
            )
            self.client.persist()
            return True
        except Exception as e:
            print(f"Error storing chat: {str(e)}")
            return False

    def store_feedback(self, user_id: str, rating: int, comment: str) -> bool:
        """Store user feedback"""
        try:
            feedback_id = f"feedback_{user_id}_{datetime.now().timestamp()}"
            self.feedback.add(
                documents=[comment],
                metadatas=[{
                    "user_id": user_id,
                    "rating": rating,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[feedback_id]
            )
            self.client.persist()
            return True
        except Exception as e:
            print(f"Error storing feedback: {str(e)}")
            return False

    def get_all_feedback(self) -> List[Dict]:
        """Get all feedback entries"""
        try:
            results = self.feedback.get()
            feedback_list = []
            
            if results['ids']:
                for i in range(len(results['ids'])):
                    feedback_list.append({
                        "id": results['ids'][i],
                        "comment": results['documents'][i],
                        "rating": results['metadatas'][i].get("rating", 0),
                        "timestamp": results['metadatas'][i].get("timestamp"),
                        "user_id": results['metadatas'][i].get("user_id")
                    })
            
            # Sort by timestamp descending
            feedback_list.sort(key=lambda x: x['timestamp'] or '', reverse=True)
            return feedback_list
        except Exception as e:
            print(f"Error getting all feedback: {str(e)}")
            return []

    def get_chat_history(self, user_id: str, limit: int = 10) -> Dict:
        """Get chat history with proper error handling"""
        try:
            results = self.chat_history.query(
                query_texts=[""],
                where={"user_id": user_id},
                n_results=min(limit, len(self.chat_history.get()['ids']))
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return {'documents': [], 'metadatas': []}
        