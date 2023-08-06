from sys import argv, exit
from pathlib import Path
import numpy as np
import pandas as pd
import json
from tqdm import tqdm

EXAMPLE_FILE = './consumption-well-being.json'

def processJSON(file: str = None):
    if not file:
        exit(1)
    jdata = json.load(open(file))
    njd = pd.json_normalize(jdata, sep='.').to_dict(orient='records')
    
    rows = []
    for i, p in tqdm(enumerate(njd), total=len(njd), desc="Flattening PDF data."):
        pt = p["text"]
        for r in pt:
            r["page"] = i
            for k in ["number", "pages", "height", "width"]:
                r[k] = p[k]
                rows += [r]
                
    df = pd.DataFrame.from_records(rows)

    pnum = df.page.unique().tolist()
    tops = df.top.unique().tolist()

    prows = []
    for p in tqdm(pnum, desc="Merging PDF data: processing pages..", total=len(pnum)):
        for t in tqdm(tops, total=len(tops), desc="Merging page data.."):
            dfph = df[(df.top == t) & (df.page == p)]
            lefts = sorted(dfph.left.unique().tolist())
            r = []        
            for lf in lefts:
                r += [dfph.loc[dfph.left == lf, 'data'].values.reshape(-1,1)]
            if not r:
                continue
            mr = np.concatenate(r,axis=1)
            prows += mr.tolist()
            
    minlen = lambda rows: min([len(i) for i in rows])
    mindiff = lambda rows: max([abs(len(i) - minL) for i in rows])

    minL = minlen(prows)
    bar = tqdm(desc="Merging page data: merging longer rows..", total=mindiff(prows))
    while mindiff(prows) > 0:
        bar.display()
        bar.update(1)
        minL = minlen(prows)
        for i, r in enumerate(prows):
            if len(r) > minL:
                r = [" ".join(r[:2]), *r[2:]]
                prows[i] = r

    fdf = pd.DataFrame.from_records(prows)
    fdf.to_csv(Path(file).with_suffix('.res.csv'), index=False)

