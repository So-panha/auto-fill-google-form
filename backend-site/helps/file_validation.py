import os
from fastapi import UploadFile, HTTPException, status

class FileValidator:

    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

    ALLOWED_MIME_TYPES = {
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    @staticmethod
    def validate_excel(file: UploadFile):

        # 1. check file exists
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is missing"
            )

        # 2. check extension
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only Excel files allowed (.xlsx, .xls). Got '{ext}'"
            )

        # 3. check MIME type
        if file.content_type not in FileValidator.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type '{file.content_type}'. Only Excel files allowed."
            )

        return True