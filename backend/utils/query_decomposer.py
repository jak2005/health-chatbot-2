# backend/utils/query_decomposer.py
import google.generativeai as genai
from openai import AsyncOpenAI
from typing import List, Dict
import json
import asyncio

class QueryDecomposer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key and api_key.startswith("gsk_"):
            self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            self.model_name = "llama-3.3-70b-versatile"
            self.is_groq = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 20,
                    "max_output_tokens": 1024,
                }
            )
            self.is_groq = False
        
    async def decompose_query(self, query: str) -> Dict[str, List[str]]:
        """Decompose main query into sub-queries and determine search necessity"""
        prompt = f"""Analyze the following health-related query and:
2. Decompose into 3-4 specific sub-queries if research is needed

Query: {query}

Provide response in the following JSON format:
{{
    "needs_research": true/false,
    "sub_queries": [
        "What is [topic] and its basic mechanisms?",
        "What are the proven benefits of [topic]?",
        "What are the potential risks and side effects of [topic]?",
        "What does recent scientific research say about [topic]'s safety?"
    ]
}}

If research is not needed, return empty sub_queries list.
"""

        try:
            print(f"\n=== Decomposing Query: {query} ===")
            
            if self.is_groq:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a health query analyzer. Respond ONLY with JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content
            else:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
                text = response.text
            
            # Parse JSON response
            # Remove markdown code blocks if present
            clean_text = text.replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_text)
            
            print(f"Needs Research: {result['needs_research']}")
            if result.get('needs_research'):
                print("Sub-queries:", result.get('sub_queries'))
            
            return result
            
        except Exception as e:
            print(f"Error decomposing query: {str(e)}")
            return {
                "needs_research": False,
                "sub_queries": []
            }