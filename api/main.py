"""HTTP API for generating and serving notebooks."""

import asyncio
import json
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from uuid import uuid4

import nbconvert
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIRECTORY = PROJECT_ROOT / "UploadedFiles"
OUTPUT_DIRECTORY = PROJECT_ROOT / "Output"
ALLOWED_DATASET_STYLES = frozenset({"A_1_one_csv", "B_2_joinable_csvs", "C_1_csv_time_series"})
ALLOWED_UPLOAD_SUFFIXES = frozenset({".csv", ".json", ".parquet", ".xlsx"})
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_ANSWERS_BYTES = 100 * 1024
PIPELINE_TIMEOUT_SECONDS = 600

app = FastAPI()


def validate_dataset_style(dataset_style: str) -> str:
    if dataset_style not in ALLOWED_DATASET_STYLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported dataset style.",
        )
    return dataset_style


def notebook_path(dataset_style: str, executed: bool) -> Path:
    prefix = "exe" if executed else "gen"
    return OUTPUT_DIRECTORY / f"{prefix}_{validate_dataset_style(dataset_style)}.ipynb"


async def save_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported upload type.",
        )

    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIRECTORY / f"{uuid4().hex}{suffix}"
    uploaded_bytes = 0

    try:
        with destination.open("xb") as output_file:
            while chunk := await upload.read(1024 * 1024):
                uploaded_bytes += len(chunk)
                if uploaded_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Upload exceeds the 50 MiB limit.",
                    )
                output_file.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return destination


def validate_answers(answers: str) -> str:
    encoded_answers = answers.encode("utf-8")
    if len(encoded_answers) > MAX_ANSWERS_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Answers exceed the 100 KiB limit.",
        )

    try:
        parsed_answers = json.loads(answers)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Answers must be valid JSON.",
        ) from error

    if not isinstance(parsed_answers, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Answers must be a JSON object.",
        )

    return json.dumps(parsed_answers, ensure_ascii=False)


def save_answers(dataset_style: str, answers: str) -> Path:
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIRECTORY / f"answers_{dataset_style}_{uuid4().hex}.json"
    destination.write_text(validate_answers(answers), encoding="utf-8")
    return destination


def require_single_upload(files: Iterable[UploadFile]) -> UploadFile:
    uploaded_files = list(files)
    if len(uploaded_files) != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Exactly one dataset file is required.",
        )
    return uploaded_files[0]


@app.post("/generate-notebook/")
async def generate_notebook(
    dataset_style: str = Form(...),
    files: list[UploadFile] = File(...),
    answers: str = Form(...),
) -> FileResponse:
    dataset_style = validate_dataset_style(dataset_style)
    upload = require_single_upload(files)
    file_path = await save_upload(upload)
    answers_path = save_answers(dataset_style, answers)

    try:
        await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "run.py", dataset_style, str(file_path), str(answers_path)],
            cwd=PROJECT_ROOT,
            check=True,
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Notebook generation timed out.",
        ) from error
    except subprocess.CalledProcessError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notebook generation failed.",
        ) from error

    generated_notebook = notebook_path(dataset_style, executed=False)
    if not generated_notebook.is_file():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notebook generation did not produce an output file.",
        )

    return FileResponse(
        generated_notebook,
        media_type="application/x-ipynb+json",
        filename=generated_notebook.name,
    )


@app.get("/download-executed-notebook/")
def download_executed_notebook(dataset_style: str = Query(...)) -> FileResponse:
    executed_notebook = notebook_path(dataset_style, executed=True)
    if not executed_notebook.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found.")
    return FileResponse(
        executed_notebook,
        media_type="application/x-ipynb+json",
        filename=executed_notebook.name,
    )


@app.get("/preview-notebook/")
def preview_notebook(
    dataset_style: str = Query(...),
    executed: bool = Query(False),
) -> HTMLResponse:
    source_notebook = notebook_path(dataset_style, executed)
    if not source_notebook.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found.")

    exporter = nbconvert.HTMLExporter()
    body, _ = exporter.from_filename(source_notebook)
    response = HTMLResponse(content=body)
    response.headers["Content-Security-Policy"] = (
        "sandbox; default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
