from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    client_name = Column(String, index=True)
    dossier_ref = Column(String, default="")
    guichet_unique_ref = Column(String, default="")
    responsable_projet = Column(String, default="")
    demandeur = Column(String, default="")
    address = Column(String, default="")
    city = Column(String, default="")
    postal_code = Column(String, default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    prestataire_detection = Column(String, default="")
    prestataire_georef = Column(String, default="")
    dates_detection = Column(String, default="")
    date_georef = Column(String, default="")
    date_rapport = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    report_type = Column(String, default="Détection de réseaux")
    networks_json = Column(Text, default="[]")
    intervenants_json = Column(Text, default="[]")
    equipements_json = Column(Text, default="[]")
    logiciels_json = Column(Text, default="[]")
    mesure_mode = Column(String, default="")
    techniques_json = Column(Text, default="[]")
    methode_detail = Column(Text, default="")
    incertitude_max = Column(String, default="")
    profondeur_investigation = Column(String, default="")
    objet_etude = Column(Text, default="")
    mode_operatoire = Column(Text, default="")
    remarques = Column(Text, default="")
    conclusion = Column(Text, default="")
    documents_livres_json = Column(Text, default="[]")
    signature_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="reports")
