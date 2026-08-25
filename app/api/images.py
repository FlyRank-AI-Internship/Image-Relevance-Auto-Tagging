from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.jobs.image_processing import (
    process_batch,
    process_image_with_retry,
)
from app.models.image import ImageRecord
from app.services.embedding_service import EmbeddingService
from app.services.vision_service import VisionProcessingError

from fastapi import BackgroundTasks

from app.jobs.image_processing import (
    process_image_with_retry,
    run_batch_job,
)
from app.jobs.job_store import create_job


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
    db: Session = Depends(get_db),
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

        # Step 1: Analyze image using Gemini Vision
        result = process_image_with_retry(path)

        # Step 2: Generate embedding from image metadata
        embedding_service = EmbeddingService()

        embedding_text = (
            f"{result.metadata.subject}. "
            f"{result.metadata.caption}. "
            f"{' '.join(result.metadata.attributes)}"
        )

        embedding = embedding_service.embed_text(
            embedding_text,
            entity_type="image",
            entity_id=filename,
        )

        # Step 3: Store image metadata + embedding
        record = ImageRecord(
            filename=filename,
            subject=result.metadata.subject,
            category=result.metadata.category,
            attributes=result.metadata.attributes,
            caption=result.metadata.caption,
            confidence=result.metadata.confidence,
            needs_review=result.needs_review,
            embedding=embedding,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "image_id": record.id,
            "filename": filename,
            **result.model_dump(),
        }

    except VisionProcessingError as exc:
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {exc}",
        ) from exc


@router.post(
    "/process-batch",
    status_code=202,
)
def process_uploaded_images(
    background_tasks: BackgroundTasks,
):
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

    job_id = create_job()

    background_tasks.add_task(
        run_batch_job,
        job_id,
        image_paths,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "images": len(image_paths),
    }