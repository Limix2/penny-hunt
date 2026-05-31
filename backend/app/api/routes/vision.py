from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import VisionResult
from app.services.vision.analyzer import analyze

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/analyze", response_model=VisionResult)
async def analyze_image(image: UploadFile = File(...), model: str = Form("local"),
                        db: Session = Depends(get_db)):
    return await analyze(await image.read(), model, db)
