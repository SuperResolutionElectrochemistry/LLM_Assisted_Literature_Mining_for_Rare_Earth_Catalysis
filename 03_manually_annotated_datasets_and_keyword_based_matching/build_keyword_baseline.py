# -*- coding: utf-8 -*-
"""Independent, pre-specified rule baseline for RE--descriptor associations.
Inputs: baseline_200_documents.csv and baseline_200_gold.csv, generated from user's locked manual workbook.
No GPT outputs, matched terms, human labels, or confidence values are accessed to generate predictions.
Standard-library only. Each prediction is (Reference Number, RE Element, Descriptor Code).
"""
import csv,re,collections,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ELEMENT_NAMES={
'Sc':['scandium','scandia'],'Y':['yttrium','yttria'],'La':['lanthanum','lanthana'],'Ce':['cerium','ceria','ceric','cerous'],'Pr':['praseodymium','praseodymia'],'Nd':['neodymium','neodymia'],'Pm':['promethium'],'Sm':['samarium','samaria'],'Eu':['europium','europia'],'Gd':['gadolinium','gadolinia'],'Tb':['terbium','terbia'],'Dy':['dysprosium','dysprosia'],'Ho':['holmium','holmia'],'Er':['erbium','erbia'],'Tm':['thulium','thulia'],'Yb':['ytterbium','ytterbia'],'Lu':['lutetium','lutetia']}
# Known full-name aliases and case-sensitive element symbols. Single-letter Y requires capital and word boundary.
# Formula symbols are allowed only followed by nonlowercase or a full name context.
ELEMENT_PATTERNS={e:[re.compile(r'(?<![A-Za-z])'+re.escape(e)+r'(?=$|[^a-z])'),*[re.compile(r'\b'+re.escape(n)+r'\b',re.I) for n in names]] for e,names in ELEMENT_NAMES.items()}
# Rules authored against descriptor definitions, not tailored to gold labels.
DESCRIPTORS={
'1.1':('Catalyst Stability','Ru Dissolution / Metal Leaching',r'\b(?:ruthenium|Ru|metal|catalyst|active\s+site|transition\s+metal)\b.{0,100}\b(?:dissolut\w*|leach\w*|metal\s+loss)\b|\b(?:dissolut\w*|leach\w*|metal\s+loss)\b.{0,85}\b(?:ruthenium|Ru|metal|catalyst)\b|\bmetal\s+dissolution\s+energ\w*\b'),
'1.2':('Catalyst Stability','Acid / Corrosion Stability',r'\b(?:acidic?\s+(?:condition\w*|medium|media|environment\w*|stabilit\w*|resistan\w*)|acid\s+(?:stabilit\w*|resistan\w*|corrosion)|corrosion\s+(?:resistan\w*|stabilit\w*|behavior|behaviour)|anti[ -]?corrosion|electrochemical\s+corrosion|acid[ -]?resistant|corrosive\s+environment\w*)\b'),
'1.3':('Catalyst Stability','Metal–O Bond Strength',r'\b(?:metal[–-]?(?:oxygen|O)|M[–-]O|Ru[–-]O|Ce[–-]O|La[–-]O|Pr[–-]O|Y[–-]O)\s+(?:bond\w*|interaction\w*)?.{0,45}\b(?:strength\w*|energi\w*|dissociation|stiffen\w*|stronger|weaken\w*|stabili\w*)\b|\b(?:strength\w*|energi\w*|dissociation|stiffen\w*|stronger|weaken\w*)\b.{0,50}\b(?:metal[–-]?(?:oxygen|O)|M[–-]O|Ru[–-]O|Ce[–-]O|La[–-]O)\s+bond\w*\b'),
'1.4':('Catalyst Stability','Lattice / Phase Stability',r'\b(?:lattice|phase|crystal(?:line)?|structure|structural|crystallographic)\s+(?:and\s+)?(?:stabilit\w*|stabili[sz]\w*|degrad\w*|reconstruct\w*|transform\w*|retention|preserv\w*)\b|\b(?:phase\s+transition|structural\s+integrity|structural\s+durability|lattice\s+distortion|structure\s+retention)\b'),
'1.5':('Catalyst Stability','Oxygen Vacancy Formation / Defect Stability',r'\b(?:oxygen|oxide|anion|O)\s+(?:ion\s+)?vacanc\w*\b|\b(?:vacanc\w*\s+(?:formation\s+energy|concentration|generation|stabili\w*)|defect\s+formation\s+energi\w*|defect\s+stabilit\w*)\b'),
'2.1':('Electronic Structure','Ru Oxidation State / High-Valence Ru',r'\b(?:Ru|ruthenium)\b.{0,80}\b(?:oxidation\s+state|valenc\w*|valence|high[ -]?valen\w*|high[ -]?oxidation|Ru\s*\(?[IVX0-9+]+\)?)\b|\b(?:oxidation\s+state|valenc\w*|valence|high[ -]?valen\w*)\b.{0,80}\b(?:Ru|ruthenium)\b'),
'2.2':('Electronic Structure','Charge Transfer / Electron Redistribution',r'\b(?:charge|electron\w*)\s+(?:transfer|redistribution|rearrangement|donation|migration|delocalization|delocalisation)\b|\b(?:electron\s+density\s+(?:redistribution|change\w*|shift\w*)|interfacial\s+charge|electronic\s+coupling)\b'),
'2.3':('Electronic Structure','Ru–O Covalency / RE–O Interaction',r'\bRu[–-]O\b.{0,40}\b(?:covalenc\w*|hybridiz\w*|interact\w*|bond\w*)\b|\b(?:covalenc\w*|hybridiz\w*|interact\w*)\b.{0,40}\bRu[–-]O\b|\b(?:rare[ -]?earth|lanthanide|lanthanoid|Ce|La|Pr|Nd|Y|Gd|Sm|Eu|Dy|Yb|Er|Tb|Ho|Lu|Tm|Sc|Pm)[– -]?(?:O|oxygen)\b.{0,45}\b(?:bond\w*|interaction\w*|hybridiz\w*|covalenc\w*)\b|\b(?:rare[ -]?earth[– -]?oxygen|RE[–-]O)\s+(?:bond\w*|interaction\w*)\b'),
'2.4':('Electronic Structure','Band Structure / Work Function / Conductivity',r'\b(?:band[ -]?gap|band\s+structure|density\s+of\s+states|electronic\s+(?:band|structure|conductiv\w*)|work\s+function|electrical\s+conductiv\w*|electronic\s+conductiv\w*|electron\s+conductiv\w*|electric\s+conductiv\w*|d[–-]?band\s+cent\w*)\b'),
'3.1':('Reaction Mechanism (CER)','Chloride Adsorption / Cl* Intermediate',r'\b(?:chloride|chlorine|Cl\*|Cl[-⁻])\b.{0,55}\b(?:adsorp\w*|intermediate\w*|binding|surface\s+species)\b|\b(?:adsorp\w*|intermediate\w*|binding)\b.{0,55}\b(?:chloride|chlorine|Cl\*)\b'),
'3.2':('Reaction Mechanism (CER)','Cl/OH Competitive Adsorption',r'\b(?:chloride|chlorine|Cl\*|Cl[-⁻])\b.{0,180}\b(?:hydroxyl|hydroxide|OH\*|OH[-⁻])\b|\b(?:hydroxyl|hydroxide|OH\*|OH[-⁻])\b.{0,180}\b(?:chloride|chlorine|Cl\*|Cl[-⁻])\b'),
'3.3':('Reaction Mechanism (CER)','CER Selectivity / OER Suppression',r'\b(?:chlorine\s+evolution|chloride\s+oxidation|chlorine\s+production|chlorine\s+selectiv\w*|CER\b)\b.{0,150}\b(?:selectiv\w*|oxygen\s+evolution|OER|suppress\w*|competition|competing)\b|\b(?:oxygen\s+evolution|OER)\b.{0,150}\b(?:chlorine\s+evolution|chlorine\s+selectiv\w*|CER\b)\b'),
'3.4':('Reaction Mechanism (CER)','Oxygen Intermediate Adsorption',r'\b(?:oxygen(?:ated)?|OH\*|OOH\*|O\*|hydroxyl|peroxide|peroxo)\b.{0,85}\b(?:intermediate\w*|adsorp\w*|binding\s+energy|adsorption\s+energy)\b|\b(?:adsorp\w*|binding\s+energy|intermediate\w*)\b.{0,85}\b(?:oxygen(?:ated)?|OH\*|OOH\*|O\*|hydroxyl|peroxide)\b'),
'3.5':('Reaction Mechanism (CER)','Lattice Oxygen Participation / LOM Suppression',r'\b(?:lattice\s+oxygen\s+(?:participat\w*|evolut\w*|mechanis\w*|oxidat\w*|activity|involv\w*|release)|lattice[ -]?oxygen[ -]?mediated|lattice\s+oxygen\s+redox|LOM\b)\b')}
# Reject weak clues; never use an unconstrained 'stability', 'selectivity', or 'oxygen' as a positive label.
EXCLUSION = {
'1.2': [r'\b(?:thermal\s+stability|sulfur\s+tolerance|anti[ -]?coking|coke\s+resistance|cycling\s+stability)\b'],
'3.2': [r'\b(?:COS|carbonyl\s+sulfide)\b'],
}
RE_SPLIT=re.compile(r'(?<=[.!?])\s+(?=[A-Z])|(?<=;)\s+')
def sentences(text):
 text=str(text or '').replace('\u00ad','').replace('\u2011','-')
 return [s.strip() for s in RE_SPLIT.split(text) if len(s.strip())>5]
def elements(text):
 return {e for e,patterns in ELEMENT_PATTERNS.items() if any(p.search(text) for p in patterns)}
compiled={k:re.compile(v[2],re.I) for k,v in DESCRIPTORS.items()}
def matched_codes(sentence):
 codes=[]
 for code,regex in compiled.items():
  if not regex.search(sentence):continue
  if code=='3.2':
   if not re.search(r'\b(?:compet\w*|co[ -]?adsorp\w*|adsorp\w*|site\s+competition|site\s+occupancy)\b',sentence,re.I):continue
  # Do not exclude if acid explicitly mentioned in same sentence; default D02 requires acid/corrosion phrase.
  codes.append(code)
 return codes

def predict(document):
 text=(document['Title']+' . '+document['Abstract']).strip()
 sent=sentences(text)
 seen=set(); results=[]
 for i,s in enumerate(sent):
  es=elements(s); codes=matched_codes(s)
  if not codes or not es:continue
  for e in sorted(es):
   for code in codes:
    key=(document['Reference Number'],e,code)
    if key in seen:continue
    seen.add(key)
    results.append({'Reference Number':document['Reference Number'],'RE Element':e,'Descriptor Code':code,'Dimension':DESCRIPTORS[code][0],'Descriptor':DESCRIPTORS[code][1],'Matched Sentence':s[:1200], 'Rule':'same-sentence RE and descriptor expression'})
 return results

def predict_docwide(document):
 """Document-level lexical co-occurrence, deliberately less restrictive than same-sentence rule."""
 text=(document['Title']+' . '+document['Abstract']).strip()
 es=elements(text)
 matched={code:next((s for s in sentences(text) if code in matched_codes(s)),None) for code in DESCRIPTORS}
 results=[]
 for e in sorted(es):
  for code,s in matched.items():
   if not s:continue
   results.append({'Reference Number':document['Reference Number'],'RE Element':e,'Descriptor Code':code,'Dimension':DESCRIPTORS[code][0],'Descriptor':DESCRIPTORS[code][1],'Matched Sentence':s[:1200],'Rule':'document-level RE and descriptor co-occurrence'})
 return results

def evaluate(pred,gold):
 a={(int(x['Reference Number']),x['RE Element'],x['Descriptor Code']) for x in pred};b={(int(x['Reference Number']),x['RE Element'],x['Descriptor Code']) for x in gold}
 tp=len(a&b);fp=len(a-b);fn=len(b-a)
 return dict(tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn) if tp+fn else 0,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
def read_csv(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,headers):
 with open(p,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,headers);w.writeheader();w.writerows(rows)
if __name__=='__main__':
 docs=read_csv(ROOT/'baseline_200_documents.csv');gold=read_csv(ROOT/'baseline_200_gold.csv')
 pred=[r for doc in docs for r in predict(doc)]
 write_csv(ROOT/'baseline_rule_predictions.csv',pred,['Reference Number','RE Element','Descriptor Code','Dimension','Descriptor','Matched Sentence','Rule'])
 wide=[r for doc in docs for r in predict_docwide(doc)]
 write_csv(ROOT/'baseline_docwide_predictions.csv',wide,['Reference Number','RE Element','Descriptor Code','Dimension','Descriptor','Matched Sentence','Rule'])
 print('documents',len(docs),'gold relations',len(gold),'sentence-rule',len(pred),evaluate(pred,gold),'docwide-rule',len(wide),evaluate(wide,gold))
