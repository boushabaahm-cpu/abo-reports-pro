from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os, json, datetime

def wrap(c, text, x, y, maxw=17*cm, leading=12, font=("Helvetica",9)):
    c.setFont(*font)
    words = str(text or "").split()
    line = ""
    while words:
        w0 = words.pop(0); test = (line + " " + w0).strip()
        if c.stringWidth(test, font[0], font[1]) > maxw:
            c.drawString(x, y, line); y -= leading; line = w0
        else:
            line = test
    if line: c.drawString(x, y, line); y -= leading
    return y

def title(c, txt, y, x=2*cm):
    if y < 3*cm: c.showPage(); y = A4[1]-2*cm
    c.setFont("Helvetica-Bold", 12); c.drawString(x, y, txt); y -= 10
    c.setStrokeColor(colors.lightgrey); c.line(x, y, x+17*cm, y); y -= 6
    return y

def kv(c, key, val, y, x=2*cm):
    c.setFont("Helvetica-Bold",9); c.drawString(x, y, key); 
    return wrap(c, val, x+4.3*cm, y)

def generate_pdf(out_path, project, report, photos, company):
    c = canvas.Canvas(out_path, pagesize=A4); W,H=A4; m=2*cm; y=H-m
    c.setFont("Helvetica-Bold",16); c.drawString(m,y,company.get("name","ABO Chantier Reports")); y-=18
    c.setFont("Helvetica",9); c.drawRightString(W-m,y,datetime.datetime.now().strftime("%d/%m/%Y %H:%M")); y-=18
    c.setFont("Helvetica-Bold",14); c.drawString(m,y,f"Rapport — {report.report_type}"); y-=20

    y=title(c,"Identification du projet",y)
    y=kv(c,"Dossier:", project.dossier_ref, y)
    y=kv(c,"Chantier:", project.name, y)
    y=kv(c,"Responsable:", project.responsable_projet, y)
    y=kv(c,"Réf. GU:", project.guichet_unique_ref, y)
    y=kv(c,"Adresse:", f"{project.address}, {project.postal_code} {project.city}", y)
    y=kv(c,"Demandeur:", project.demandeur, y)
    y=kv(c,"Prestataire détection:", project.prestataire_detection, y)
    y=kv(c,"Prestataire géoréférencement:", project.prestataire_georef, y)
    y=kv(c,"Dates interventions:", f"Détection: {project.dates_detection} | Géoréférencement: {project.date_georef}", y)
    y=kv(c,"Date de rédaction:", project.date_rapport, y)

    y=title(c,"Nature des réseaux",y)
    nets=json.loads(report.networks_json or "[]"); y=wrap(c, " • " + " | ".join(nets), 2*cm, y)

    y=title(c,"Ressources utilisées",y)
    inter=json.loads(report.intervenants_json or "[]")
    for i in inter: y=wrap(c, f"• {i.get('nom','')} — {i.get('role','')}", 2*cm, y)
    y=kv(c,"Matériels:", ", ".join(json.loads(report.equipements_json or "[]")), y)
    y=kv(c,"Logiciels:", ", ".join(json.loads(report.logiciels_json or "[]")), y)

    y=title(c,"Technologies & méthodes",y)
    y=kv(c,"Mode:", report.mesure_mode, y)
    y=kv(c,"Techniques:", ", ".join(json.loads(report.techniques_json or "[]")), y)
    y=kv(c,"Détails:", report.methode_detail, y)

    y=title(c,"Incertitudes / Profondeur",y)
    y=kv(c,"Incertitude max:", report.incertitude_max, y)
    y=kv(c,"Profondeur:", report.profondeur_investigation, y)

    for label, body in [("Objet de l’étude", report.objet_etude), ("Mode opératoire", report.mode_operatoire), ("Remarques / Anomalies", report.remarques), ("Conclusion", report.conclusion)]:
        y=title(c,label,y); y=wrap(c, body, 2*cm, y)

    y=title(c,"Documents livrés",y); y=wrap(c, " • " + " | ".join(json.loads(report.documents_livres_json or "[]")), 2*cm, y)

    if report.signature_path and os.path.exists(report.signature_path):
        y=title(c,"Signature",y)
        c.drawImage(ImageReader(report.signature_path), 2*cm, y-3.5*cm, width=4.5*cm, height=3.5*cm, preserveAspectRatio=True)
        y -= 3.5*cm + 10

    y=title(c,"Annexes — Photos",y)
    x=2*cm; imgw=6*cm; imgh=4.5*cm
    for ph in photos or []:
        if x+imgw>W-2*cm:
            x=2*cm; y-=imgh+28
            if y<4*cm: c.showPage(); y=H-2*cm
        if os.path.exists(ph.filename):
            try: c.drawImage(ImageReader(ph.filename), x, y-imgh, width=imgw, height=imgh, preserveAspectRatio=True)
            except: c.rect(x,y-imgh,imgw,imgh)
        c.setFont("Helvetica",8); c.drawString(x, y-imgh-10, getattr(ph,'caption','') or "")
        x+=imgw+0.7*cm
    c.showPage(); c.save()
