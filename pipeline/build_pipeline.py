from src.data_loader import MedDataLoader
from src.vector_store import VectorStoreBuilder
from dotenv import load_dotenv
load_dotenv()
from utils.logger import get_logger
from utils.custom_exception import CustomException  

logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting to build pipeline ")
        loader=MedDataLoader("data/indian_medicine_all_with_alternatives.csv","data/processed_med_alternatives.csv")
        processed_csv=loader.load_and_process()
        logger.info("Data loaded and processed sucesfully...")
        vector_builder=VectorStoreBuilder(csv_path=processed_csv)
        vector_builder.build_and_save_vectorstore()

        logger.info("vector store built Successfully")
        logger.info("Pipeline build Succefully")
    except Exception as e:
        logger.error(f"Failed to build pipeline {str(e)}")
        raise CustomException("Error during pipeline building" , e)                    
            

if __name__=="__main__":
    main()
