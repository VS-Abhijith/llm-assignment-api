from fastapi import FastAPI, UploadFile, Form, HTTPException
import zipfile
import pandas as pd
import os
import shutil
import logging
from mangum import Mangum  # Required for Vercel

app = FastAPI()

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

@app.post("/api/")
async def get_answer(question: str = Form(...), file: UploadFile = None):
    try:
        temp_dir = "/tmp/temp"
        extracted_dir = "/tmp/temp/extracted"

        # Ensure temp directories exist
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(extracted_dir, exist_ok=True)

        if file:
            file_location = os.path.join(temp_dir, file.filename)
            logging.info(f"Saving uploaded file to: {file_location}")

            # Save uploaded ZIP file
            with open(file_location, "wb") as f:
                f.write(await file.read())

            # Extract ZIP contents
            with zipfile.ZipFile(file_location, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)
            logging.info(f"Extracted ZIP to: {extracted_dir}")

            # Find CSV file inside extracted folder
            csv_files = [f for f in os.listdir(extracted_dir) if f.endswith(".csv")]
            if csv_files:
                csv_path = os.path.join(extracted_dir, csv_files[0])
                logging.info(f"Found CSV file: {csv_path}")
                
                df = pd.read_csv(csv_path)
                if "answer" in df.columns:
                    answer = str(df["answer"].iloc[0])
                    
                    # Cleanup after processing
                    os.remove(file_location)
                    shutil.rmtree(extracted_dir, ignore_errors=True)
                    
                    return {"answer": answer}

        # If no file or not a ZIP, return default answer
        return {"answer": "This is a sample answer from the LLM."}

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ASGI handler for Vercel
lambda_handler = Mangum(app)
