# backend/services/health_tips.py
from typing import Dict, List, Optional
import random

class HealthTipsService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.categories = ['sleep', 'sexual_health', 'general_health', 'lifestyle']
        
        self.default_tips = []
    
    def get_random_tip(self, category: Optional[str] = None) -> Dict:
        """Get a random health tip"""
        try:
            results = self.db_manager.get_health_tips(category=category, limit=5)
            
            if results and results.get('documents') and len(results['documents']) > 0:
                index = random.randint(0, len(results['documents']) - 1)
                return {
                    "tip": results['documents'][index],
                    "category": results['metadatas'][index]['category'],
                    "related_products": self.get_related_products(results['metadatas'][index]['category'])
                }
            return {
                "tip": "Ask me any health related question to get started!",
                "category": "general",
                "related_products": []
            }
        except Exception as e:
            print(f"Error getting tip: {str(e)}")
            return {
                "tip": "I am ready to help with your health questions.",
                "category": "general",
                "related_products": []
            }

    def get_related_products(self, category: str) -> List[Dict]:
        """Get related products"""
        try:
            results = self.db_manager.get_products_by_category(category)
            if results and results.get('documents'):
                return [{
                    "name": metadata.get('name', 'Product'),
                    "description": doc,
                    "price": metadata.get('price', 0.0)
                } for doc, metadata in zip(results['documents'], results['metadatas'])]
            return []
        except:
            return []