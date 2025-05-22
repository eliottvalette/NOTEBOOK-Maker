from fastapi import FastAPI, Form, Query
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
    gen_path = f"Output/gen_{dataset_style}.ipynb"
    if os.path.exists(gen_path):
        return FileResponse(gen_path, media_type="application/x-ipynb+json", filename=f"gen_{dataset_style}.ipynb")
    return {"error": "Notebook not found"}

@app.get("/download-executed-notebook/")
def download_executed_notebook(dataset_style: str = Query(...)):
    exe_path = f"Output/exe_{dataset_style}.ipynb"
    if os.path.exists(exe_path):
        return FileResponse(exe_path, media_type="application/x-ipynb+json", filename=f"exe_{dataset_style}.ipynb")
    return {"error": "Executed notebook not found"} 