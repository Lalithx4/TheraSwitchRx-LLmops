from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
import warnings
import os
import shutil
from pathlib import Path

# Suppress deprecation warnings for now
warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
load_dotenv()

class VectorStoreBuilder:
    def __init__(self, csv_path: str, persist_dir: str = "chroma_db"):
        self.csv_path = csv_path
        self.persist_dir = persist_dir
        
        # Verify CSV file exists
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
            
        # Initialize embeddings
        print("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        print("Embeddings model initialized successfully")
    
    def clear_existing_db(self):
        """Clear existing vector store if it exists"""
        if os.path.exists(self.persist_dir):
            print(f"Removing existing vector store at {self.persist_dir}")
            shutil.rmtree(self.persist_dir)
    
    def build_and_save_vectorstore(self, force_rebuild: bool = False):
        """
        Build and save vector store from CSV data
        
        Args:
            force_rebuild: If True, rebuild even if vector store exists
        """
        # Check if vector store already exists
        if os.path.exists(self.persist_dir) and not force_rebuild:
            print(f"Vector store already exists at {self.persist_dir}")
            try:
                return self.load_vector_store()
            except Exception as e:
                print(f"Failed to load existing vector store: {e}")
                print("Rebuilding vector store...")
                self.clear_existing_db()
        
        try:
            # Load CSV data
            print(f"Loading CSV from: {self.csv_path}")
            loader = CSVLoader(
                file_path=self.csv_path,
                encoding='utf-8',
                csv_args={
                    'delimiter': ',',
                    'quotechar': '"',
                    'fieldnames': None  # Let it auto-detect field names
                }
            )
            
            data = loader.load()
            print(f"Loaded {len(data)} documents from CSV")
            
            if len(data) == 0:
                raise ValueError("No data loaded from CSV file")
            
            # Split documents
            print("Splitting documents...")
            splitter = CharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                separator="\n",
                length_function=len
            )
            texts = splitter.split_documents(data)
            print(f"Created {len(texts)} text chunks")
            
            # Create and persist vector store
            print("Creating vector store...")
            # IMPORTANT: Use 'embedding' parameter for creation
            db = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,  # Note: 'embedding' not 'embeddings'
                persist_directory=self.persist_dir,
                collection_name="medical_recommendations"
            )
            
            # Explicitly persist (may not be needed in newer versions)
            try:
                db.persist()
            except AttributeError:
                # persist() method might not exist in newer versions
                pass
            
            print(f"Vector store saved to {self.persist_dir}")
            return db
            
        except Exception as e:
            print(f"Error building vector store: {e}")
            raise
    
    def load_vector_store(self):
        """Load existing vector store"""
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError(f"No vector store found at {self.persist_dir}")
        
        try:
            print(f"Loading vector store from {self.persist_dir}")
            # IMPORTANT: Use 'embedding_function' parameter for loading
            db = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,  # Note: 'embedding_function' not 'embeddings'
                collection_name="medical_recommendations"
            )
            print("Vector store loaded successfully")
            return db
        except Exception as e:
            print(f"Error loading vector store: {e}")
            # Try alternative parameter name if the above fails
            try:
                db = Chroma(
                    persist_directory=self.persist_dir,
                    embedding=self.embeddings,  # Try 'embedding' instead
                    collection_name="medical_recommendations"
                )
                print("Vector store loaded successfully (using 'embedding' parameter)")
                return db
            except Exception as e2:
                print(f"Error with alternative loading approach: {e2}")
                raise e  # Raise the original error
    
    def test_vector_store(self, query: str = "test", k: int = 3):
        """Test the vector store with a sample query"""
        try:
            db = self.load_vector_store()
            results = db.similarity_search(query, k=k)
            print(f"Found {len(results)} similar documents for query: '{query}'")
            return results
        except Exception as e:
            print(f"Error testing vector store: {e}")
            return None
    
    def get_retriever(self, search_kwargs: dict = None):
        """Get a retriever from the vector store"""
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        
        db = self.load_vector_store()
        return db.as_retriever(search_kwargs=search_kwargs)


# Backward compatibility wrapper
class VectorStoreBuilderCompat(VectorStoreBuilder):
    """Compatibility wrapper that handles both old and new parameter names"""
    
    def load_vector_store(self):
        """Load with automatic parameter detection"""
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError(f"No vector store found at {self.persist_dir}")
        
        # Try different parameter combinations
        param_combinations = [
            {"embedding_function": self.embeddings},
            {"embedding": self.embeddings},
            {"embeddings": self.embeddings},  # Old parameter name
        ]
        
        last_error = None
        for params in param_combinations:
            try:
                print(f"Trying to load with parameters: {list(params.keys())}")
                db = Chroma(
                    persist_directory=self.persist_dir,
                    collection_name="medical_recommendations",
                    **params
                )
                print(f"Successfully loaded with: {list(params.keys())}")
                return db
            except TypeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue
        
        # If all attempts failed, raise the last error
        raise last_error if last_error else Exception("Failed to load vector store")


# Usage example for GCP deployment
if __name__ == "__main__":
    import sys
    
    # Get CSV path from environment variable or command line
    csv_path = os.environ.get('CSV_PATH', 'data.csv')
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    # Initialize vector store builder with compatibility wrapper
    try:
        # Use compatibility wrapper for better version handling
        builder = VectorStoreBuilderCompat(
            csv_path=csv_path,
            persist_dir='/tmp/chroma_db'  # Use /tmp for GCP Cloud Run
        )
        
        # Force rebuild to ensure clean state
        db = builder.build_and_save_vectorstore(force_rebuild=True)
        
        # Test the vector store
        results = builder.test_vector_store("medical recommendation")
        
        print("Vector store initialization completed successfully")
        
    except Exception as e:
        print(f"Failed to initialize vector store: {e}")
        sys.exit(1)

