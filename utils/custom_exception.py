import sys

class CustomException(Exception):
    """
    Custom exception class for the Med Recommender application.
    """
    
    def __init__(self, error_message: str, error_detail: Exception = None):
        """
        Initialize the custom exception.
        
        Args:
            error_message: A descriptive error message
            error_detail: The original exception that caused this error
        """
        super().__init__(error_message)
        self.error_message = error_message
        self.error_detail = error_detail
        
        if error_detail:
            _, _, exc_tb = sys.exc_info()
            if exc_tb:
                self.line_number = exc_tb.tb_lineno
                self.file_name = exc_tb.tb_frame.f_code.co_filename
            else:
                self.line_number = None
                self.file_name = None
        else:
            self.line_number = None
            self.file_name = None
    
    def __str__(self):
        """
        Return a formatted error message.
        """
        if self.line_number and self.file_name:
            return f"Error occurred in {self.file_name} at line {self.line_number}: {self.error_message}"
        else:
            return f"Error: {self.error_message}"
