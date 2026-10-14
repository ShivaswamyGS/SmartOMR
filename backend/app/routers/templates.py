import io
import cv2
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import OMRTemplate, User
from ..schemas import OMRTemplateResponse, OMRTemplateCreate
from ..security import get_current_user
from ..omr.templates import get_default_50q_template, get_default_20q_template, get_default_100q_template
from ..omr.sheet_generator import generate_blank_omr_sheet

router = APIRouter(prefix="/templates", tags=["OMR Templates"])

def ensure_built_in_templates(db: Session):
    """Seed standard templates if not present."""
    count = db.query(OMRTemplate).count()
    if count == 0:
        t50 = get_default_50q_template()
        t20 = get_default_20q_template()
        t100 = get_default_100q_template()
        
        db.add(OMRTemplate(
            name=t50["name"],
            description=t50["description"],
            total_questions=50,
            options_per_question=4,
            columns_count=2,
            questions_per_column=25,
            config_json=t50
        ))
        db.add(OMRTemplate(
            name=t20["name"],
            description=t20["description"],
            total_questions=20,
            options_per_question=4,
            columns_count=1,
            questions_per_column=20,
            config_json=t20
        ))
        db.add(OMRTemplate(
            name=t100["name"],
            description=t100["description"],
            total_questions=100,
            options_per_question=4,
            columns_count=4,
            questions_per_column=25,
            config_json=t100
        ))
        db.commit()

@router.get("", response_model=List[OMRTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    ensure_built_in_templates(db)
    return db.query(OMRTemplate).all()

@router.post("", response_model=OMRTemplateResponse)
def create_template(
    t_in: OMRTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = OMRTemplate(
        name=t_in.name,
        description=t_in.description,
        total_questions=t_in.total_questions,
        options_per_question=t_in.options_per_question,
        columns_count=t_in.columns_count,
        questions_per_column=t_in.questions_per_column,
        config_json=t_in.config_json
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/{template_id}/blank")
def download_blank_sheet(
    template_id: int,
    db: Session = Depends(get_db)
):
    template = db.query(OMRTemplate).filter(OMRTemplate.id == template_id).first()
    config = template.config_json if template else get_default_50q_template()
    title = f"{template.name if template else 'SmartOMR Standard'}"
    
    sheet_bgr = generate_blank_omr_sheet(config, exam_title=title)
    success, encoded_img = cv2.imencode(".png", sheet_bgr)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to render blank template image")
        
    return Response(
        content=encoded_img.tobytes(),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=blank_omr_{template_id}.png"}
    )
