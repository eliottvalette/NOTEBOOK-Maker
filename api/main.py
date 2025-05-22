from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

OUTPUT_PATH = "Output/generated_notebook.ipynb"

@app.post("/generate-notebook/")
def generate_notebook(dataset_style: str = Form(...)):
    # Appelle run.py avec le dataset_style choisi
    subprocess.run([
        "python", "run.py", dataset_style
    ], check=True)
    # On suppose que le notebook est généré à OUTPUT_PATH
    if os.path.exists(OUTPUT_PATH):
        return FileResponse(OUTPUT_PATH, media_type="application/x-ipynb+json", filename="notebook.ipynb")
    return {"error": "Notebook not found"} 