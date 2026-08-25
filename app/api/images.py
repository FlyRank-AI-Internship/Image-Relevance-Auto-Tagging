from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.jobs.image_processing import (
    process_batch,
    process_image_with_retry,
)

from app.jobs.image_processing import (
    process_image_with_retry,
)
from app.services.vision_service import VisionProcessingError


router = APIRouter(
    prefix="/images",
    tags=["images"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image type. "
                "Use JPEG, PNG or WEBP."
            ),
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]

    filename = f"{uuid4()}{extension}"
    path = UPLOAD_DIR / filename

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        path.write_bytes(contents)

        result = process_image_with_retry(path)

        return {
            "filename": filename,
            **result.model_dump(),
        }

    except VisionProcessingError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    

@router.post("/process-batch")
def process_uploaded_images():
    image_paths = [
        path
        for path in UPLOAD_DIR.iterdir()
        if path.suffix.lower()
        in {".jpg", ".jpeg", ".png", ".webp"}
    ]

    if not image_paths:
        raise HTTPException(
            status_code=404,
            detail="No uploaded images found.",
        )

    return process_batch(image_paths)