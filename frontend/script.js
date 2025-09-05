const API='https://abo-reports-pro.onrender.com/';
const NETS=["Electricité (BT/HTA/HTB, éclairage)","Gaz","Hydrocarbures","Produits chimiques","Eau potable (AEP)","Assainissement/Pluvial","Chauffage/Climatisation","Télécommunications","Feux tricolores TBT","Non identifié","Vapeur/Eau chaude/Eau glacée","Transports guidés"];
const EQUIPS=["GPR US RADAR QUANTUM","Sensors & Software LMX100","Détecteur VIVAX vLoc3‑5000","SPX RD8100","Caméra RIDGID SeeSnake","VIVAX vLoc‑RTK‑Pro","Flexitrace","Pince à champ magnétique"];
const LOGICIELS=["AutoCAD/COVADIS","Land2Map","Autre"];
const TECHS=["Induction","Raccordement direct","Pince","Flexitrace","Prise domestique"];
const DOCS=["Plan géolocalisation 1/200","DWG/DXF","PDF Rapport","Carnet photos"];

function chipBar(id, items){
  const box=document.getElementById(id); box.innerHTML="";
  items.forEach(txt=>{
    const b=document.createElement('button'); b.type='button'; b.className='chip'; b.textContent=txt; b.dataset.active='0';
    b.onclick=()=>{ b.dataset.active=b.dataset.active==='1'?'0':'1'; b.classList.toggle('on'); saveDraft(); };
    box.appendChild(b);
  })
}
function addIntervenant(nom='', role=''){
  const wrap=document.getElementById('intervenants');
  const row=document.createElement('div'); row.className='grid';
  row.innerHTML=`<input placeholder="Nom prénom" value="${nom}"/><input placeholder="Rôle (ex: Technicien détection)" value="${role}"/>`;
  wrap.appendChild(row);
}

function saveDraft(){
  const f1=new FormData(document.getElementById('form-project'));
  const f2=new FormData(document.getElementById('form-report'));
  const draft={
    proj:Object.fromEntries(f1.entries()),
    nets:[...document.querySelectorAll('#chips-networks .chip.on')].map(b=>b.textContent),
    equips:[...document.querySelectorAll('#chips-equipements .chip.on')].map(b=>b.textContent),
    logiciels:[...document.querySelectorAll('#chips-logiciels .chip.on')].map(b=>b.textContent),
    techs:[...document.querySelectorAll('#chips-techniques .chip.on')].map(b=>b.textContent),
    docs:[...document.querySelectorAll('#chips-docs .chip.on')].map(b=>b.textContent),
    intervs:[...document.querySelectorAll('#intervenants .grid')].map(row=>({nom:row.children[0].value, role:row.children[1].value}))
  };
  localStorage.setItem('abo_draft', JSON.stringify(draft));
}
function loadDraft(){
  const raw=localStorage.getItem('abo_draft'); if(!raw) return;
  try{
    const d=JSON.parse(raw);
    if(d.proj){ for(const [k,v] of Object.entries(d.proj)){ const el=document.querySelector(`#form-project [name="${k}"]`); if(el) el.value=v; } }
    document.getElementById('intervenants').innerHTML=''; (d.intervs||[]).forEach(p=>addIntervenant(p.nom,p.role));
    ['chips-networks','chips-equipements','chips-logiciels','chips-techniques','chips-docs'].forEach(id=>{
      document.querySelectorAll('#'+id+' .chip').forEach(b=>{ b.classList.remove('on'); b.dataset.active='0'; });
    });
    (d.nets||[]).forEach(v=>{ [...document.querySelectorAll('#chips-networks .chip')].find(b=>b.textContent===v)?.classList.add('on'); });
    (d.equips||[]).forEach(v=>{ [...document.querySelectorAll('#chips-equipements .chip')].find(b=>b.textContent===v)?.classList.add('on'); });
    (d.logiciels||[]).forEach(v=>{ [...document.querySelectorAll('#chips-logiciels .chip')].find(b=>b.textContent===v)?.classList.add('on'); });
    (d.techs||[]).forEach(v=>{ [...document.querySelectorAll('#chips-techniques .chip')].find(b=>b.textContent===v)?.classList.add('on'); });
    (d.docs||[]).forEach(v=>{ [...document.querySelectorAll('#chips-docs .chip')].find(b=>b.textContent===v)?.classList.add('on'); });
  }catch(e){}
}
setInterval(saveDraft, 3000);

async function createProject(e){
  e.preventDefault();
  const fd=new FormData(e.target); const obj=Object.fromEntries(fd.entries());
  ['latitude','longitude'].forEach(k=>{ if(obj[k]==='') delete obj[k]; else obj[k]=parseFloat(obj[k]); });
  const r=await fetch(API+'/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
  const data=await r.json(); loadProjects(); alert('Chantier enregistré #'+data.id);
}
async function loadProjects(){
  const res=await fetch(API+'/projects'); const list=await res.json();
  const sel=document.getElementById('project-select'); sel.innerHTML='';
  list.forEach(p=>{ const o=document.createElement('option'); o.value=p.id; o.textContent=`#${p.id} — ${p.name}`; sel.appendChild(o); });
  document.getElementById('projects').textContent=list.map(p=>`#${p.id} ${p.name}`).join(' | ');
}
async function createReport(e){
  e.preventDefault();
  const fd=new FormData(e.target); const obj=Object.fromEntries(fd.entries()); obj.project_id=parseInt(obj.project_id);
  obj.networks=[...document.querySelectorAll('#chips-networks .chip.on')].map(b=>b.textContent);
  obj.equipements=[...document.querySelectorAll('#chips-equipements .chip.on')].map(b=>b.textContent);
  obj.logiciels=[...document.querySelectorAll('#chips-logiciels .chip.on')].map(b=>b.textContent);
  obj.techniques=[...document.querySelectorAll('#chips-techniques .chip.on')].map(b=>b.textContent);
  obj.documents_livres=[...document.querySelectorAll('#chips-docs .chip.on')].map(b=>b.textContent);
  obj.intervenants=[...document.querySelectorAll('#intervenants .grid')].map(row=>({nom:row.children[0].value, role:row.children[1].value}));
  const r=await fetch(API+'/reports',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
  const data=await r.json();
  alert('Rapport créé ID: '+data.id);
  document.getElementById('photo-report-id').value=data.id;
  document.getElementById('sign-report-id').value=data.id;
  document.getElementById('pdf-report-id').value=data.id;
}
async function uploadPhotos(){
  const rid=parseInt(document.getElementById('photo-report-id').value||'0'); if(!rid){alert('ID rapport manquant');return;}
  const files=document.getElementById('photo-files').files; if(!files.length){alert('Choisir des photos');return;}
  const fd=new FormData(); for(const f of files) fd.append('files', f);
  const r=await fetch(API+`/reports/${rid}/photos`,{method:'POST',body:fd}); const j=await r.json(); alert(`Photos envoyées: ${j.count}`);
}
const canvas=document.getElementById('sign-pad'); const ctx=canvas.getContext('2d'); let drawing=false;
function pos(e){ const r=canvas.getBoundingClientRect(); const t=(e.touches?e.touches[0]:e); return {x:t.clientX-r.left,y:t.clientY-r.top}; }
canvas.addEventListener('mousedown',e=>{ drawing=true; const p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y); });
canvas.addEventListener('mousemove',e=>{ if(!drawing) return; const p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke(); });
['mouseup','mouseleave','touchend','touchcancel'].forEach(ev=>canvas.addEventListener(ev,()=>drawing=false));
canvas.addEventListener('touchstart',e=>{ e.preventDefault(); drawing=true; const p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y); });
canvas.addEventListener('touchmove',e=>{ e.preventDefault(); if(!drawing) return; const p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke(); });
document.getElementById('btn-clear').onclick=()=>{ ctx.clearRect(0,0,canvas.width,canvas.height); };
document.getElementById('btn-save-sign').onclick=async()=>{
  const rid=parseInt(document.getElementById('sign-report-id').value||'0'); if(!rid){alert('ID rapport manquant');return;}
  const fd=new FormData(); fd.append('b64png', canvas.toDataURL('image/png'));
  const r=await fetch(API+`/reports/${rid}/signature`,{method:'POST',body:fd}); const j=await r.json(); alert('Signature OK');
};

document.getElementById('form-project').addEventListener('submit', createProject);
document.getElementById('form-report').addEventListener('submit', createReport);
document.getElementById('btn-upload-photos').addEventListener('click', uploadPhotos);
document.getElementById('btn-pdf').addEventListener('click', async()=>{
  const rid=parseInt(document.getElementById('pdf-report-id').value||'0'); if(!rid){alert('ID rapport manquant');return;}
  const r=await fetch(API+`/reports/${rid}/pdf`); if(!r.ok){alert('Erreur PDF'); return;}
  const blob=await r.blob(); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`rapport_${rid}.pdf`; a.click(); URL.revokeObjectURL(url);
});

chipBar('chips-networks', NETS);
chipBar('chips-equipements', EQUIPS);
chipBar('chips-logiciels', LOGICIELS);
chipBar('chips-techniques', TECHS);
chipBar('chips-docs', DOCS);
document.getElementById('btn-add-interv').onclick=()=>{ addIntervenant(); saveDraft(); };
setInterval(saveDraft, 3000);
loadDraft(); loadProjects();
