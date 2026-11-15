import json,sys
from pathlib import Path
res=json.loads(Path(sys.argv[1]).read_text())
if res.get('ok') is not True: raise SystemExit('Coleta não confirmada')
d=res.get('dados')
if not isinstance(d,dict) or not isinstance(d.get('rows'),list) or type(res.get('linhas')) is not int or len(d['rows'])!=res['linhas']:
    raise SystemExit('Métricas ausentes ou contagem truncada')
p=Path(sys.argv[2]); q=p.with_suffix('.novo'); q.write_text(json.dumps(d,ensure_ascii=False)+'\n'); q.replace(p)
