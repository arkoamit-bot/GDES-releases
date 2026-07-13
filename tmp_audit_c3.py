import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'bgddr.settings'
import django
django.setup()
from knowledge.models import Disease, KnowledgeBaseEntry, ClinicalPathway, ClinicalCase
from collections import Counter

m = Disease.objects.get(id='c3')
print('id=%s name=%s' % (m.id, m.name))
TF = ['definition','epidemiology','etiology','pathophysiology','clinical_presentation','treatment_overview','monitoring_protocol','relapse_information','long_term_prognosis','evidence_summary','notes']
JSN = ['diagnostic_criteria','differential_diagnosis','lab_findings','biopsy_findings','classification_systems','risk_stratification','treatment_algorithms','complications','guideline_recommendations','key_references']
for f in TF:
    v = getattr(m,f)
    print('  %s: %s' % (f, 'EMPTY' if not v else '%d chars' % len(v)))
for f in JSN:
    v = getattr(m,f)
    fl = len(v) if isinstance(v,(list,dict)) else 0
    print('  %s: %d items' % (f, fl))
print()
rules = KnowledgeBaseEntry.objects.filter(disease_id='c3')
print('KB Rules: %d' % rules.count())
if rules.count():
    print('  types: %s' % dict(Counter(r.rule_type for r in rules)))
print('Pathways: %d' % ClinicalPathway.objects.filter(disease=m).count())
print('Cases: %d' % ClinicalCase.objects.filter(disease=m).count())
