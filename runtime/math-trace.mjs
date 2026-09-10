/** Read-only arithmetic witnesses. No training, state mutation or display interpolation. */
import {transform,forward,clone} from './engine.mjs';
/** Exact additive logit terms; deterministic lowest-index tie break, no causal claim. */
export function logitContributions(trace){
 const terms=trace.hidden.map((h,k)=>h*trace.model.w2[k]);
 const maximum=Math.max(...terms.map(Math.abs));
 const ties=terms.flatMap((v,k)=>Math.abs(v)===maximum?[k]:[]);
 return {terms,strongest:ties[0],ties,bias:trace.model.b2,sum:terms.reduce((s,v)=>s+v,0),extent:Math.max(maximum,Math.abs(trace.model.b2))||1};
}
export function forwardTrace(bundle,model,raw){
 const x=transform(bundle,raw),{p,hidden}=forward(model,x);
 const hidden_terms=model.b1.map((_,k)=>x.map((v,j)=>v*model.w1[j][k]));
 const hidden_sums=hidden_terms.map((terms,k)=>model.b1[k]+terms.reduce((a,b)=>a+b,0));
 const output_terms=hidden.map((v,k)=>v*model.w2[k]);
 return {raw:clone(raw),x,log:raw.map(Math.log1p),mean:clone(bundle.mean),scale:clone(bundle.scale),
  standardized:raw.map((v,j)=>(Math.log1p(v)-bundle.mean[j])/bundle.scale[j]),
  model:clone(model),hidden_terms,hidden_sums,hidden,output_terms,
  logit:model.b2+output_terms.reduce((a,b)=>a+b,0),p,complement:1-p,trust:100*(1-p)};
}
export function parameterStep(step,kind,j,k){
 let before,after,gradient,expression;
 if(kind==='w1'){before=step.before.w1[j][k];after=step.after.w1[j][k];gradient=step.dh[k]*step.x[j]+step.l2*before;expression=`hidden gradient × transformed input + L2 × old weight`;}
 else if(kind==='b1'){before=step.before.b1[k];after=step.after.b1[k];gradient=step.dh[k];expression='hidden gradient (biases have no L2 penalty)';}
 else if(kind==='w2'){before=step.before.w2[k];after=step.after.w2[k];gradient=step.error*step.hidden[k]+step.l2*before;expression='(prediction − label) × hidden activation + L2 × old weight';}
 else if(kind==='b2'){before=step.before.b2;after=step.after.b2;gradient=step.error;expression='prediction − label (output bias has no L2 penalty)';}
 else throw Error('Unknown parameter kind');
 return {before,after,gradient,delta:after-before,lr:step.learning_rate,expression};
}
