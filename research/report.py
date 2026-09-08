"""Measured tables and publication figures; never substitute illustrative results."""
from pathlib import Path
import json, csv, zipfile, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.metrics import (roc_auc_score,average_precision_score,f1_score,precision_score,recall_score,
 balanced_accuracy_score,matthews_corrcoef,confusion_matrix,roc_curve,precision_recall_curve,brier_score_loss)
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'assets/research'; FIG=OUT/'figures'; FIG.mkdir(exist_ok=True,parents=True)
NAMES={'static':'Frozen MLP','ungoverned':'Adaptive MLP','monitor_only':'Audit-only MLP','governed':'DriftTrust gated',
       'no_replay':'Gated: no replay','no_attribution':'Gated: error only','Logistic regression':'Logistic regression','Random forest':'Random forest'}
COLORS={'static':'#7b8799','ungoverned':'#b66828','monitor_only':'#976fc0','governed':'#087f8c','no_replay':'#4d698a','no_attribution':'#bd5c6a','Logistic regression':'#809944','Random forest':'#273c66'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':300})

def savefig(name,fig):
    fig.tight_layout()
    for fmt in ['png','pdf','svg']:fig.savefig(FIG/f'{name}.{fmt}',bbox_inches='tight')
    plt.close(fig)

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p);pred=p>=.5;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'attack_f1':f1_score(y,pred,zero_division=0),'attack_precision':precision_score(y,pred,zero_division=0),
      'attack_recall':recall_score(y,pred,zero_division=0),'balanced_accuracy':balanced_accuracy_score(y,pred),
      'mcc':matthews_corrcoef(y,pred),'roc_auc':roc_auc_score(y,p),'average_precision':average_precision_score(y,p),
      'benign_false_alarm_rate':fp/max(tn+fp,1),'attack_miss_rate':fn/max(tp+fn,1),'brier':brier_score_loss(y,p),
      'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)}

def main():
    rows=[]; primary=None
    for path in sorted((ROOT/'data/prepared').glob('results-*.json')):
        d=json.loads(path.read_text());y=d['labels']
        if d['seed']==11 and d['protocol']=='shifted':primary=d
        for name,m in d['models'].items():
            es=[e for e in m['events'] if 'checks' in e]
            delays=[];missed=0
            if name not in ['static','Logistic regression','Random forest']:
                for i,b in enumerate(d['boundaries']):
                    end=d['boundaries'][i+1] if i+1<len(d['boundaries']) else len(y)
                    hits=[e['position']-b for e in m['events'] if b<=e['position']<end]
                    if hits:delays.append(min(hits))
                    else:missed+=1
            rows.append({'seed':d['seed'],'protocol':d['protocol'],'model':name,'n':len(y),**metrics(y,m['scores']),
                'attempts':len(m['events']),'accepted':m['accepted'],'rejected':m['rejected'],
                'eci_mean':float(np.mean([e['explanation_consistency']['eci'] for e in es])) if es else None,
                'audit_completeness':float(np.mean([all(k in e for k in ['checks','model_before_sha256','candidate_sha256','record_sha256','training_record_ids','anchor_record_ids']) for e in es])) if es else None,
                'gate_pass_rate':float(np.mean([all(e['checks'].values()) for e in es])) if es else None,
                'mean_alarm_delay_records':float(np.mean(delays)) if delays else None,'missed_regime_transitions':missed,
                'attempts_per_1000':len(m['events'])/len(y)*1000,'elapsed_ms':m['elapsed_ms']})
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'metrics_per_seed.csv',index=False)
    summary=[]
    measures=['attack_f1','attack_precision','attack_recall','balanced_accuracy','mcc','roc_auc','average_precision','benign_false_alarm_rate','attack_miss_rate','brier','attempts','accepted','rejected','eci_mean','gate_pass_rate','elapsed_ms']
    for (protocol,model),g in frame.groupby(['protocol','model']):
        entry={'protocol':protocol,'model':model,'name':NAMES[model],'seeds':len(g),'n_per_seed':int(g.n.iloc[0])}
        for metric in measures:
            a=g[metric].dropna().to_numpy(float)
            if len(a):
                sd=float(a.std(ddof=1)) if len(a)>1 else 0;half=float(t.ppf(.975,len(a)-1)*sd/np.sqrt(len(a))) if len(a)>1 else 0
                entry[metric]={'mean':float(a.mean()),'sd':sd,'interval95_half_width':half}
            else:entry[metric]=None
        summary.append(entry)
    ds=json.loads((OUT/'dataset.json').read_text())
    result={'dataset':ds,'summary':summary,'uncertainty':'Mean, sample SD and descriptive t intervals across five seeded splits. Splits share source data and all novel-family rows; intervals are not independent-sample population guarantees.',
      'primary_seed':11,'positive_class':'attack','decision_threshold':.5,
      'timing_scope':'Local Node runtime wall time; excludes initial training and I/O, includes governance hashing; not cloud throughput or a controlled overhead benchmark.',
      'primary':{name:metrics(primary['labels'],m['scores']) for name,m in primary['models'].items()}}
    (OUT/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    # Exact paired differences, with no significance claim.
    paired=[]
    for protocol in ['stationary','shifted']:
        g=frame[frame.protocol==protocol].pivot(index='seed',columns='model',values='attack_f1')
        for seed,r in g.iterrows():paired.append({'protocol':protocol,'seed':seed,'gated_minus_frozen_f1':r.governed-r['static'],'gated_minus_ungoverned_f1':r.governed-r.ungoverned,'audit_only_minus_ungoverned_f1':r.monitor_only-r.ungoverned})
    pd.DataFrame(paired).to_csv(OUT/'paired_differences.csv',index=False)
    # Figure 1: raw versus deduplicated counts, including what was removed.
    fig,ax=plt.subplots(figsize=(9,4.6));names=list(ds['raw_class_counts']);pos=np.arange(len(names))
    ax.barh(pos-.18,[ds['raw_class_counts'][k] for k in names],.36,label='Raw flows',color='#9ba8b7')
    ax.barh(pos+.18,[ds['unique_class_counts'].get(k,0) for k in names],.36,label='Unique valid input vectors',color='#087f8c')
    ax.set_yticks(pos,[n.replace('_',' ') for n in names]);ax.set_xscale('log');ax.set_xlabel('Records (log scale)');ax.legend();savefig('01_dataset_audit',fig)
    order=['Logistic regression','Random forest','static','ungoverned','monitor_only','governed','no_replay','no_attribution']
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    for ax,protocol in zip(axes,['stationary','shifted']):
        ss={r['model']:r for r in summary if r['protocol']==protocol}
        vals=[ss[n]['attack_f1']['mean'] for n in order];err=[ss[n]['attack_f1']['sd'] for n in order]
        ax.barh(range(len(order)),vals,xerr=err,color=[COLORS[n] for n in order],capsize=3)
        ax.set_yticks(range(len(order)),[NAMES[n] for n in order]);ax.invert_yaxis();ax.set_xlim(0,1.05);ax.set_xlabel('Attack-class F1 (mean ± 1 SD, five splits)');ax.set_title(protocol.title()+' replay')
    savefig('02_baselines_and_ablations',fig)
    y=np.array(primary['labels']);fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
    rolling=[]
    for mode in ['static','ungoverned','governed']:
        p=np.array(primary['models'][mode]['scores']);xx=[];ba=[];fr=[]
        for i in range(0,len(y),256):
            a=y[i:i+256];b=p[i:i+256];xx.append(i+len(a)/2)
            ba.append(balanced_accuracy_score(a,b>=.5) if len(set(a))==2 else np.nan)
            fr.append(float(((b>=.5)!=a).mean()))
            rolling.append({'model':mode,'start':i,'end':i+len(a),'balanced_accuracy':ba[-1],'error_rate':fr[-1]})
        axes[0].plot(xx,ba,label=NAMES[mode],color=COLORS[mode]);axes[1].plot(xx,fr,label=NAMES[mode],color=COLORS[mode])
    for ax in axes:
        for b in primary['boundaries']:ax.axvline(b,color='#888',linestyle=':',linewidth=.8)
        ax.set_ylim(0,1);ax.grid(alpha=.15)
    axes[0].legend(ncol=3,loc='lower left');axes[0].set_ylabel('Balanced accuracy');axes[1].set_ylabel('Error fraction');axes[1].set_xlabel('Constructed replay position (256-flow reporting windows)')
    savefig('03_stream_performance',fig);pd.DataFrame(rolling).to_csv(OUT/'rolling_metrics.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for mode in ['static','ungoverned','governed','Random forest']:
        p=primary['models'][mode]['scores'];fpr,tpr,_=roc_curve(y,p);precision,recall,_=precision_recall_curve(y,p)
        axes[0].plot(fpr,tpr,color=COLORS[mode],label=NAMES[mode]);axes[1].plot(recall,precision,color=COLORS[mode],label=NAMES[mode])
    axes[0].plot([0,1],[0,1],':',color='#aaa');axes[0].set(xlabel='Benign false-positive rate',ylabel='Attack recall');axes[1].axhline(y.mean(),linestyle=':',color='#aaa');axes[1].set(xlabel='Attack recall',ylabel='Attack precision');axes[1].legend(fontsize=8)
    savefig('04_roc_pr',fig)
    fig,axes=plt.subplots(1,3,figsize=(10,3.4))
    for ax,mode in zip(axes,['static','ungoverned','governed']):
        cm=confusion_matrix(y,np.array(primary['models'][mode]['scores'])>=.5,labels=[0,1]);ax.imshow(cm/cm.sum(axis=1,keepdims=True),vmin=0,vmax=1,cmap='Blues')
        for i in range(2):
            for j in range(2):ax.text(j,i,f'{cm[i,j]:,}\n{cm[i,j]/cm[i].sum():.1%}',ha='center',va='center',color='white' if cm[i,j]/cm[i].sum()>.55 else '#132333')
        ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Benign','Attack'],yticklabels=['Benign','Attack'],xlabel='Predicted',ylabel='Actual',title=NAMES[mode])
    savefig('05_confusion_matrices',fig)
    events=primary['models']['governed']['events'];fig,axes=plt.subplots(2,1,figsize=(10,5.5),sharex=True)
    for e in events:
        color='#087f8c' if e['accepted'] else '#bd4b3e';axes[0].scatter(e['position'],e['explanation_consistency']['eci'],c=color,marker='o' if e['accepted'] else 'x')
        axes[1].scatter(e['position'],e['same_anchor_candidate']['loss']-e['same_anchor_before']['loss'],c=color,marker='o' if e['accepted'] else 'x')
    axes[0].axhline(.5,color='#777',linestyle='--');axes[1].axhline(.05,color='#777',linestyle='--');axes[0].set_ylabel('ECI');axes[0].set_ylim(0,1.05);axes[1].set_ylabel('Anchor log-loss change');axes[1].set_xlabel('Candidate update position (green: accepted; red: rejected)')
    savefig('06_governance_decisions',fig)
    fig,ax=plt.subplots(figsize=(10,4));families=sorted(set(primary['families']));pos=np.arange(len(families));fam=np.array(primary['families'])
    for j,mode in enumerate(['static','ungoverned','governed']):
        pred=np.array(primary['models'][mode]['scores'])>=.5;v=[np.mean(pred[fam==f]==y[fam==f]) for f in families]
        ax.bar(pos+(j-1)*.25,v,width=.25,color=COLORS[mode],label=NAMES[mode])
    ax.set_xticks(pos,[f.replace('_',' ')+'\n(n='+str(sum(fam==f))+')' for f in families],rotation=35,ha='right');ax.set_ylabel('Correct classification fraction');ax.legend(ncol=3);savefig('07_per_family',fig)
    def diagram(name,boxes,links,size):
        fig,ax=plt.subplots(figsize=size);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        for key,(x,y,w,h,label,color) in boxes.items():
            ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009',facecolor=color,edgecolor='#a7b3c0',linewidth=.8));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9)
        for a,b,label in links:
            x,y,w,h,*_=boxes[a];xx,yy,ww,hh,*_=boxes[b];start=(x+w/2,y);end=(xx+ww/2,yy+hh)
            if abs(y-yy)<.03:start=(x+w,y+h/2);end=(xx,yy+hh/2)
            ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=12,color='#536577',connectionstyle='arc3,rad=0'))
            if label:ax.text((start[0]+end[0])/2+.012,(start[1]+end[1])/2,label,fontsize=8,ha='left')
        savefig(name,fig)
    diagram('08_research_workflow',{
      'raw':(.03,.79,.27,.14,'UCI RT-IoT2022\n123,117 captured flows','#e9eef3'),
      'clean':(.37,.79,.27,.14,'Validate + deduplicate\n17,701 unique feature vectors','#e9eef3'),
      'split':(.70,.79,.27,.14,'Known-family split\nNovel families: test only','#e9eef3'),
      'fit':(.07,.47,.36,.16,'Training only\nlog1p → scaling → 12–24–1 MLP','#e3f2f0'),
      'val':(.57,.47,.36,.16,'Validation only\nModel selection + fixed anchor set','#e3f2f0'),
      'eval':(.12,.13,.76,.18,'Five seeds × two constructed replay protocols\nPredict batch → reveal labels → detect → candidate update → audit gate\nFrozen / adaptive / audit-only / gated / ablations / logistic / random forest','#f1f3f6')},
      [('raw','clean',''),('clean','split',''),('split','fit',''),('split','val',''),('fit','eval',''),('val','eval','')],(11,6))
    diagram('09_live_architecture',{
      'input':(.03,.79,.27,.14,'Browser inputs\nMeasured flow / CSV / replay','#e9eef3'),
      'api':(.37,.79,.27,.14,'Worker API\nValidate input + isolate session','#e3f2f0'),
      'db':(.71,.79,.26,.14,'D1 database\nSession model + audit chain','#e9eef3'),
      'score':(.05,.48,.26,.15,'Actual MLP inference\nRisk + feature attribution','#e3f2f0'),
      'update':(.37,.48,.27,.15,'Label feedback + drift\nTrain candidate with replay','#e3f2f0'),
      'gate':(.71,.48,.26,.15,'Fixed-anchor policy gate\nECI + loss + attack misses','#e3f2f0'),
      'accept':(.35,.12,.28,.17,'Accepted candidate\nActivate session model','#daf0e4'),
      'reject':(.70,.12,.27,.17,'Rejected candidate\nKeep previous model','#fae8e3')},
      [('input','api',''),('api','db',''),('api','score',''),('score','update',''),('update','gate',''),('gate','accept','PASS'),('gate','reject','FAIL')],(11,6))
    # Full numerical results and event logs, without the source dataset or private conversation.
    with zipfile.ZipFile(OUT/'replication_results.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in (ROOT/'data/prepared').glob('results-*.json'):z.write(p,p.name)
        for p in [OUT/'metrics_per_seed.csv',OUT/'paired_differences.csv',OUT/'dataset.json',OUT/'execution.json']:z.write(p,p.name)
    with zipfile.ZipFile(OUT/'paper_figures.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in FIG.iterdir():z.write(p,'figures/'+p.name)
    print(frame[['seed','protocol','model','attack_f1','balanced_accuracy','accepted','rejected']].to_string(index=False))

if __name__=='__main__':main()
