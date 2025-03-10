from fastapi import FastAPI, UploadFile, Form
import zipfile
import pandas as pd
import os
from mangum import Mangum  # Required for Vercel

app = FastAPI()

@app.post("/api/")
async def get_answer(question: str = Form(...), file: UploadFile = None):
    temp_dir = "temp"
    extracted_dir = "temp/extracted"

    # Ensure temp directories exist
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)

    if file:
        file_location = os.path.join(temp_dir, file.filename)

        # Save uploaded ZIP file
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Extract ZIP contents
        with zipfile.ZipFile(file_location, "r") as zip_ref:
            zip_ref.extractall(extracted_dir)

        # Find CSV file inside extracted folder
        csv_files = [f for f in os.listdir(extracted_dir) if f.endswith(".csv")]
        if csv_files:
            df = pd.read_csv(os.path.join(extracted_dir, csv_files[0]))
            if "answer" in df.columns:
                return {"answer": str(df["answer"].iloc[0])}

    # If no file or not a ZIP, return default answer
    return {"answer": "This is a sample answer from the LLM."}

# ASGI handler for Vercel
handler = Mangum(app)
