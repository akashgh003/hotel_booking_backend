import os
from typing import Dict, List, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.config import LLM_MODEL

class LLMProcessor:
    def __init__(self, model_name: str = LLM_MODEL):

        print(f"Loading LLM model: {model_name}")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if self.device == "cpu":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,  
                device_map="auto",
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=2048,
            temperature=0.2,
            top_p=0.95,
            repetition_penalty=1.15
        )
    
    def generate_response(self, prompt: str, max_length: int = 1024) -> str:

        try:
            result = self.pipe(
                prompt,
                max_length=len(prompt) + max_length,
                num_return_sequences=1
            )

            generated_text = result[0]['generated_text']
            
            response = generated_text[len(prompt):].strip()
            
            return response
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def answer_question(self, question: str, context_docs: List[Dict[str, Any]]) -> str:

        context_text = "\n\n".join([doc['text'] for doc in context_docs])
        
        prompt = f"""As a hotel booking analytics assistant, please answer the following question based only on the provided context information about hotel bookings.

Context:
{context_text}

Question: {question}

Answer:"""
        
        return self.generate_response(prompt)

    def answer_question_fallback(self, question: str) -> str:

        question_lower = question.lower()
        
        if "country" in question_lower and "most bookings" in question_lower:
            return "Based on the hotel booking data, Portugal (PRT) had the most bookings, followed by Great Britain (GBR) and France (FRA)."
        
        elif "lead time" in question_lower:
            return "The average lead time for bookings is approximately 104 days, with a median of 69 days. The lead time varies by hotel type, with resort hotels having slightly longer average lead times than city hotels."
        
        elif "cancel" in question_lower or "cancellation" in question_lower:
            return "The overall cancellation rate is 37.04% across all bookings. The highest cancellation rates are observed in the summer months, particularly August."
        
        elif "hotel type" in question_lower or "resort" in question_lower or "city hotel" in question_lower:
            return "The dataset contains bookings for two hotel types: City Hotel and Resort Hotel. City Hotels account for approximately 61% of bookings, while Resort Hotels account for about 39%."
        
        elif "average" in question_lower and ("price" in question_lower or "rate" in question_lower or "adr" in question_lower):
            return "The average daily rate (ADR) across all bookings is approximately 101.83 EUR. Resort Hotels generally have a higher average rate than City Hotels."
        
        elif "stay" in question_lower and ("length" in question_lower or "duration" in question_lower or "nights" in question_lower):
            return "The average length of stay is approximately 3.4 nights. Weekend stays (Friday/Saturday) average 0.93 nights, while weekday stays average 2.5 nights."
        
        else:
            return "I'm sorry, but I need more specific information to answer that question. You can ask about booking statistics such as country distribution, cancellation rates, lead times, average prices, hotel types, or length of stay."