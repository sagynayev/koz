import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from tg_integration import send_report
from pipeline import run_pipeline

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <body style="font-family: sans-serif; max-width: 600px; margin: auto;">
            <h2>Meeting Agent</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label>Meeting type:</label><br>
                <select name="meeting_type">
                    <option value="team">Team</option>
                    <option value="standup">Standup</option>
                    <option value="sales">Sales</option>
                    <option value="planning">Planning</option>
                </select><br><br>

                <label>Audio file:</label><br>
                <input type="file" name="file"><br><br>

                <button type="submit">Upload & Process</button>
            </form>
        </body>
    </html>
    """


@app.post("/upload")
def upload(
    meeting_type: str = Form(...),
    file: UploadFile = File(...)
):
    os.makedirs("uploads", exist_ok=True)

    file_id = str(uuid.uuid4())
    input_path = f"uploads/{file_id}_{file.filename}"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pdf_path = run_pipeline(input_path, meeting_type)
    send_report(pdf_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="meeting_report.pdf"
    )
