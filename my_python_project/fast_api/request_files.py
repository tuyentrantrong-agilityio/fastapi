# File Upload - Receive files from client
#
# File upload = multipart/form-data (not JSON)
# Need pip install python-multipart to use


from fastapi import FastAPI, File, UploadFile, Form
from typing import Annotated
import os

app = FastAPI()


# TWO WAYS TO RECEIVE FILES
# =========================

# Method 1: bytes (read entire file into RAM)
# ===========================================
# Use when: small files, testing, learning
# WARNING: Do NOT use for large files!


@app.post("/upload-bytes/")
async def upload_bytes(file: Annotated[bytes, File()]):
    # FastAPI reads entire file → RAM → returns bytes
    # {"size": 1024} = file is 1024 bytes
    return {"size": len(file)}


# Method 2: UploadFile (RECOMMENDED)
# ==================================
# Use when: images, videos, PDFs, real files
# Smartly handles: small files → RAM, large files → disk


@app.post("/upload/")
async def upload_file(file: UploadFile):
    # Receive UploadFile object
    # FastAPI handles memory intelligently
    return {"filename": file.filename, "content_type": file.content_type}


# UploadFile - Important methods
# ==============================


@app.post("/upload-info/")
async def upload_with_info(file: UploadFile):
    # file.filename = file name ("photo.jpg")
    # file.content_type = MIME type ("image/jpeg")
    # file.file = file object (to read)

    # Read file contents
    contents = await file.read()

    # If need to read again, use seek(0) to reset pointer
    await file.seek(0)
    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }


# FILE CAN BE OPTIONAL
# ====================


@app.post("/upload-optional/")
async def upload_optional(file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded"}
    return {"filename": file.filename}


# UPLOAD MULTIPLE FILES
# =====================


@app.post("/upload-multiple/")
async def upload_multiple(files: list[UploadFile]):
    # Client sends: files=a.jpg, files=b.png, files=c.pdf
    # FastAPI groups into list
    results = []
    for file in files:
        results.append({"filename": file.filename, "content_type": file.content_type})
    return results


# WRONG: Cannot mix JSON + File
# ==============================
from pydantic import BaseModel


class UserData(BaseModel):
    name: str
    email: str


# DO NOT DO THIS:
# @app.post("/upload-mixed/")
# async def upload_mixed(user: UserData, file: UploadFile):
#     # Because:
#     # - user: JSON → application/json
#     # - file: multipart/form-data
#     # HTTP does NOT allow mixing 2 content-types!


# CORRECT: Use Form() for additional data
# ========================================


@app.post("/upload-with-data/")
async def upload_with_data(
    name: Annotated[str, Form()], email: Annotated[str, Form()], file: UploadFile
):
    # Everything is form-data
    # name, email: Form() - text data
    # file: UploadFile - file data
    return {"name": name, "email": email, "filename": file.filename}


# SAVE FILE TO DISK
# =================


@app.post("/save-file/")
async def save_file(file: UploadFile):
    # Save file to uploads directory
    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    # Read file and save
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    return {"filename": file.filename, "saved_path": file_path, "size": len(contents)}


# IMPORTANT NOTES
# ===============
# 1. File upload = multipart/form-data (not JSON)
# 2. Use UploadFile instead of bytes (smarter)
# 3. Cannot mix JSON body + File (use Form() instead)
# 4. Need pip install python-multipart to use File/Form
# 5. UploadFile methods: .read(), .seek(), .close()
