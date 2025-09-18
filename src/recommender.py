from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from src.prompt_template import (
    get_med_prompt, 
    get_med_search_prompt, 
    get_price_comparison_prompt, 
    get_composition_search_prompt
)
import re


class MedRecommender:
    def __init__(self,retriever,api_key:str,model_name:str):

        self.retriever=retriever
        self.api_key=api_key
        self.model_name=model_name
        self.llm=ChatGroq(api_key=self.api_key,model_name=self.model_name,temperature=0)
        
        # Store all prompt templates
        self.prompts = {
            'general': get_med_prompt(),
            'search': get_med_search_prompt(),
            'price': get_price_comparison_prompt(),
            'composition': get_composition_search_prompt()
        }
        
        # Default QA chain with general prompt
        self.qa_chain=RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt":self.prompts['general']}
        )

    def _detect_query_type(self, query: str) -> str:
        """
        Detect the type of query to use the appropriate prompt
        """
        query_lower = query.lower()
        
        # Price-related keywords
        price_keywords = ['price', 'cost', 'cheap', 'expensive', 'budget', 'affordable', 
                         'savings', 'compare price', 'cheaper', 'costlier']
        
        # Composition-related keywords  
        composition_keywords = ['composition', 'salt', 'ingredient', 'contains', 
                               'active ingredient', 'chemical', 'formula']
        
        # Search-related keywords
        search_keywords = ['condition', 'disease', 'symptom', 'treatment', 'cure', 
                          'for', 'help with', 'treat']
        
        if any(keyword in query_lower for keyword in price_keywords):
            return 'price'
        elif any(keyword in query_lower for keyword in composition_keywords):
            return 'composition'
        elif any(keyword in query_lower for keyword in search_keywords):
            return 'search'
        else:
            return 'general'
    
    def get_recommendation(self,query:str):
        """
        Get medicine recommendation using the most appropriate prompt
        """
        # Detect query type and use appropriate prompt
        query_type = self._detect_query_type(query)
        
        # Create QA chain with the appropriate prompt
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt":self.prompts[query_type]}
        )
        
        result = qa_chain.invoke({"query":query})
        return result['result']
    
