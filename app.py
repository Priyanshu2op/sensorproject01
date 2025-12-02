import os
import sys
from flask import Flask, render_template, jsonify, request, send_file
from src.exception import CustomException
from src.logger import logging as lg

# Assuming your pipelines are structured correctly
from src.pipelines.train_pipline import TrainingPipeline
from src.pipelines.predict_pipline import PredictionPipeline


app = Flask(__name__)


@app.route("/")
def home():
    """Renders the main welcome page."""
    lg.info("Accessed the home page.")
    return "Welcome to the Wafer Fault Detection Application!"


@app.route("/train", methods=['GET'])
def train_route():
    """Initiates the training pipeline."""
    try:
        lg.info("Starting the training pipeline initiated via /train route.")
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        lg.info("Training pipeline completed successfully.")
        
        # Return a simple success message
        return "Training Completed Successfully."

    except Exception as e:
        lg.error(f"Error during training pipeline execution: {e}")
        # Re-raise the custom exception for detailed logging
        raise CustomException(e, sys)


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    """
    Handles file upload for prediction.
    GET: Renders the upload form (upload_file.html).
    POST: Processes the uploaded CSV file, runs prediction, and triggers file download.
    """
    
    try:
        if request.method == 'POST':
            lg.info("POST request received. Starting prediction pipeline.")
            
            # The PredictionPipeline now handles the file upload logic internally
            # It takes the request object to access request.files['file']
            prediction_pipeline = PredictionPipeline(request)
            
            # The run_pipeline method returns the PredictionPipelineConfig object,
            # which contains the path to the resulting prediction file.
            prediction_config = prediction_pipeline.run_pipeline()

            lg.info("Prediction completed. Preparing file download.")
            
            # Ensure your system uses the correct path separators
            prediction_file_path = prediction_config.prediction_file_path
            prediction_file_name = prediction_config.prediction_file_name
            
            # Send the predicted file back to the user
            return send_file(
                prediction_file_path,
                download_name=prediction_file_name,
                as_attachment=True
            )

        else:
            # GET request: render the upload page, assuming it's in the 'templates' folder
            lg.info("GET request received. Rendering upload page (upload_file.html).")
            return render_template('upload_file.html')
            
    except CustomException as e:
        # Catch and log the CustomException with the detailed message
        lg.error(f"Custom Exception during prediction: {str(e)}")
        # Provide a simple error message to the user/browser
        return jsonify({"error": str(e)}), 500
        
    except Exception as e:
        # Catch any other unexpected exceptions
        lg.error(f"An unexpected error occurred: {e}")
        # Raise the custom exception to utilize its detailed logging features
        raise CustomException(e, sys)


if __name__ == "__main__":
    # Running on 0.0.0.0 allows access from external interfaces (like Docker or networked systems)
    # and is generally safe for local development.
    app.run(host="0.0.0.0", port=5000, debug=True)