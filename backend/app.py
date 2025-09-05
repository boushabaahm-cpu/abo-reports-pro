from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import os, base64, json

from .database import Base, engine, SessionLocal
from . import models, schemas
from .utils import generate_pdf

Base.metadata.create_all(bind=engine)
with engine.connect() as con:
    con.execute(text("""CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER,
        filename TEXT,
        caption TEXT,
        timestamp TEXT
    )"""))
    con.commit()

app = FastAPI(title="ABO Mini‑SaaS Reports PRO")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
PHOTOS_DIR = os.path.join(STORAGE_DIR, "photos")
SINGS_DIR = os.path.join(STORAGE_DIR, "signatures")
PDFS_DIR = os.path.join(STORAGE_DIR, "pdfs")
for d in [STORAGE_DIR, PHOTOS_DIR, SINGS_DIR, PDFS_DIR]: os.makedirs(d, exist_ok=True)
app.mount("/static", StaticFiles(directory=STORAGE_DIR), name="static")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/projects", response_model=schemas.ProjectOut)
def create_project(p: schemas.ProjectCreate, db: Session = Depends(get_db)):
    obj = models.Project(**p.dict()); db.add(obj); db.commit(); db.refresh(obj); return obj

@app.get("/projects", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.id.desc()).all()

@app.post("/reports", response_model=schemas.ReportOut)
def create_report(r: schemas.ReportCreate, db: Session = Depends(get_db)):
    if not db.query(models.Project).get(r.project_id): raise HTTPException(404, "Project not found")
    obj = models.Report(
        project_id=r.project_id, report_type=r.report_type,
        networks_json=json.dumps(r.networks, ensure_ascii=False),
        intervenants_json=json.dumps(r.intervenants, ensure_ascii=False),
        equipements_json=json.dumps(r.equipements, ensure_ascii=False),
        logiciels_json=json.dumps(r.logiciels, ensure_ascii=False),
        mesure_mode=r.mesure_mode, techniques_json=json.dumps(r.techniques, ensure_ascii=False),
        methode_detail=r.methode_detail, incertitude_max=r.incertitude_max, profondeur_investigation=r.profondeur_investigation,
        objet_etude=r.objet_etude, mode_operatoire=r.mode_operatoire, remarques=r.remarques, conclusion=r.conclusion,
        documents_livres_json=json.dumps(r.documents_livres, ensure_ascii=False),
    )
    db.add(obj); db.commit(); db.refresh(obj); return obj

@app.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    arr=[]; 
    for rep in db.query(models.Report).order_by(models.Report.id.desc()).all():
        arr.append({
            "id":rep.id,"project_id":rep.project_id,"report_type":rep.report_type,
            "networks":json.loads(rep.networks_json or "[]"),
            "intervenants":json.loads(rep.intervenants_json or "[]"),
            "equipements":json.loads(rep.equipements_json or "[]"),
            "logiciels":json.loads(rep.logiciels_json or "[]"),
            "mesure_mode":rep.mesure_mode,"techniques":json.loads(rep.techniques_json or "[]"),
            "methode_detail":rep.methode_detail,"incertitude_max":rep.incertitude_max,"profondeur_investigation":rep.profondeur_investigation,
            "objet_etude":rep.objet_etude,"mode_operatoire":rep.mode_operatoire,"remarques":rep.remarques,"conclusion":rep.conclusion,
            "documents_livres":json.loads(rep.documents_livres_json or "[]"),"signature_path":rep.signature_path
        })
    return arr

@app.post("/reports/{rid}/photos")
async def upload_photos(rid: int, files: List[UploadFile] = File(...), captions: Optional[str] = Form(None), db: Session = Depends(get_db)):
    cap_list = []
    if captions:
        try: cap_list = json.loads(captions)
        except: cap_list = [c.strip() for c in captions.split(",")]
    out=[]
    ext_i=0
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        fname=f"r{rid}_{ext_i}{ext}"; ext_i+=1
        path=os.path.join(PHOTOS_DIR, fname)
        with open(path,"wb") as fp: fp.write(await f.read())
        db.execute(text("INSERT INTO photos (report_id, filename, caption, timestamp) VALUES (:rid,:fn,:cap, datetime('now'))"),
                   {"rid":rid,"fn":path,"cap":cap_list[out.__len__()] if out.__len__()<len(cap_list) else ""})
        db.commit()
        out.append({"filename":path})
    return {"count":len(out)}

@app.post("/reports/{rid}/signature")
async def upload_signature(rid: int, file: UploadFile = File(None), b64png: str = Form(None), db: Session = Depends(get_db)):
    out_path=os.path.join(SINGS_DIR, f"sign_r{rid}.png")
    if file:
        with open(out_path,"wb") as fp: fp.write(await file.read())
    elif b64png:
        if "," in b64png: b64png = b64png.split(",")[1]
        import base64; data=base64.b64decode(b64png); 
        with open(out_path,"wb") as fp: fp.write(data)
    else: raise HTTPException(400,"No signature provided")
    db.execute(text("UPDATE reports SET signature_path=:p WHERE id=:rid"),{"p":out_path,"rid":rid}); db.commit()
    return {"ok":True}

@app.get("/reports/{rid}/pdf")
def export_pdf(rid: int, db: Session = Depends(get_db)):
    rep = db.query(models.Report).get(rid)
    if not rep: raise HTTPException(404,"Report not found")
    proj = db.query(models.Project).get(rep.project_id)
    rows = db.execute(text("SELECT filename, caption FROM photos WHERE report_id=:rid"),{"rid":rid}).fetchall()
    class P: pass
    photos=[]; 
    for r in rows:
        p=P(); p.filename, p.caption = r[0], r[1]; photos.append(p)
    out_path=os.path.join(PDFS_DIR, f"report_{rid}.pdf")
    generate_pdf(out_path, proj, rep, photos, {"name":"ABO Chantier Reports","email":"contact@example.com"})
    if not os.path.exists(out_path): raise HTTPException(500,"PDF not generated")
    return FileResponse(out_path, media_type="application/pdf", filename=os.path.basename(out_path))
