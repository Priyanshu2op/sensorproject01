import sys

def error_message_detail(error, error_detail: sys):
    """
    Constructs a detailed error message including file name and line number 
    from the traceback information provided in 'error_detail'.
    """
    # Unpack the traceback information
    _, _, exc_tb = error_detail.exc_info()

    # Get file name and line number
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno

    # Construct the detailed error message string
    error_message = "Error occurred in Python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, line_number, str(error)
    ) 

    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        """
        Initializes the custom exception.
        
        Correction: The keyword argument 'error_details' in the function call 
        has been removed and replaced with positional arguments to match the 
        definition of error_message_detail.
        """
        # Call the parent class constructor with the simplified error message
        super().__init__(error_message) 
        
        # Set the detailed error message using the helper function
        self.error_message = error_message_detail(
            error_message, 
            error_detail  # Pass as a positional argument
        )

    def __str__(self):
        """Returns the detailed error message when the exception is printed."""
        return self.error_message