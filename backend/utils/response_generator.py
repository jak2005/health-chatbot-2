# backend/utils/response_generator.py
import google.generativeai as genai
from openai import AsyncOpenAI
from typing import Dict, List, Optional
import asyncio

class ResponseGenerator:
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
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            self.is_groq = False
    
    async def generate_response(
        self, 
        original_query: str, 
        sub_queries: List[str], 
        research_results: Dict[str, str],
        rag_context: Optional[str] = None,
        user_profile: Optional[Dict] = None
    ) -> str:
        """Generate natural, contextual response using Chain of Thought"""
        try:
            print("\n=== Generating Response ===")
            
            # Prepare context information
            context_parts = []
            
            # Add RAG context if available
            if rag_context:
                context_parts.append(f"Local Knowledge:\n{rag_context}")
            
            # Add user profile context if available
            if user_profile and user_profile.get('summary'):
                context_parts.append(f"User Context:\n{user_profile['summary']}")
            
            # Add research findings
            if research_results:
                research_summary = "\n".join([
                    f"Research on {query}:\n{results}"
                    for query, results in research_results.items()
                ])
                context_parts.append(f"Research Findings:\n{research_summary}")
            
            # Combine all context
            context = "\n\n".join(context_parts)
            
            prompt = f"""As a health advisor, use Chain of Thought reasoning to provide a helpful response.

User Query: {original_query}

Context Information:
{context}

Think through these steps:

1. Query Analysis:
- What is the main health topic/concern?
- Is this a general or specific question?
- What level of detail is appropriate?

2. Context Evaluation:
- What relevant information do we have?
- Are there any safety concerns?
- What research findings are most relevant?

3. Response Planning:
- What key points should be addressed?
- Are there any warnings needed?
- Should we recommend professional consultation?

4. Response Formulation:
- Start with direct answer
- Include relevant context naturally
- Add safety information if needed
- Suggest professional help if appropriate

Important Guidelines:
- Only mention general health tips (water, sleep, vitamins) if directly relevant
- Include product recommendations only if specifically relevant
- Keep the response focused on the user's question
- Be clear about limitations and uncertainties
- Maintain a conversational but professional tone

Now, think through your response step by step, then provide a natural, focused answer that addresses the user's specific question.

Reasoning:"""

            print(f"Getting CoT response from {'Groq' if self.is_groq else 'Gemini'}...")
            
            if self.is_groq:
                reasoning_response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a health advisor using Chain of Thought reasoning."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                reasoning_text = reasoning_response.choices[0].message.content
            else:
                loop = asyncio.get_event_loop()
                reasoning_response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
                reasoning_text = reasoning_response.text
            
            # Generate final response without the reasoning
            final_prompt = f"""Based on this reasoning:

{reasoning_text}

Generate a natural, conversational response that focuses specifically on answering the user's question:
"{original_query}"

Remember:
- Be direct and relevant
- Don't force general health tips
- Only mention products if truly relevant
- Keep it concise and natural

Final Response:"""

            if self.is_groq:
                final_response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a health advisor. Provide a natural response."},
                        {"role": "user", "content": final_prompt}
                    ],
                    temperature=0.7
                )
                final_text = final_response.choices[0].message.content
            else:
                loop = asyncio.get_event_loop()
                final_response = await loop.run_in_executor(None, lambda: self.model.generate_content(final_prompt))
                final_text = final_response.text
            
            print("Response generated successfully")
            return final_text
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return """I apologize, but I'm having trouble generating a response right now. 
For your safety and best advice, please consider consulting with a healthcare professional."""