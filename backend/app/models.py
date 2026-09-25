from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Scores(BaseModel):
    overall: int = Field(..., ge=0, le=100)
    general: int = Field(..., ge=0, le=100)
    ats: int = Field(..., ge=0, le=100)
    jdMatch: int = Field(..., ge=0, le=100)
    skillGap: int = Field(..., ge=0, le=100)


class DocumentItem(BaseModel):
    id: str
    text: str
    itemType: Literal["heading", "subheading", "bullet", "text"] = "bullet"


class DocumentSection(BaseModel):
    id: str
    title: str
    items: List[DocumentItem] = []


class ParsedDocument(BaseModel):
    candidateName: str = "Candidate"
    contactInfo: str = ""
    sections: List[DocumentSection] = []
    rawText: Optional[str] = None


class Annotation(BaseModel):
    id: str
    anchorId: str  # References a DocumentItem.id or DocumentSection.id
    flagType: Literal["amber", "red", "green"]
    symbol: Literal["⚠", "✗", "✓"]
    label: str
    fixText: str


class AnalysisResponse(BaseModel):
    scores: Scores
    document: ParsedDocument
    annotations: List[Annotation]
