'use strict';
const $=id=>document.getElementById(id);
let catalog={}, active=null, serial=0, pendingRequest=null, locationMap=null, currentView='overview';
let draft={lat:-26.312389,lon:-50.080639,name:'Papanduva'}, resultOrigin='Saved assessment';
const systems={open_ground:['Open field + ground','Ambient weather','Rain, cold and heat remain outdoor exposures.','Native or amended soil','Mapped soil is a screening layer. Drainage and field tests remain necessary.','Water supply','Dry spells do not account for irrigation or root-zone storage.'],open_pots:['Open field + pots','Fruit exposure remains','Pots do not stop rain reaching berries or remove cold exposure.','Managed substrate','Native-soil chemistry is not the pot root zone. Substrate pH, aeration and drainage must be specified.','Irrigation dependence','Small root-zone storage, water quality and root heating need assessment.'],tunnel_ground:['Tunnel + ground','Potential rain interception','An effective cover can reduce direct fruit wetting; no calibrated numerical reduction is applied.','Heat, light and cold','Ventilation and cover transmission matter. An unheated tunnel does not guarantee frost protection.','Ground constraints remain','Runoff, drainage and native or amended soil still need assessment.'],tunnel_pots:['Tunnel + pots','Cover + managed root zone','Potential rain interception and substrate control are separate effects, not universal protection.','Remaining exposures','Heat, humidity, light loss and cold remain conditional on the actual structure.','Water and drainage','Reliable irrigation, suitable water chemistry and freely draining containers are essential.']};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const good=a=>a.filter(v=>typeof v==='number'&&Number.isFinite(v));
const mean=a=>{a=good(a);return a.length?a.reduce((s,v)=>s+v,0)/a.length:null};
const median=a=>{a=good(a).sort((x,y)=>x-y);return a.length?(a[Math.floor((a.length-1)/2)]+a[Math.floor(a.length/2)])/2:null};
const fmt=(v,d=1)=>v===null||v===undefined?'Unavailable':Number(v).toLocaleString('en-US',{maximumFractionDigits:d});
function card(title,value,unit,desc,values,index){const a=good(values);return `<article class="risk"><div class="risk-top"><h3>${title}</h3><span class="risk-index">0${index}</span></div><div class="metric">${fmt(value)}${value===null?'':`<small>${unit}</small>`}</div><p>${desc}</p><div class="detail">${a.length?`${a.length}/15 valid years · range ${fmt(Math.min(...a))}–${fmt(Math.max(...a))}`:'Not acquired for this coordinate'}</div></article>`}
function bars(id,values,labels,unit){const node=$(id);const w=Math.max(290,node.clientWidth),h=220,p={l:48,r:10,t:16,b:34},valid=good(values);if(!valid.length){node.innerHTML='<p class="small">This metric is unavailable. No values have been substituted.</p>';return}const lo=Math.min(0,...valid),hi=Math.max(...valid,1),y=v=>h-p.b-(v-lo)/(hi-lo)*(h-p.b-p.t),step=(w-p.l-p.r)/values.length;let svg=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(unit)} by ${id==='monthly-chart'?'month':'year'}"><title>${esc(unit)}; exact values available in the data tables or JSON export</title>`;for(let n=0;n<=3;n++){const v=lo+(hi-lo)*n/3;svg+=`<line x1="${p.l}" x2="${w-p.r}" y1="${y(v)}" y2="${y(v)}" stroke="#ebebeb"/><text x="${p.l-8}" y="${y(v)+4}" text-anchor="end">${fmt(v,0)}</text>`}values.forEach((v,i)=>{const x=p.l+step*i;if(v!==null&&Number.isFinite(v))svg+=`<rect class="bar" x="${x+step*.16}" width="${step*.68}" y="${Math.min(y(0),y(v))}" height="${Math.max(1,Math.abs(y(v)-y(0)))}"><title>${labels[i]}: ${fmt(v,2)} ${esc(unit)}</title></rect>`;if(i%Math.ceil(labels.length/(w<400?6:12))===0)svg+=`<text x="${x+step/2}" y="${h-10}" text-anchor="middle">${labels[i]}</text>`});node.innerHTML=svg+'</svg>'}
function charts(){if(!active)return;const m=$('monthly-metric').value,a=$('annual-metric').value;bars('monthly-chart',active.climatology[m],['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],$('monthly-metric').selectedOptions[0].text);bars('annual-chart',active.annual.map(r=>r[a]),active.annual.map(r=>r.year),$('annual-metric').selectedOptions[0].text)}
function management(){
  const s=systems[$('system').value];
  $('management-title').textContent=s[0];
  $('management').innerHTML=[1,3,5].map(i=>`<article><h3>${s[i]}</h3><p>${s[i+1]}</p></article>`).join('');
  renderSoil();renderPlanting();renderProduction();renderOverview();
}
function renderSoil(){if(!active)return;const soil=active.soil??[];$('soil-status').textContent=soil.length?`${soil.length}/45 mapped records`:'Not acquired';if(!soil.length){$('soil-content').innerHTML='<div class="soil-note">No soil snapshot is available at this coordinate. Weather results remain usable; soil suitability is not assessed.</div>';return}const rows=[];for(const p of ['phh2o','soc','sand','silt','clay'])for(const depth of ['0-5cm','5-15cm','15-30cm']){const r=soil.filter(x=>x.property===p&&x.depth===depth),v=s=>r.find(x=>x.statistic===s)?.value;rows.push(`<tr><td>${({phh2o:'pH in water',soc:'Organic carbon',sand:'Sand',silt:'Silt',clay:'Clay'})[p]}</td><td>${depth}</td><td>${fmt(v('mean'))} ${esc(r[0]?.unit??'')}</td><td>${fmt(v('Q0.05'))}–${fmt(v('Q0.95'))}</td></tr>`)}$('soil-content').innerHTML=($('system').value.endsWith('pots')?'<div class="soil-note">For pots, these native-soil estimates are site context only. Substrate, irrigation water and container drainage have not been assessed.</div>':'')+`<div class="table-scroll"><table><thead><tr><th>Property</th><th>Depth</th><th>Mean</th><th>5th–95th bounds</th></tr></thead><tbody>${rows.join('')}</tbody></table></div><p class="small">ISRIC SoilGrids predictions, not field measurements. Bounds describe prediction uncertainty. WCS returned geographic-grid samples; native-grid parity and field drainage remain unverified.</p>`}
const CLASSES=['Evergreen','Semi-evergreen','Deciduous'],STAGES=[['chill','Chill fulfilled'],['budbreak','Budbreak'],['flowering_start','Flowering start'],['flowering_end','Flowering end'],['harvest_start','Harvest start'],['harvest_end','Harvest end']];
const md=s=>{if(!s)return 'Unavailable';const [m,d]=s.split('-');return `${Number(d)} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][Number(m)-1]}`};
const pct=v=>v===null||v===undefined?'Unavailable':`${fmt(v*100,2)}%`;
const eligibilityLabel={ranked:'Recurring risk',below_frequency:'Below recurrence threshold',insufficient_data:'Insufficient valid winters',not_applicable:'Not applicable',definition_pending:'Exposure only; event definition pending'};
function sourceLinks(sources){
  return (sources??[]).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noreferrer">${esc(s.title)}</a>`).join(' · ');
}
function renderPlanting(){
  if(!active)return;
  const p=active.planting,node=$('planting-content');
  $('planting-badge').textContent=p?.status==='available'?'Regional field guidance':'No applicable regional window';
  if(!p){node.innerHTML='<p>No establishment guidance accompanies this result.</p>';return}
  node.innerHTML=`<div class="planting-window"><span class="stamp">${esc(p.region??'Region not established')}</span><h3>${esc(p.label)}</h3><p>${esc(p.precision)}</p>${p.status==='available'&&p.window?`<p class="small">${p.window.crosses_year?'This regional window crosses the calendar-year boundary.':''}</p>`:`<p>${esc(p.reason??'No source-supported regional establishment window is available.')}</p>`}</div>
    <div class="planting-guidance"><p>This is regional nursery-establishment guidance, not an annual planting date or a first-harvest prediction.</p><details><summary>Sources, stock requirements and limits</summary><p>${esc(p.basis)}</p>
    <h3>Conditions and limits</h3><ul>${[...p.assumptions,...p.limitations].map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>Not numerically adjusted for tunnels, pots or irrigation.</p><h3>Regional sources</h3><p class="evidence-sources">${sourceLinks(p.sources)}</p><p class="small">Method: ${esc(p.method)}</p></details></div>`;
}
function riskRows(records){
  return records.map(r=>`<tr><td>${r.rank??'Not ranked'}</td><th scope="row">${esc(r.label)}<span class="risk-stage">${esc(r.stage)}</span></th>
    <td>${r.years_with_event===null?'Not assigned':r.years_with_event} / ${r.valid_years}<span class="risk-stage">k / n; ${r.total_years} total winters</span></td>
    <td>${r.frequency===null?'Not assigned':pct(r.frequency)}${r.ci95?`<span class="risk-stage">95% Wilson CI ${pct(r.ci95[0])} to ${pct(r.ci95[1])}</span>`:''}</td>
    <td><strong>${esc(eligibilityLabel[r.eligibility])}</strong><p>${esc(r.reason)}</p><p>${esc(r.event_definition??'No event threshold or frequency is assigned.')}</p><div class="evidence-sources">${sourceLinks(r.evidence)}</div></td></tr>`).join('');
}
function riskTable(records,label){
  return `<div class="table-scroll" tabindex="0" role="region" aria-label="${esc(label)}"><table class="risk-assessments"><thead><tr><th>Rank</th><th>Assessment / stage</th><th>Event winters / valid winters</th><th>Frequency</th><th>Eligibility and evidence</th></tr></thead><tbody>${riskRows(records)}</tbody></table></div>`;
}
function renderProduction(){
  if(!active)return;
  const p=active.production,node=$('production-content'),badge=$('production-badge'),previous=node.querySelector('.cycle-panel')?.dataset;
  const view=previous?{winter:previous.winter,stage:previous.stage}:null;
  if(!p||p.status!=='available'){
    badge.textContent='Not available';
    const warm=p?.warm_midwinter_fallback;
    node.innerHTML=`<div class="soil-note"><h3>A crop calendar is not available here</h3><p>${esc(p?.reason??'Production analysis is not part of this result.')} Daily climate history remains usable. Planting guidance is assessed separately.</p><button class="text-button" type="button" data-open-view="climate">View climate history →</button></div>
      ${warm?`<article class="prod-panel"><span class="stamp">Independent winter context / Daily data only</span><h3>${esc(warm.label)}</h3><div class="metric">${fmt(warm.summary.mean,1)}<small>${esc(warm.unit)}</small></div><p class="small">Mean across ${warm.summary.n} valid winters. p10 to p90 ${fmt(warm.summary.p10,1)} to ${fmt(warm.summary.p90,1)} ${esc(warm.unit)}.</p><p class="small">${esc(warm.note)}</p><p class="small">These are daily maximum-temperature counts, not estimated warm hours, measured chill negation or ranked crop risks.</p><details><summary>Warm mid-winter daily proxy by winter</summary><div class="table-scroll" tabindex="0" role="region" aria-label="Daily warm mid-winter proxy"><table><thead><tr><th>Winter</th><th>UTC window, inclusive</th><th>${esc(warm.unit)}</th></tr></thead><tbody>${warm.seasons.map(s=>`<tr><th scope="row">${s.winter_year}</th><td>${esc(s.window.join(' to '))}</td><td>${fmt(s.value,0)}</td></tr>`).join('')}</tbody></table></div></details></article>`:''}`;
    return;
  }
  const c=p.classification,cal=p.calendar,rk=p.risks,a=p.assumptions,open=$('system').value==='open_ground';
  const hypothetical=!c.multi_feature.majority||c.multi_feature.majority==='Evergreen';
  badge.textContent=`${p.profile} · ${a.chill_requirement_hours} h chill requirement`;
  const rule=r=>{const x=c[r];const counts=CLASSES.map(k=>`${k.replace('Semi-evergreen','Semi')} ${x.year_counts[k]}`).join(' · ');return `<tr><td>${r==='chill_only'?'Chill-only':'Multi-feature'}</td><td>${esc(c.mean_based[r]??'Unavailable')}</td><td>${counts}</td><td><strong>${esc(x.majority??'Unavailable')}</strong>${x.majority_share!==null&&x.majority_share!==undefined?` <span class="small">${pct(x.majority_share)} of ${x.valid_years}</span>`:''}</td></tr>`};
  const metrics=p.metric_catalog;
  const exposureRows=metrics.map(m=>{const s=rk.exposures[m.key]??p[m.key];return `<tr><th scope="row">${esc(m.label)}<span class="risk-stage">${esc(m.stage)} · ${esc(m.unit)}</span></th><td>${fmt(s?.mean,2)}</td><td>${fmt(s?.median,2)}</td><td>${fmt(s?.p10,2)} to ${fmt(s?.p90,2)}</td><td>${s?.n??0} / ${p.seasons.length}</td><td>${esc(m.note)}</td></tr>`}).join('');
  const seasons=p.seasons.map(s=>`<tr><th scope="row">${s.winter_year}</th><td>${esc(s.status)}</td><td>${esc(c.per_year[s.winter_year]?.multi_feature??'Unclassified')}</td><td>${esc(s.chill_date??'Unavailable')}</td><td>${esc(s.budbreak_date??'Unavailable')}</td><td>${s.flowering?esc(s.flowering.join(' to ')):'Unavailable'}</td><td>${s.harvest?esc(s.harvest.join(' to ')):'Unavailable'}</td><td>${s.warm_midwinter_window?esc(s.warm_midwinter_window.join(' to ')):'Unavailable'}</td>${metrics.map(m=>`<td>${fmt(m.key in s?s[m.key]:s.metrics?.[m.key],2)}${s.issues?.[m.key]?`<span class="risk-stage">${esc(s.issues[m.key])}</span>`:''}</td>`).join('')}</tr>`).join('');
  const sens=Object.entries(p.sensitivity).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${v.chill_definition==='below_7_2'?'T < 7.2°C':'0–7.2°C'}</td><td>${v.chill_requirement_hours}</td><td>${fmt(v.chill_hours_mean,0)}</td><td>${esc(v.majority_multi_feature??'Unavailable')}</td><td>${md(v.flowering_start_median)}</td><td>${md(v.harvest_start_median)}</td><td>${pct(v.flowering_freeze_frequency)}</td></tr>`).join('');
  node.innerHTML=`${open?'':'<div class="soil-note">Evaluated for open field + ground. Growing setup changes qualitative notes only; no tunnel or pot adjustment is applied.</div>'}
    <div class="production-reference"><div class="prod-grid"><article class="prod-panel"><span class="stamp">System hypothesis</span><div class="metric">${esc(c.multi_feature.majority??'Unclassified')}</div><p class="small">Two-thirds majority across ${c.multi_feature.valid_years} valid winters. Mean chill ${fmt(p.chill_hours.mean,0)} h, p10 to p90 ${fmt(p.chill_hours.p10,0)} to ${fmt(p.chill_hours.p90,0)} h.</p>
    <div class="table-scroll" tabindex="0" role="region" aria-label="System classification"><table><thead><tr><th>Rule</th><th>From means</th><th>Per-winter counts</th><th>Majority</th></tr></thead><tbody>${rule('chill_only')}${rule('multi_feature')}</tbody></table></div><p class="small">Evergreen &lt;${a.evergreen_chill_max} h with warm winter months and no freezing; Deciduous ≥${a.deciduous_chill_min} h; otherwise semi-evergreen. A climate hypothesis, not a cultivar verdict.</p></article>
    <article class="prod-panel"><span class="stamp">${hypothetical?'Hypothetical chill-triggered calendar; not applicable':'Assumed bearing-plant calendar'}</span><div class="table-scroll" tabindex="0" role="region" aria-label="Assumed calendar"><table><thead><tr><th>Stage</th><th>Median</th><th>p10 to p90</th><th>Winters</th></tr></thead><tbody>${STAGES.map(([k,l])=>`<tr><td>${l}</td><td>${md(cal[k]?.median_date)}</td><td>${md(cal[k]?.p10_date)} to ${md(cal[k]?.p90_date)}</td><td>${cal[k]?.n??0}</td></tr>`).join('')}</tbody></table></div><p class="small">${a.chill_requirement_hours} h chill, then ${a.gdd_to_budbreak} °C·d above ${a.gdd_base_c}°C to budbreak; flowering +${a.flowering_after_budbreak_days[0]} to +${a.flowering_after_budbreak_days[1]} d; harvest +${a.harvest_after_flowering_start_days[0]} to +${a.harvest_after_flowering_start_days[1]} d from flowering start. Provisional bearing-plant constants, not an establishment plan.</p></article></div>
    <article class="prod-panel"><h3>Exposure catalogue</h3><p class="small">${hypothetical?'Crop-stage exposures use hypothetical chill-triggered dates, not an applicable crop calendar. ':''}Warm mid-winter hours are independent winter context. Missing values are not zero; counts and thresholds are not estimates of crop loss.</p><div class="table-scroll" tabindex="0" role="region" aria-label="All exposure summaries"><table class="exposure-table"><thead><tr><th>Metric / unit</th><th>Mean</th><th>Median</th><th>p10 to p90</th><th>Valid winters</th><th>Definition and limits</th></tr></thead><tbody>${exposureRows}</tbody></table></div></article>
    <details><summary>Every winter, all exposure values and missing-data reasons</summary><p class="small">Warm-window end dates are inclusive. Each crop exposure uses that winter's own modelled stage, not a median or timing-spread window.${hypothetical?' Crop-stage values are hypothetical, not applicable risk labels.':''}</p><div class="table-scroll" tabindex="0" role="region" aria-label="Per-winter dates and all exposures"><table class="winter-table"><thead><tr><th>Winter</th><th>Status</th><th>Class</th><th>Chill date</th><th>Budbreak</th><th>Flowering</th><th>Harvest</th><th>Warm winter window</th>${metrics.map(m=>`<th>${esc(m.label)} · ${esc(m.unit)}</th>`).join('')}</tr></thead><tbody>${seasons}</tbody></table></div></details>
    <details><summary>Sensitivity, assumptions and changes from the R workflow</summary><div class="table-scroll" tabindex="0" role="region" aria-label="Profile sensitivity"><table><thead><tr><th>Profile</th><th>Chill definition</th><th>Requirement h</th><th>Mean chill</th><th>Majority</th><th>Flowering start</th><th>Harvest start</th><th>Flowering freeze</th></tr></thead><tbody>${sens}</tbody></table></div><ul class="small">${p.changes.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><ul class="small">${p.limitations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details></div>`;
  CycleView.mount(node,p,{site:active.site.name,system:$('system').value,view});
}
const stageNames={chill:'Winter context',flower:'Flowering',fruit:'Fruit development',harvest:'Harvest',whole:'Across crop stages'};
function showView(name,focus=false){
  if(!$(`panel-${name}`))return;
  currentView=name;
  document.querySelectorAll('[data-view]').forEach(b=>{
    const selected=b.dataset.view===name;
    b.setAttribute('aria-selected',String(selected));b.tabIndex=selected?0:-1;
  });
  document.querySelectorAll('.view-panel').forEach(p=>p.hidden=p.id!==`panel-${name}`);
  if(name==='climate')charts();
  if(focus)$(`panel-${name}`).focus({preventScroll:true});
}
function renderOverview(){
  if(!active)return;
  const p=active.production,available=p?.status==='available',majority=available?p.classification.multi_feature.majority:null;
  const applicable=available&&majority&&majority!=='Evergreen',rk=available?p.risks:null;
  const summaryCard=(label,value,note)=>`<article class="summary-card"><span class="eyebrow">${label}</span><div class="summary-value">${esc(value)}</div><p>${esc(note)}</p></article>`;
  $('decision-summary').innerHTML=
    summaryCard('Production-system hypothesis',available?(majority??'Unclassified'):'Not assessed',available?'Climate-based hypothesis, not a cultivar recommendation.':'Full hourly analysis is not exposed for this coordinate.')+
    summaryCard('Assumed harvest window',applicable?`${md(p.calendar.harvest_start.median_date)} to ${md(p.calendar.harvest_end.median_date)}`:'No supported calendar',applicable?'Median modelled dates for bearing plants. Not observed harvest or first-year establishment.':'Evergreen, unclassified or hourly-unavailable locations need a supported crop calendar.')+
    summaryCard('Evidence to interpret',rk?`${rk.ranked.length} recurring ${rk.ranked.length===1?'risk':'risks'}`:'Daily weather context',rk?`${rk.policy.min_valid_years}+ valid winters and ${pct(rk.policy.min_frequency)}+ recurrence to qualify. Frequency is not severity or crop-loss probability.`:'Climate history remains useful. Missing stage evidence is not low risk.');
  const chips=[
    [true,`Daily weather · ${active.provenance.rows.toLocaleString()} rows`],
    [available,available?'Hourly analysis available':'Hourly analysis unavailable'],
    [applicable,applicable?'Assumed crop calendar':'No applicable crop calendar'],
    [active.planting?.status==='available',active.planting?.status==='available'?'Regional planting guide':'Planting guide unavailable'],
    [active.soil?.length===45,`Soil · ${active.soil?.length??0}/45 records`],
  ];
  $('coverage-summary').innerHTML=chips.map(([ok,text])=>`<span class="coverage-chip${ok?'':' is-limited'}">${esc(text)}</span>`).join('');
  if(rk){
    $('headline-risks').innerHTML=rk.ranked.length?`<div class="recurring-grid">${rk.ranked.map(r=>`<article class="recurring-card" data-risk="${esc(r.risk)}"><div class="rank-line"><span class="rank-number">Rank ${r.rank}</span><span>${esc(stageNames[r.stage]??r.stage)}</span></div><h3>${esc(r.label)}</h3><div class="recurrence-value">${pct(r.frequency)} <span>of assessable winters</span></div><div class="frequency-track" aria-hidden="true"><span style="width:${r.frequency*100}%"></span></div><p class="small">${r.years_with_event} of ${r.valid_years} valid winters · ${r.total_years} total</p><details><summary>Definition &amp; uncertainty</summary><p>${esc(r.event_definition)}</p><p>${esc(r.reason)}</p><p>95% Wilson interval: ${pct(r.ci95?.[0])} to ${pct(r.ci95?.[1])}. This describes sampling uncertainty, not model accuracy.</p><p class="evidence-sources">${sourceLinks(r.evidence)}</p></details><button type="button" class="text-button" data-explore-stage="${esc(r.stage)}">See stage evidence →</button></article>`).join('')}</div>`:
      `<div class="notice"><h3>${applicable?'No assessment meets the reporting gate':'Crop risks cannot be ranked here'}</h3><p>${applicable?'This is not an all-clear. Low recurrence, insufficient years or an undefined loss threshold can keep an assessment out of the ranking.':'The available crop-stage calculations are hypothetical. They cannot establish an applicable calendar or risk ranking.'}</p></div>`;
    $('headline-risks').innerHTML+=`<p class="ranking-note">Ranks compare recurrence, not severity. Equal frequencies share a rank. ${rk.demoted.length} other assessments retain their evidence and exclusion reasons.</p><details><summary>Why other assessments are not ranked</summary>${riskTable(rk.demoted,'Assessments outside headline ranking')}</details>`;
    $('risk-evidence').innerHTML=riskTable(Object.values(rk.by_id),'All risk definitions and eligibility');
  }else{
    $('headline-risks').innerHTML='<div class="notice"><h3>Stage risks have not been assessed</h3><p>The location has no extracted hourly crop calendar in this service. Explore daily climate history; do not interpret unavailable risks as zero.</p><button class="text-button" type="button" data-open-view="climate">Open climate history →</button></div>';
    $('risk-evidence').innerHTML=`<p class="small">${esc(p?.reason??'No crop-stage result is available.')}</p>`;
  }
  const signal=(title,key,stage,extra='')=>{
    const m=available?p.metric_catalog.find(m=>m.key===key):null,s=available?(rk.exposures[key]??p[key]):null;
    const hypothetical=!applicable&&stage!=='chill';
    return `<article class="signal-card" data-metric="${key}"><span class="eyebrow">${esc(stageNames[stage])}</span><h3>${title}</h3><div class="metric">${fmt(s?.mean)}${s?.mean!=null?`<small>${esc(m?.unit)}</small>`:''}</div><p>${s?`Mean · ${s.n}/${p.seasons.length} valid winters`:'Crop-stage data unavailable'}</p>${extra}<p class="signal-context">${hypothetical&&available?'Hypothetical stage dates. ':''}Exposure only, not a ranked loss estimate.</p>${m?`<details><summary>What this measures</summary><p>${esc(m.note)}</p><p>p10 to p90: ${fmt(s?.p10)} to ${fmt(s?.p90)} ${esc(m.unit)}.</p></details>`:''}<button type="button" class="text-button" data-explore-stage="${stage}">View detail →</button></article>`;
  };
  const dry=available?rk.exposures.fruit_max_dry_days:null;
  const warm=p?.warm_midwinter_fallback;
  $('exposure-highlights').innerHTML=signal('Pollination weather','flowering_pollination_unfavourable_days','flower')+
    (available?signal('Warm midwinter','warm_midwinter_hours','chill'):`<article class="signal-card"><span class="eyebrow">Winter context · daily fallback</span><h3>Warm midwinter days</h3><div class="metric">${fmt(warm?.summary.mean)}${warm?.summary.mean!=null?'<small>days</small>':''}</div><p>${warm?`Daily Tmax >21°C · ${warm.summary.n} valid winters`:'Daily fallback unavailable'}</p><p class="signal-context">Days, not estimated hours or measured chill negation.</p><button type="button" class="text-button" data-open-view="season">View window &amp; definition →</button></article>`)+
    signal('Fruit frost exposure','fruit_frost_days','fruit')+
    signal('Longest flowering dry run','flowering_max_dry_days','flower',`<p>Fruit-development mean: ${fmt(dry?.mean)}${dry?.mean!=null?' days':''}${dry?` · ${dry.n} valid winters`:''}</p>`);
}
function render(r){
  if(r.method_version!=='location-evidence-v4'||(r.production?.status==='available'&&r.production.method!=='open-field-production-v2'))
    throw Error('This result uses an older analysis method. Update saved snapshots and the analysis service to location-evidence-v4. Old risk results are not displayed.');
  $('production-content').replaceChildren();
  active=r;$('results').hidden=false;
  $('location-name').textContent=r.site.name;
  $('result-origin').textContent=resultOrigin;
  $('coordinate-label').textContent=`${r.site.lat.toFixed(6)}, ${r.site.lon.toFixed(6)} · 2011–2025 · UTC`;
  const ann=r.annual,v=k=>ann.map(a=>a[k]),solar=v('solar'),longest=good(v('dry_spell'));
  $('risk-cards').innerHTML=card('Reference chill',median(v('chill_hours')),'hours','Median reference-winter chill · 0–7.2°C',v('chill_hours'),1)+card('Cold exposure',mean(v('cold_days')),'days/yr','Mean days with minimum temperature <0°C',v('cold_days'),2)+card('Rainfall',mean(v('rain_mm')),'mm/yr','Mean annual total, not harvest rainfall',v('rain_mm'),3)+card('Heat exposure',mean(v('hot_days')),'days/yr','Mean days with maximum temperature ≥35°C',v('hot_days'),4)+card('Dry weather',longest.length?Math.max(...longest):null,'days','Longest within-year dry run · rain <1 mm',v('dry_spell'),5)+card('Radiation',mean(solar),'MJ/m²/day','Mean annual daily shortwave energy',solar,6);
  $('availability').innerHTML=`<span>Daily archive · ${r.provenance.rows} rows</span><span>Hourly source · ${r.hourly_source?`${r.hourly_source.source_lat}, ${r.hourly_source.source_lon} · ${fmt(r.hourly_source.distance_km)} km from pin · ${esc(r.hourly_source.site)}`:'Not exposed for this coordinate'}</span><span>Soil · ${r.soil?.length??0} records; no nearby-site substitution</span><span>Meteorology source cell · ${fmt(r.provenance.sources?.[0]?.distance_km)} km from pin</span>`;
  $('annual-table').innerHTML='<table><thead><tr>'+['Year','Chill h','Cold days','Rain mm','Hot days','Dry spell days','Solar MJ/m²/day'].map(h=>`<th>${h}</th>`).join('')+'</tr></thead><tbody>'+ann.map(a=>'<tr>'+['year','chill_hours','cold_days','rain_mm','hot_days','dry_spell','solar'].map(k=>`<td>${fmt(a[k])}</td>`).join('')+'</tr>').join('')+'</tbody></table>';
  $('summary').innerHTML=`<h3>Weather evidence, not a suitability verdict</h3><p>${esc(r.site.name)} has ${fmt(mean(v('rain_mm')))} mm mean annual rainfall across ${good(v('rain_mm')).length} usable years. The longest within-year dry spell is ${fmt(longest.length?Math.max(...longest):null)} days. These are weather exposures, not irrigation need or yield loss.</p><p>Outdoor values remain unchanged across growing setups. Tunnel effects, soil drainage, cultivar suitability and modelled stage dates have not been calibrated.</p><p>Station comparisons show missed cold events in the grid data. Zero recorded cold days is not proof of frost safety. ${r.provenance.screening?.precip_suspect_days?`${r.provenance.screening.precip_suspect_days} suspect rainfall days affect this point; dependent windows are excluded.`:''}</p>`;
  $('provenance').innerHTML=`<p>Method: ${esc(r.method_version)} · Baseline 2011–2025 · UTC. Analysis ID: ${esc(r.analysis_id??'saved-snapshot')}.</p><p>Meteorology: 0.5° × 0.625°; solar: 1° × 1°. Each variable retains its source grid. Shared weather cells do not resolve parcel differences. Values are uncorrected gridded estimates.</p><p><a href="https://power.larc.nasa.gov/docs/services/aws/" target="_blank" rel="noreferrer">NASA POWER source</a> · <a href="https://docs.isric.org/globaldata/soilgrids/" target="_blank" rel="noreferrer">SoilGrids source</a></p><pre>${esc(JSON.stringify(r.provenance.sources,null,2))}</pre>`;
  management();showView('overview');charts();locationMap?.setEvidence(r);
  $('status').textContent=`Assessment ready for ${r.site.name}. Historical evidence, not a forecast.`;
  updateDraftNotice();
}
function samePoint(a,b){return a&&b&&Math.abs(a.lat-b.lat)<1e-7&&Math.abs(a.lon-b.lon)<1e-7}
function updateDraftNotice(){
  const changed=active&&!samePoint(draft,active.site);
  $('draft-notice').hidden=!changed;
  if(changed)$('draft-notice').textContent=`A new pin is selected. The assessment below still belongs to ${active.site.name} (${active.site.lat.toFixed(4)}, ${active.site.lon.toFixed(4)}). Choose Analyze location to replace it.`;
}
function setBusy(busy){
  $('analyze').disabled=busy;$('cancel-analysis').hidden=!busy;
  $('location-form').setAttribute('aria-busy',String(busy));
}
function cancelRequest(){
  if(!pendingRequest)return;
  serial++;pendingRequest.abort();pendingRequest=null;setBusy(false);
  $('results').hidden=!active;
  $('status').textContent='Request cancelled. The previous assessment, if shown, is unchanged.';
}
function selectLocation(lat,lon,name='Selected point',{recenter=true}={}){
  cancelRequest();
  draft={lat,lon,name};$('latitude').value=lat;$('longitude').value=lon;
  $('selection-label').textContent=`${name}${catalog[name]?' · saved location':' · not yet analyzed'}`;
  locationMap?.setSelection(lat,lon,{label:name,recenter});
  document.querySelectorAll('[data-site]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.site===name)));
  $('error').hidden=true;updateDraftNotice();
}
function selectSaved(name){
  const entry=catalog[name];if(!entry)return;
  selectLocation(entry.site.lat,entry.site.lon,name);
  $('status').textContent=`${name} selected. Choose Analyze location to open its saved evidence.`;
}
async function loadSaved(entry,signal){
  if(entry.annual)return entry;
  const res=await fetch(entry.file,{signal});
  if(!res.ok)throw Error('Saved evidence could not load. Check the local snapshot files or choose another saved location.');
  const full=await res.json();catalog[full.site.name]={...full,group:entry.group};
  return catalog[full.site.name];
}
async function analyze(lat,lon,{recenter=true,focusResult=true}={}){
  if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180){
    $('error').textContent='Enter a latitude from −90 to 90 and longitude from −180 to 180.';$('error').hidden=false;return;
  }
  cancelRequest();
  const request=++serial,controller=new AbortController();pendingRequest=controller;
  const saved=Object.values(catalog).find(r=>samePoint(r.site,{lat,lon}));
  draft={lat,lon,name:saved?.site.name??'Selected point'};
  locationMap?.setSelection(lat,lon,{label:draft.name,recenter});
  $('latitude').value=lat;$('longitude').value=lon;
  $('error').hidden=true;$('draft-notice').hidden=true;$('results').hidden=true;
  $('status').textContent=saved?'Opening saved location evidence…':'Reading the private historical archive. No new weather download is requested.';
  setBusy(true);
  const timer=setTimeout(()=>controller.abort(),90000);
  try{
    let result;
    if(saved)result=await loadSaved(saved,controller.signal);
    else{
      const res=await fetch(`/api/analysis?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}`,{signal:controller.signal});
      const body=await res.json();
      if(!res.ok)throw Error(res.status===503?'The private archive is disconnected. Saved locations still work; reconnect the local archive tunnel to analyze other coordinates.':res.status===429?'The archive is processing another request. Wait for it to finish, then analyze again.':body.error??'The archive could not return an assessment. No result was substituted.');
      if(body.error)throw Error(body.error);
      result=body;
    }
    if(request!==serial)return;
    resultOrigin=saved?'Saved location assessment':'Connected archive assessment';
    render(result);
    $('selection-label').textContent=`${result.site.name} · assessment loaded`;
    if(focusResult){
      $('location-name').focus({preventScroll:true});
      $('results').scrollIntoView({block:'start',behavior:'instant'});
    }
    return {location:result.site.name,status:'ready'};
  }catch(e){
    if(request===serial){
      $('error').textContent=e.name==='AbortError'?'Analysis timed out. No result was substituted. Saved locations remain available.':e.message;
      $('error').hidden=false;$('status').textContent='No new assessment returned for the selected coordinate.';
      $('results').hidden=!active;updateDraftNotice();
    }
  }finally{
    clearTimeout(timer);
    if(request===serial){pendingRequest=null;setBusy(false)}
  }
}
function presets(){
  const query=$('site-search').value.trim().toLowerCase();
  const entries=Object.values(catalog).filter(r=>[r.site.name,r.site.region,r.site.county,r.group].filter(Boolean).join(' ').toLowerCase().includes(query));
  const groups=['Reference','Georgia','Central Florida','South Florida'];
  $('presets').innerHTML=groups.map(g=>{
    const rows=entries.filter(r=>(r.group??'Reference')===g);
    return rows.length?`<div class="preset-group"><span class="preset-group-title">${g}</span>${rows.map(r=>`<button class="preset-option" type="button" data-site="${esc(r.site.name)}" aria-pressed="${draft.name===r.site.name}"><span>${esc(r.site.name)}</span><small>${esc(r.site.county??r.site.region??'Saved')}</small></button>`).join('')}</div>`:'';
  }).join('')||'<p class="small">No saved locations match. Use the map or coordinates for other places.</p>';
  $('preset-count').textContent=`${entries.length} of ${Object.keys(catalog).length} saved locations`;
}
$('site-search').addEventListener('input',presets);
$('presets').addEventListener('click',e=>{const b=e.target.closest('[data-site]');if(b)selectSaved(b.dataset.site)});
for(const id of ['latitude','longitude'])$(id).addEventListener('input',()=>{
  cancelRequest();
  const lat=$('latitude').valueAsNumber,lon=$('longitude').valueAsNumber;
  draft={lat,lon,name:'Entered coordinates'};
  if(Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=90&&Math.abs(lon)<=180)locationMap?.setSelection(lat,lon,{label:'Entered coordinates',recenter:false});
  $('selection-label').textContent='Coordinates changed · analyze to update evidence';updateDraftNotice();
});
$('location-form').addEventListener('submit',e=>{e.preventDefault();analyze($('latitude').valueAsNumber,$('longitude').valueAsNumber)});
$('cancel-analysis').onclick=cancelRequest;
$('change-location').onclick=()=>{
  $('latitude').focus({preventScroll:true});
  document.querySelector('.explorer').scrollIntoView({block:'start',behavior:'instant'});
};
$('system').onchange=management;$('monthly-metric').onchange=charts;$('annual-metric').onchange=charts;
document.querySelector('.view-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-view]');if(b)showView(b.dataset.view)});
document.querySelector('.view-tabs').addEventListener('keydown',e=>{
  const tabs=[...document.querySelectorAll('[data-view]')],index=tabs.indexOf(document.activeElement);
  if(index<0||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
  e.preventDefault();
  const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(index+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
  showView(tabs[next].dataset.view);tabs[next].focus();
});
$('results').addEventListener('click',e=>{
  const tab=e.target.closest('[data-open-view]'),stage=e.target.closest('[data-explore-stage]');
  if(tab)showView(tab.dataset.openView,true);
  if(stage){showView('season',true);CycleView.select?.($('production-content'),stage.dataset.exploreStage)}
});
let resize;window.addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(()=>{if(currentView==='climate')charts();locationMap?.resize()},100)});
function download(content,type,name){
  const u=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');
  a.href=u;a.download=name;a.hidden=true;document.body.append(a);a.click();
  setTimeout(()=>{a.remove();URL.revokeObjectURL(u)},1000);
}
$('export-json').onclick=()=>{
  if(!active)return;
  const view=document.querySelector('.cycle-panel')?.dataset;
  download(JSON.stringify({...active,management:systems[$('system').value][0],management_evidence:'qualitative only',
    cycle_view:view?.winter?{winter:view.winter,stage:view.stage}:null},null,2),'application/json','blueberry-assessment.json');
};
$('export').onclick=async()=>{
  if(!active)return;
  const button=$('export'),snapshot=active,system=systems[$('system').value][0];
  // Render hidden climate charts at their real width before cloning the immutable report.
  const previous=currentView;showView('climate');charts();
  const content=$('results').cloneNode(true);showView(previous);
  content.querySelectorAll('.actions,.view-tabs,.cycle-stage-controls,[data-open-view],[data-explore-stage]').forEach(n=>n.remove());
  content.querySelector('.cycle-panel')?.classList.add('is-snapshot');
  content.querySelectorAll('.view-panel').forEach(p=>{
    p.hidden=false;p.removeAttribute('role');p.removeAttribute('aria-labelledby');p.removeAttribute('tabindex');
  });
  const intro=content.querySelector('.cycle-header p');if(intro)intro.textContent='Saved cycle selection. Full definitions and evidence tables follow.';
  content.querySelectorAll('select').forEach(s=>{
    const label=document.createElement('span');label.textContent=$(s.id)?.selectedOptions[0]?.text??'';s.replaceWith(label);
  });
  content.querySelectorAll('details').forEach(d=>d.open=true);
  button.disabled=true;
  try{
    const styles=await Promise.all(['style.css','cycle.css'].map(async path=>{
      const res=await fetch(path);if(!res.ok)throw Error('Report styles could not load. No incomplete report was saved.');return res.text();
    }));
    download(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(snapshot.site.name)} | Blueberry assessment</title><style>${styles.join('\n')}</style></head><body class="export-document"><main><p class="stamp export-heading">Historical baseline 2011–2025 · ${esc(system)} · ${esc(snapshot.analysis_id??'saved-snapshot')}</p>${content.outerHTML}</main></body></html>`,'text/html','blueberry-assessment.html');
  }catch(e){$('error').textContent=e.message;$('error').hidden=false}
  finally{button.disabled=false}
};
async function initialize(){
  try{
    const res=await fetch('snapshots.json');if(!res.ok)throw Error('Saved location index could not load.');
    catalog=(await res.json()).sites;presets();
  }catch(e){$('error').textContent=e.message;$('error').hidden=false}
  if(typeof LocationMap!=='undefined'){
    locationMap=LocationMap.mount('location-map',{sites:Object.values(catalog),
      onSelect:({lat,lon})=>selectLocation(lat,lon,'Map pin',{recenter:false}),onPreset:selectSaved});
    locationMap.setSelection(draft.lat,draft.lon,{label:draft.name,recenter:false});
  }else $('location-map').innerHTML='<p class="notice">The map could not load. Coordinate entry and saved locations still work.</p>';
  if(catalog.Papanduva)await analyze(draft.lat,draft.lon,{recenter:false,focusResult:false});
}
initialize();
$('connection').textContent='Saved locations · archive not connected';
if(['127.0.0.1','localhost'].includes(location.hostname)){
  fetch('/api/health').then(r=>r.ok?r.json():null).then(r=>{
    if(r?.status==='ready')$('connection').textContent='Private archive connected';
  }).catch(()=>{});
}
if(document.modelContext?.registerTool){
  Promise.resolve(document.modelContext.registerTool({name:'analyze_blueberry_location',
    description:'Select and analyze a coordinate in the visible historical climate workspace. No weather download is triggered.',
    inputSchema:{type:'object',properties:{latitude:{type:'number'},longitude:{type:'number'}},required:['latitude','longitude'],additionalProperties:false},
    annotations:{readOnlyHint:false},execute:async({latitude,longitude})=>{
      if(!Number.isFinite(latitude)||!Number.isFinite(longitude)||Math.abs(latitude)>90||Math.abs(longitude)>180)throw Error('Numeric coordinates within latitude/longitude bounds required');
      selectLocation(latitude,longitude);return analyze(latitude,longitude);
    }})).catch(()=>{});
}
