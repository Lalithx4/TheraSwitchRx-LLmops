from src.vector_store import VectorStoreBuilder
from src.recommender import MedRecommender
from config.config import GROQ_API_KEY,MODEL_NAME
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class MedRecommendationPipeline:
    def __init__(self,persist_dir="chroma_db"):
        try:
            logger.info("Intializing Recommdation Pipeline")

            vector_builder = VectorStoreBuilder(csv_path="data/indian_medicine_all_with_alternatives.csv" , persist_dir=persist_dir)

            # Try to load existing vector store, if it fails, build a new one
            try:
                retriever = vector_builder.load_vector_store().as_retriever()
                logger.info("Loaded existing vector store")
            except Exception as load_error:
                logger.info(f"Failed to load existing vector store: {load_error}")
                logger.info("Building new vector store from CSV data...")
                vector_builder.build_and_save_vectorstore()
                retriever = vector_builder.load_vector_store().as_retriever()
                logger.info("Built and loaded new vector store")

            self.recommender = MedRecommender(retriever,GROQ_API_KEY,MODEL_NAME)

            logger.info("Pipleine intialized sucesfully...")

        except Exception as e:
            logger.error(f"Failed to intialize pipeline {str(e)}")
            raise CustomException("Error during pipeline intialization" , e)
        
    def recommend(self,query:str) -> str:
        try:
            logger.info(f"Recived a query {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Recommendation generated sucesfulyy...")
            return recommendation
        except Exception as e:
            logger.error(f"Failed to get recommendation {str(e)}")
            raise CustomException("Error during getting recommendation" , e)
        


        