import shutil
import os
import sys 
import pandas as pd 
import pickle
from src.logger import logging
from src.exception import CustomException
from flask import request
# Assuming TARGET_COLUMN, artifact_folder, and others are defined in constants
from src.constants import TARGET_COLUMN, artifact_folder
from src.utils.main_utils import MainUtils
from dataclasses import dataclass

# --- Configuration Dataclass ---
@dataclass
class PredictionPipelineConfig:
    prediction_output_dirname: str = "prediction"
    prediction_file_name: str = "prediction.csv"
    # Assuming 'artifact_folder' is correctly imported from src.constants
    model_file_path: str = os.path.join(artifact_folder, 'model.pkl')
    preprocessor_path: str = os.path.join(artifact_folder, 'preprocessor.pkl')
    prediction_file_path: str = os.path.join(prediction_output_dirname, prediction_file_name)


# --- Prediction Pipeline Class ---
class PredictionPipeline:
    def __init__(self, request):
        self.request = request 
        self.utils = MainUtils()
        self.prediction_pipeline_config = PredictionPipelineConfig()

    def save_input_file(self) -> str:
        """
        Saves the uploaded file from the POST request.
        """
        try:
            pred_file_input_dir = "prediction_artifacts"
            os.makedirs(pred_file_input_dir, exist_ok=True)

            # --- Note: Using 'file' key, matching typical Flask/HTML input name ---
            input_csv_file = self.request.files.get('file')
            
            if not input_csv_file or input_csv_file.filename == '':
                logging.error("No file provided in the upload request.")
                raise CustomException("No file provided in the upload request.", sys)

            pred_file_path = os.path.join(pred_file_input_dir, input_csv_file.filename)
            
            input_csv_file.save(pred_file_path)
            logging.info(f"Input file saved to: {pred_file_path}")

            return pred_file_path
        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, feature: pd.DataFrame):
        """
        Loads the preprocessor and model, and generates predictions.
        """
        try:
            logging.info("Loading model and preprocessor for prediction.")
            model = self.utils.load_object(self.prediction_pipeline_config.model_file_path)
            preprocessor = self.utils.load_object(file_path=self.prediction_pipeline_config.preprocessor_path)

            transformed_x = preprocessor.transform(feature)
            preds = model.predict(transformed_x)
            logging.info("Prediction generated successfully.")

            return preds
        except Exception as e:
            raise CustomException(e, sys)

    def get_predicted_dataframe(self, input_dataframe_path: str):
        """
        Reads the input file, generates predictions, adds the prediction column,
        maps the predictions, and saves the final DataFrame.
        """
        try:
            prediction_columns_name: str = TARGET_COLUMN
            input_dataframe: pd.DataFrame = pd.read_csv(input_dataframe_path)

            # Use errors='ignore' to safely drop the column if it exists
            input_dataframe = input_dataframe.drop(columns="Unnamed: 0", errors='ignore')

            predictions = self.predict(input_dataframe)

            # Map predictions
            target_column_mapping = {0: 'bad', 1: 'good'}
            
            # Add and map the prediction column
            input_dataframe[prediction_columns_name] = predictions
            input_dataframe[prediction_columns_name] = input_dataframe[prediction_columns_name].map(target_column_mapping)
            
            # Save the predicted file
            os.makedirs(self.prediction_pipeline_config.prediction_output_dirname, exist_ok=True)
            input_dataframe.to_csv(self.prediction_pipeline_config.prediction_file_path, index=False)

            logging.info(f"Predictions completed and saved to: {self.prediction_pipeline_config.prediction_file_path}")
            
            return input_dataframe 

        except Exception as e:
            raise CustomException(e, sys)
            
    def run_pipeline(self):
        """
        Executes the entire prediction process and returns the config object 
        containing the output file path.
        
        --- FIX ---
        Changed the call from self.save_input_files() to self.save_input_file().
        """
        try:
            logging.info("Starting prediction pipeline.")
            # ERROR FIX: Corrected method name from 'save_input_files' to 'save_input_file'
            input_csv_path = self.save_input_file()
            self.get_predicted_dataframe(input_csv_path)

            logging.info("Prediction pipeline finished.")
            return self.prediction_pipeline_config
        except Exception as e:
            raise CustomException(e, sys)