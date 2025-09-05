from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ProjectCreate(BaseModel):
    name: str
    client_name: str
    dossier_ref: str = ""
    guichet_unique_ref: str = ""
    responsable_projet: str = ""
    demandeur: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    prestataire_detection: str = ""
    prestataire_georef: str = ""
    dates_detection: str = ""
    date_georef: str = ""
    date_rapport: str = ""

class ProjectOut(ProjectCreate):
    id: int
    class Config: orm_mode = True

class ReportCreate(BaseModel):
    project_id: int
    report_type: str = "Détection de réseaux"
    networks: List[str] = []
    intervenants: List[Dict[str, Any]] = []
    equipements: List[str] = []
    logiciels: List[str] = []
    mesure_mode: str = ""
    techniques: List[str] = []
    methode_detail: str = ""
    incertitude_max: str = ""
    profondeur_investigation: str = ""
    objet_etude: str = ""
    mode_operatoire: str = ""
    remarques: str = ""
    conclusion: str = ""
    documents_livres: List[str] = []

class ReportOut(ReportCreate):
    id: int
    signature_path: Optional[str] = None
    class Config: orm_mode = True
