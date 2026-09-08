"""Download, audit, split and fit RT-IoT2022 without test-set model selection."""
from pathlib import Path
import copy, hashlib, json, platform, sys, urllib.request, zipfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/public'
OUT = ROOT / 'data/prepared'
PUBLIC = ROOT / 'assets/research'
URL = 'https://archive.ics.uci.edu/static/public/942/rt-iot2022.zip'
ZIP_SHA = 'bcaa24d62abbb1215be576d5cf9c02dfcb0bb7c4c2f5a00e03055afaa1ed109e'
FEATURES = ['flow_duration','fwd_pkts_tot','bwd_pkts_tot','flow_pkts_per_sec',
            'down_up_ratio','flow_SYN_flag_count','flow_RST_flag_count','flow_ACK_flag_count',
            'flow_pkts_payload.avg','flow_pkts_payload.std','fwd_init_window_size','bwd_init_window_size']
BENIGN = ['MQTT_Publish', 'Thing_Speak', 'Wipro_bulb']
NOVEL = ['ARP_poisioning', 'DDOS_Slowloris', 'NMAP_XMAS_TREE_SCAN']
SEEDS = [11, 23, 37, 53, 71]

def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, allow_nan=False, separators=(',', ':')), encoding='utf-8')

def load_data():
    RAW.mkdir(parents=True, exist_ok=True)
    archive = RAW / 'rt-iot2022.zip'
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == ZIP_SHA, 'Dataset checksum mismatch'
    with zipfile.ZipFile(archive) as z:
        content = z.read('RT_IOT2022')
    csv = RAW / 'RT_IOT2022.csv'
    csv.write_bytes(content)
    df = pd.read_csv(csv)
    df['source_row'] = np.arange(len(df))
    assert set(BENIGN) <= set(df.Attack_type.unique()), df.Attack_type.unique()
    df['label'] = (~df.Attack_type.isin(BENIGN)).astype(int)  # 1 = ATTACK in this new backend
    valid = np.isfinite(df[FEATURES]).all(axis=1) & (df[FEATURES] >= 0).all(axis=1)
    clean = df.loc[valid].copy()
    # Group by EXACT deployed input vector, including across differing source protocols.
    clean['feature_hash'] = pd.util.hash_pandas_object(clean[FEATURES], index=False).astype(str)
    conflicting = clean.groupby('feature_hash').label.nunique()
    conflicts = set(conflicting[conflicting > 1].index)
    clean = clean[~clean.feature_hash.isin(conflicts)]
    clean = clean.drop_duplicates('feature_hash').reset_index(drop=True)
    manifest = {
        'dataset':'RT-IoT2022', 'doi':'10.24432/C5P338', 'license':'CC BY 4.0',
        'source_url':URL, 'source_page':'https://archive.ics.uci.edu/dataset/942/rt-iot2022',
        'creators':'B. S. Sharmila and Rohini Nagapadma', 'archive_sha256':ZIP_SHA,
        'csv_sha256':hashlib.sha256(content).hexdigest(), 'raw_rows':len(df),
        'invalid_rows':int((~valid).sum()), 'conflicting_feature_groups':len(conflicts),
        'removed_conflicting_rows':int(df.loc[valid].assign(h=pd.util.hash_pandas_object(df.loc[valid, FEATURES],index=False).astype(str)).h.isin(conflicts).sum()),
        'unique_rows':len(clean), 'raw_class_counts':df.Attack_type.value_counts().to_dict(),
        'unique_class_counts':clean.Attack_type.value_counts().to_dict(), 'features':FEATURES,
        'label_convention':{'0':'benign','1':'attack'}, 'benign_classes':BENIGN,
        'held_out_attack_families':NOVEL, 'seeds':SEEDS,
        'scope':'Captured IoT testbed traffic with generated attacks; not enterprise access-decision ground truth.',
        'ordering':'No capture timestamps in the released CSV. Evaluation uses explicitly constructed replay order; no claim of natural chronological concept drift.',
        'environment':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'platform':platform.platform()},
        'prepared_at_utc':datetime.now(timezone.utc).isoformat()
    }
    return clean, manifest

def rows(df):
    return [{'id':int(r.source_row),'x':[float(v) for v in r[FEATURES]],'y':int(r.label),'family':r.Attack_type} for _,r in df.iterrows()]

def prepare():
    df, manifest = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    known = df[~df.Attack_type.isin(NOVEL)]
    novel = df[df.Attack_type.isin(NOVEL)]
    manifest['protocol'] = {
        'split':'Known families: stratified 60% train, 20% validation, 20% test. Novel families: exclusively test.',
        'selection':'Model selected by known-family validation log loss; no test data used in training, scaling, canonical anchors or threshold choice.',
        'threshold':0.5, 'feedback':'Test-then-train, labels revealed only after each 32-record batch; this is a simulated oracle-label assumption.',
        'stationary':'Known-family test records shuffled once.',
        'shifted':'Four replay phases: known / novel / known / novel attack families. Held-out benign rows distributed across all phases; each record used once.',
        'unit':'One measured bidirectional flow; this backend is not a temporal LSTM.',
        'duplicates':'Exact deployed-feature vectors deduplicated BEFORE splitting; binary-label conflicts excluded.'
    }
    for seed in SEEDS:
        print('Preparing seed',seed,flush=True)
        tr, rest = train_test_split(known,test_size=.4,stratify=known.Attack_type,random_state=seed)
        va, te = train_test_split(rest,test_size=.5,stratify=rest.Attack_type,random_state=seed)
        assert not set(tr.feature_hash)&set(rest.feature_hash)
        assert not set(va.feature_hash)&set(te.feature_hash)
        train=np.log1p(tr[FEATURES].to_numpy(float)); mean=train.mean(0); scale=train.std(0); scale[scale<1e-9]=1
        transform=lambda frame:np.clip((np.log1p(frame[FEATURES].to_numpy(float))-mean)/scale,-8,8)
        xt=transform(tr); xv=transform(va); yt=tr.label.to_numpy(); yv=va.label.to_numpy()
        mlp=MLPClassifier(hidden_layer_sizes=(24,),activation='tanh',solver='adam',alpha=.001,
                          learning_rate_init=.001,batch_size=128,max_iter=1,random_state=seed)
        best=None; bestloss=float('inf'); curve=[]; stale=0
        # Deterministic class-balanced resampling is training-only; validation keeps actual prevalence.
        rng=np.random.default_rng(seed); idx0=np.where(yt==0)[0]; idx1=np.where(yt==1)[0]
        for epoch in range(45):
            size=max(len(idx0),len(idx1)); ix=np.concatenate([rng.choice(idx0,size),rng.choice(idx1,size)]);rng.shuffle(ix)
            mlp.partial_fit(xt[ix],yt[ix],classes=[0,1])
            loss=log_loss(yv,mlp.predict_proba(xv),labels=[0,1]); curve.append(float(loss))
            if loss<bestloss-1e-5: best=copy.deepcopy(mlp);bestloss=loss;stale=0
            else: stale+=1
            if stale>=7: break
        logistic=LogisticRegression(C=1,max_iter=1000,class_weight='balanced',random_state=seed).fit(xt,yt)
        forest=RandomForestClassifier(n_estimators=200,max_depth=16,min_samples_leaf=2,class_weight='balanced',random_state=seed,n_jobs=2).fit(xt,yt)
        anchors=pd.concat([va[va.label==y].sample(n=min(48,sum(va.label==y)),random_state=seed) for y in [0,1]])
        anchor_rows=rows(anchors)
        replay=pd.concat([tr[tr.label==y].sample(n=min(64,sum(tr.label==y)),random_state=seed) for y in [0,1]])
        bundle={'version':'rtiot-mlp-v1','seed':seed,'features':FEATURES,'mean':mean.tolist(),'scale':scale.tolist(),
                'model':{'w1':best.coefs_[0].tolist(),'b1':best.intercepts_[0].tolist(),'w2':best.coefs_[1][:,0].tolist(),'b2':float(best.intercepts_[1][0])},
                'anchors':anchor_rows,'replay':rows(replay),'validation_loss':bestloss,'validation_curve':curve,
                'bounds':[{'min':float(tr[f].min()),'max':float(tr[f].max()),'p01':float(tr[f].quantile(.01)),'p99':float(tr[f].quantile(.99))} for f in FEATURES],
                'provenance':{'dataset':manifest['dataset'],'archive_sha256':ZIP_SHA,'license':'CC BY 4.0'},
                'config':{'batch_size':32,'error_short':64,'error_long':256,'error_margin':.08,'attribution_threshold':.15,
                          'min_update_gap':128,'adaptation_window':128,'replay_size':128,'update_epochs':3,'update_lr':.003,
                          'eci_threshold':.5,'max_anchor_loss_increase':.05,'max_attack_miss_increase':.05}}
        bundle['model_sha256']=hashlib.sha256(json.dumps(bundle['model'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        stationary=te.sample(frac=1,random_state=seed)
        benign=te[te.label==0].sample(frac=1,random_state=seed)
        ka=te[te.label==1].sample(frac=1,random_state=seed)
        na=novel.sample(frac=1,random_state=seed)
        phases=[]; boundaries=[]; total=0
        for phase in range(4):
            b=benign.iloc[len(benign)*phase//4:len(benign)*(phase+1)//4]
            attacks=(ka if phase%2==0 else na)
            half=phase//2; attacks=attacks.iloc[len(attacks)*half//2:len(attacks)*(half+1)//2]
            part=pd.concat([b,attacks]).sample(frac=1,random_state=seed+phase)
            if phase:boundaries.append(total)
            total+=len(part); phases.append(part)
        shifted=pd.concat(phases)
        split={'seed':seed,'train':len(tr),'validation':len(va),'stationary_test':len(te),'shifted_test':len(shifted),
               'split_hashes':{name:hashlib.sha256(','.join(map(str,frame.source_row)).encode()).hexdigest() for name,frame in [('train',tr),('validation',va),('test',shifted)]}}
        save(OUT/f'bundle-{seed}.json',bundle)
        for name,stream in [('stationary',stationary),('shifted',shifted)]:
            xs=transform(stream)
            save(OUT/f'{name}-{seed}.json',{'rows':rows(stream),'boundaries':boundaries if name=='shifted' else [],
                 'baselines':{'Logistic regression':logistic.predict_proba(xs)[:,1].tolist(),'Random forest':forest.predict_proba(xs)[:,1].tolist()},'split':split})
        if seed==SEEDS[0]:
            save(PUBLIC/'model.json',bundle)
            # Compact public replay with all four regimes, not training examples.
            demo=[]; demo_boundaries=[]
            for phase,part in enumerate(phases):
                if phase:demo_boundaries.append(len(demo))
                chosen=part.iloc[:min(320,len(part))]
                demo.extend(rows(chosen))
            save(PUBLIC/'replay.json',{'rows':demo,'boundaries':demo_boundaries,'source':'Unique held-out measured flows; constructed replay order.','license':'CC BY 4.0'})
            examples=[]
            for family,grp in shifted.groupby('Attack_type'):
                examples.append(rows(grp.head(1))[0])
            save(PUBLIC/'examples.json',examples)
            manifest['primary_split']=split
            # Independent Python predictions to test the deployed JavaScript implementation.
            sample=shifted.head(80)
            save(PUBLIC/'parity.json',{'rows':rows(sample),'attack_probabilities':best.predict_proba(transform(sample))[:,1].tolist()})
        print('Finished',seed,split,'validation loss',bestloss,flush=True)
    save(PUBLIC/'dataset.json',manifest)

if __name__=='__main__':prepare()
