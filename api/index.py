from fastapi import FastAPI, UploadFile, Form, HTTPException
import zipfile
import pandas as pd
import os

app = FastAPI()

@app.post("/api/")
async def get_answer(question: str = Form(...), file: UploadFile = None):
    try:
        temp_dir = "/tmp"

        if file:
            file_location = os.path.join(temp_dir, file.filename)

            # Save uploaded ZIP file
            with open(file_location, "wb") as f:
                f.write(await file.read())

            # Extract ZIP contents
            extracted_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)
            
            with zipfile.ZipFile(file_location, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)

            # Find CSV file inside extracted folder
            csv_files = [f for f in os.listdir(extracted_dir) if f.endswith(".csv")]
            if csv_files:
                csv_path = os.path.join(extracted_dir, csv_files[0])
                df = pd.read_csv(csv_path)

                # Check if the "answer" column exists
                if "answer" in df.columns and not df["answer"].empty:
                    return {"answer": str(df["answer"].iloc[0])}
                else:
                    raise HTTPException(status_code=400, detail="CSV file does not contain an 'answer' column or is empty.")

        return {"answer": "This is a sample answer from the LLM."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
