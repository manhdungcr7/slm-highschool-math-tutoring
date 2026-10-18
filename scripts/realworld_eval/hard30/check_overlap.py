import csv,json,re,importlib.util
from pathlib import Path
P=Path(__file__).parent/'collect_hard_questions.py'
REPO=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('collect',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.collect()
def norm(s):
    s=re.sub(r'\\(?:left|right|,|;|!|quad|qquad|cdot|times|big|Big)', '', s)
    s=s.replace('dfrac','frac').replace('tfrac','frac').replace('\\bar','\\overline')
    return re.sub(r'[\s{}$.]', '', s)
old=[json.loads(l) for l in open(REPO/'data/router_train/kaggle_bundle/eval_set.jsonl',encoding='utf-8')]
train=[json.loads(l) for l in open(REPO/'data/router_train/kaggle_bundle/finetune_router.jsonl',encoding='utf-8')]
old += [dict(id='train:'+str(r['stt']),so_dang=re.search(r'\d+',r['completion']).group(),nguon='training',de_bai=r['prompt']) for r in train]
current=list(csv.DictReader(open(REPO/'data/results/pipeline_realworld/questions/cau_hoi_thuc_te_100_cau_da_ra_soat.csv',encoding='utf-8-sig')))
report=[]
for r in m.ROWS:
    stem=r['question_markdown_latex'].split('\nA.')[0]
    chunks=re.findall(r'\$(.*?)\$',stem)
    keys=[norm(c) for c in chunks if len(norm(c))>=5]
    same=[]
    for o in old:
        if str(o['so_dang'])==r['dang_dung'] and all(key in norm(o['de_bai'].split('\nA.')[0]) for key in keys):
            if r['params']['group']=='nested_count' and not re.search(r'không quá\s*'+str(r['params']['K'])+r'\s',o['de_bai']): continue
            same.append((o['id'],o['nguon'],o['de_bai'][:300]))
    samecurrent=[o['id'] for o in current if all(key in norm(o['question_markdown_latex'].split('\nA.')[0]) for key in keys)]
    print(r['id'],r['dang_dung'],'CURRENT',samecurrent,'OLD',same[:3])
    report.append(dict(id=r['id'],dang_dung=r['dang_dung'],matches_current=samecurrent,matches_previous=same))
(m.OUT/'overlap_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
