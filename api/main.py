from fastapi import FastAPI, Form, Query, UploadFile, File, Body
from typing import List, Dict, Any
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware
import nbconvert
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_PATH = "Output/generated_notebook.ipynb"

@app.post("/generate-notebook/")
async def generate_notebook(dataset_style: str = Form(...), files: List[UploadFile] = File(...)):
    # Sauvegarder les fichiers uploadés
    upload_dir = "UploadedFiles"
    os.makedirs(upload_dir, exist_ok=True)
    file_paths = []
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_paths.append(file_path)
    subprocess.run(["python", "run.py", dataset_style, *file_paths], check=True)
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

@app.get("/preview-notebook/")
def preview_notebook(dataset_style: str = Query(...), executed: bool = Query(False)):
    if executed:
        nb_path = f"Output/exe_{dataset_style}.ipynb"
    else:
        nb_path = f"Output/gen_{dataset_style}.ipynb"
    if os.path.exists(nb_path):
        exporter = nbconvert.HTMLExporter()
        body, _ = exporter.from_filename(nb_path)
        # Inject improved dark mode CSS
        dark_css = '''<style>
          body { background: #0c0b0e !important; color: #ffffff !important; }
          .jp-Notebook, .jp-Cell, .jp-InputArea, .jp-OutputArea { background: #0c0b0e !important; color: #ffffff !important; }
          pre, code { background: #1c1b1f !important; color: #ffffff !important; }
          h1, h2, h3, h4, h5, h6, p, li { color: #ffffff !important; }
          a { color: #a277ff !important; }
          .output_area, .output_subarea { background: #1c1b1f !important; color: #ffffff !important; }
          .cm-s-ipython span { color: #c9cbff !important; }
        </style>'''
        body = body.replace("</head>", f"{dark_css}</head>")
        return HTMLResponse(content=body)
    return {"error": "Notebook not found"} 

@app.post("/submit-answers/")
async def submit_answers(
    dataset_style: str = Form(...),
    files: List[UploadFile] = File(...),
    answers: str = Form(...)
):
    """
    Reçoit un JSON answers (sous forme de string), sauvegarde, puis lance le pipeline avec ce JSON.
    """
    upload_dir = "UploadedFiles"
    os.makedirs(upload_dir, exist_ok=True)
    file_paths = []
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_paths.append(file_path)
    # Sauvegarder le JSON answers
    answers_path = os.path.join(upload_dir, f"answers_{dataset_style}.json")
    with open(answers_path, "w") as f:
        f.write(answers)
    # Lancer le pipeline avec le JSON answers
    subprocess.run([
        "python", "run.py", dataset_style, *file_paths, answers_path
    ], check=True)
    gen_path = f"Output/gen_{dataset_style}.ipynb"
    if os.path.exists(gen_path):
        return FileResponse(gen_path, media_type="application/x-ipynb+json", filename=f"gen_{dataset_style}.ipynb")
    return {"error": "Notebook not found"}

