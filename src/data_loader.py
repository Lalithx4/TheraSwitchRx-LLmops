import pandas as pd
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedDataLoader:
    def __init__(self, original_csv: str, processed_csv: str):
        """
        Initialize the Medicine Data Loader
        
        Args:
            original_csv: Path to the original medicine CSV file
            processed_csv: Path to save the processed CSV file
        """
        self.original_csv = original_csv
        self.processed_csv = processed_csv
        self.medicine_names = set()  # Track all medicine names for validation

    def load_and_process(self):
        """
        Load and process the medicine dataset with improved structure
        to prevent hallucinations
        """
        try:
            # Load the CSV file
            logger.info(f"Loading medicine data from {self.original_csv}")
            df = pd.read_csv(self.original_csv, encoding='utf-8', on_bad_lines='skip')
            
            # Convert column names to lowercase for case-insensitive matching
            df.columns = df.columns.str.lower()
            
            # Check for required columns
            required_columns = {
                'name', 
                'salt_composition', 
                'alternatives',
                'manufacturer_name',
                'medicine_desc'
            }
            
            missing = required_columns - set(df.columns)
            if missing:
                logger.warning(f"Available columns: {list(df.columns)}")
                essential_columns = {'name', 'salt_composition', 'alternatives'}
                essential_missing = essential_columns - set(df.columns)
                if essential_missing:
                    raise ValueError(f"Missing essential columns: {essential_missing}")
                else:
                    logger.warning(f"Some columns missing: {missing}, proceeding with available columns")
            
            # Clean and standardize medicine names
            df['name'] = df['name'].fillna('Unknown Medicine').str.strip()
            
            # Store all valid medicine names for validation
            self.medicine_names = set(df['name'].str.lower().unique())
            logger.info(f"Loaded {len(self.medicine_names)} unique medicines")
            
            # Log sample medicines for verification
            sample_medicines = list(self.medicine_names)[:10]
            logger.info(f"Sample medicines in database: {sample_medicines}")
            
            # Check if common medicines exist
            test_medicines = ['magvion', 'paracetamol', 'aspirin', 'shelcal']
            for med in test_medicines:
                exists = med.lower() in self.medicine_names
                logger.info(f"Medicine '{med}': {'FOUND' if exists else 'NOT FOUND'} in database")
            
            # Handle missing values with clear indicators
            df['salt_composition'] = df['salt_composition'].fillna('Composition not specified')
            df['alternatives'] = df['alternatives'].fillna('No alternatives listed')
            df['manufacturer_name'] = df.get('manufacturer_name', pd.Series(['Unknown'] * len(df))).fillna('Unknown')
            df['medicine_desc'] = df.get('medicine_desc', pd.Series(['No description'] * len(df))).fillna('No description')
            df['side_effects'] = df.get('side_effects', pd.Series(['Not specified'] * len(df))).fillna('Not specified')
            df['price'] = df.get('price', pd.Series([0.0] * len(df))).fillna(0.0)
            
            # IMPORTANT: Create structured combined info with validation markers
            logger.info("Creating structured information fields for vector search")
            
            # Add validation prefix to prevent hallucination
            df['combined_info'] = (
                "DATABASE_ENTRY_START | " +
                "Medicine Name: " + df['name'].astype(str) + 
                " | Salt Composition: " + df['salt_composition'].astype(str) +
                " | Description: " + df['medicine_desc'].astype(str) +
                " | Manufacturer: " + df['manufacturer_name'].astype(str) +
                " | Price: ₹" + df['price'].astype(str) +
                " | Alternative Medicines: " + df['alternatives'].astype(str) +
                " | Side Effects: " + df['side_effects'].astype(str) +
                " | DATABASE_ENTRY_END"
            )
            
            # Create search keywords with exact medicine names
            df['search_keywords'] = (
                "EXACT_NAME: " + df['name'].astype(str) + " | " +
                "COMPOSITION: " + df['salt_composition'].astype(str) + " | " +
                "ALTERNATIVES: " + df['alternatives'].astype(str).replace(',', ' ')
            )
            
            # Add a validation field
            df['is_valid_entry'] = True
            df['medicine_id'] = range(1, len(df) + 1)
            
            # Save processed data with additional validation columns
            logger.info(f"Saving processed data to {self.processed_csv}")
            df[['medicine_id', 'combined_info', 'search_keywords', 'name', 
                'salt_composition', 'alternatives', 'price', 'manufacturer_name',
                'is_valid_entry']].to_csv(
                self.processed_csv, 
                index=False, 
                encoding='utf-8'
            )
            
            # Save a separate validation file with all medicine names
            validation_file = self.processed_csv.replace('.csv', '_validation.json')
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_medicines': len(self.medicine_names),
                    'medicine_names': sorted(list(self.medicine_names)),
                    'processed_date': pd.Timestamp.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Validation file saved to {validation_file}")
            
            logger.info(f"Successfully processed {len(df)} medicine records")
            
            # Create a summary report
            self.create_data_summary(df)
            
            return self.processed_csv
            
        except Exception as e:
            logger.error(f"Error processing medicine data: {e}")
            raise
    
    def create_data_summary(self, df):
        """Create a summary of the processed data for quality checking"""
        summary = {
            'total_records': len(df),
            'unique_medicines': len(df['name'].unique()),
            'medicines_with_alternatives': len(df[df['alternatives'] != 'No alternatives listed']),
            'medicines_with_price': len(df[df['price'] > 0]),
            'unique_manufacturers': len(df['manufacturer_name'].unique()),
            'unique_compositions': len(df['salt_composition'].unique())
        }
        
        logger.info("Data Summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        
        # Save summary to file
        summary_file = self.processed_csv.replace('.csv', '_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {summary_file}")
    
    def validate_medicine_exists(self, medicine_name):
        """
        Check if a medicine exists in the database
        """
        return medicine_name.lower() in self.medicine_names
    
    def load_for_alternative_search(self):
        """
        Special method to create a dataset optimized for finding alternatives
        with validation
        """
        try:
            logger.info("Creating alternative medicine search dataset")
            df = pd.read_csv(self.original_csv, encoding='utf-8', on_bad_lines='skip')
            
            # Convert column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Clean medicine names
            df['name'] = df['name'].fillna('Unknown').str.strip()
            
            # Create alternative-focused combined field with validation markers
            df['alternative_search'] = (
                "VALID_ALTERNATIVE_ENTRY | " +
                "For medicine: " + df['name'].astype(str) +
                " (Composition: " + df['salt_composition'].astype(str) + ") " +
                "the verified alternatives are: " + df['alternatives'].astype(str) +
                ". These are medicines with similar therapeutic effects. " +
                "| END_ALTERNATIVE_ENTRY"
            )
            
            # Create a price comparison field
            df['price_info'] = (
                "PRICE_ENTRY | Medicine: " + df['name'].astype(str) + 
                " | Cost: ₹" + df['price'].astype(str) +
                " | Alternatives: " + df['alternatives'].astype(str) +
                " | END_PRICE_ENTRY"
            )
            
            # Add validation column
            df['is_database_verified'] = True
            
            # Save alternative-focused dataset
            alternative_csv = self.processed_csv.replace('.csv', '_alternatives.csv')
            df[['alternative_search', 'price_info', 'name', 'alternatives', 
                'salt_composition', 'price', 'is_database_verified']].to_csv(
                alternative_csv,
                index=False,
                encoding='utf-8'
            )
            
            logger.info(f"Alternative search dataset saved to {alternative_csv}")
            return alternative_csv
            
        except Exception as e:
            logger.error(f"Error creating alternative search dataset: {e}")
            raise

# Validator class to use with your retrieval system
class MedicineValidator:
    def __init__(self, validation_file_path):
        """Load the validation data"""
        with open(validation_file_path, 'r', encoding='utf-8') as f:
            self.validation_data = json.load(f)
        self.valid_medicines = set([m.lower() for m in self.validation_data['medicine_names']])
        logger.info(f"Loaded {len(self.valid_medicines)} valid medicine names for validation")
    
    def is_valid_medicine(self, medicine_name):
        """Check if a medicine exists in the database"""
        return medicine_name.lower().strip() in self.valid_medicines
    
    def get_similar_names(self, medicine_name):
        """Get similar medicine names for suggestions"""
        from difflib import get_close_matches
        similar = get_close_matches(
            medicine_name.lower(), 
            self.valid_medicines, 
            n=5, 
            cutoff=0.6
        )
        return similar

# Example usage with validation
if __name__ == "__main__":
    # Initialize the loader
    loader = MedDataLoader(
        original_csv="indian_medicine_with_alternatives.csv",
        processed_csv="processed_medicines.csv"
    )
    
    # Process the data
    processed_file = loader.load_and_process()
    print(f"Processed file saved to: {processed_file}")
    
    # Create alternative-focused dataset
    alt_file = loader.load_for_alternative_search()
    print(f"Alternative search file saved to: {alt_file}")
    
    # Test validation
    validator = MedicineValidator("processed_medicines_validation.json")
    
    test_medicines = ["Paracetamol", "Magvion", "Aspirin", "NonExistentMed"]
    for med in test_medicines:
        if validator.is_valid_medicine(med):
            print(f"✓ {med} exists in database")
        else:
            print(f"✗ {med} NOT found in database")
            similar = validator.get_similar_names(med)
            if similar:
                print(f"  Suggestions: {similar}")