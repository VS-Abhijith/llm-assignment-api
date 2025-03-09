from fastapi import FastAPI, UploadFile, Form
import zipfile
import pandas as pd
import os

app = FastAPI()

@app.post("/api/")
async def get_answer(question: str = Form(...), file: UploadFile = None):
    if file:
        # Save and extract the ZIP file
        file_location = f"temp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        with zipfile.ZipFile(file_location, "r") as zip_ref:
            zip_ref.extractall("temp/extracted")

        # Find CSV file inside extracted folder
        csv_files = [f for f in os.listdir("temp/extracted") if f.endswith(".csv")]
        if csv_files:
            df = pd.read_csv(f"temp/extracted/{csv_files[0]}")
            if "answer" in df.columns:
                return {"answer": str(df["answer"].iloc[0])}
    
    # If no file or not a ZIP, use a placeholder answer (replace with LLM response)
    return {"answer": "This is a sample answer from the LLM."}
