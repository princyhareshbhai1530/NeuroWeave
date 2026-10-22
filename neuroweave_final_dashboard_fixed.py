from pathlib import Path
import base64
import json
import mimetypes
import altair as alt
import pandas as pd
import streamlit as st

BASE = Path('results/combined_participants_3_to_9')
OUTPUTS = Path('outputs')
FULL_COHORT = list(range(1, 19))
VALIDATED = list(range(3, 10))

st.set_page_config(page_title='NEUROWEAVE', page_icon='🧠', layout='wide', initial_sidebar_state='expanded')


def inject_background_video():
    """Embed the local neural video behind the Streamlit interface."""
    candidates = [
        Path('assets/AdobeStock_480629528.mp4'),
        Path('assets/AdobeStock_480629528.mov'),
        Path('assets/AdobeStock_480629528.MOV'),
    ]
    video_path = next((path for path in candidates if path.exists()), None)
    if video_path is None:
        return False

    mime_type = mimetypes.guess_type(video_path.name)[0]
    if not mime_type:
        mime_type = 'video/mp4' if video_path.suffix.lower() == '.mp4' else 'video/quicktime'

    encoded = base64.b64encode(video_path.read_bytes()).decode('ascii')
    video_html = (
        '<div id="nw-video-layer" aria-hidden="true">'
        '<video id="nw-bg-video" autoplay muted loop playsinline preload="auto">'
        f'<source src="data:{mime_type};base64,{encoded}" type="{mime_type}">'
        '</video><div id="nw-video-overlay"></div></div>'
    )
    st.markdown(video_html, unsafe_allow_html=True)
    return True


BACKGROUND_VIDEO_LOADED = inject_background_video()

st.markdown('''
<style>
:root{--cyan:#66e3ff;--violet:#9b7bff;--teal:#36d6b4;--orange:#ff9f68;--ink:#eaf4ff;--muted:#93a7bb;--panel:#0d1b2a;}
.stApp{background:transparent!important;color:#eaf4ff;position:relative!important;z-index:10!important}
html,body{background:#050b14!important}
#nw-video-layer{position:fixed!important;inset:0!important;z-index:0!important;overflow:hidden!important;pointer-events:none!important;background:#050b14!important}
#nw-bg-video{position:absolute!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:0!important;object-fit:cover!important;object-position:center center!important;filter:saturate(.78) contrast(1.08) brightness(.62);transform:scale(1.015);pointer-events:none!important}
#nw-video-overlay{position:absolute!important;inset:0!important;z-index:1!important;background:radial-gradient(circle at 20% 8%,rgba(20,72,103,.22),rgba(3,10,18,.68) 42%,rgba(3,8,15,.84) 100%)!important;backdrop-filter:blur(1px);pointer-events:none!important}
[data-testid="stAppViewContainer"]{background:transparent!important;position:relative!important;z-index:10!important}
[data-testid="stMain"]{position:relative!important;z-index:12!important;background:transparent!important}
[data-testid="stMainBlockContainer"]{position:relative!important;z-index:13!important}
[data-testid="stSidebar"]{position:relative!important;z-index:20!important}
[data-testid="stToolbar"]{position:relative!important;z-index:30!important}
[data-testid="stHeader"]{background:rgba(5,11,20,.35);backdrop-filter:blur(10px)}
[data-testid="stSidebar"]{background:rgba(5,15,26,.88);backdrop-filter:blur(18px);border-right:1px solid #24465d}
.block-container{padding-top:1.5rem;max-width:1500px;position:relative;z-index:15}
h1,h2,h3{color:#f4f9ff;letter-spacing:-.02em}
p,li,label,[data-testid="stCaptionContainer"]{color:#b9c9d8!important}
.nw-hero{padding:24px 28px;border:1px solid #1e4762;border-radius:22px;background:linear-gradient(135deg,rgba(18,50,73,.78),rgba(8,18,31,.84));backdrop-filter:blur(14px);box-shadow:0 20px 60px rgba(0,0,0,.28);margin-bottom:18px}
.nw-kicker{color:#66e3ff;font-size:.78rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.nw-title{font-size:3rem;font-weight:850;line-height:1;margin:.4rem 0 .8rem;color:#f7fbff}
.nw-sub{font-size:1.08rem;max-width:900px;color:#b5c7d9}
.nw-flow{display:flex;gap:9px;flex-wrap:wrap;margin-top:18px}.nw-step{background:#0a1725;border:1px solid #1e4059;border-radius:999px;padding:7px 12px;color:#c8d7e5;font-size:.82rem}.nw-step b{color:#66e3ff}
.nw-card{border:1px solid #173a52;background:linear-gradient(180deg,rgba(14,31,47,.82),rgba(8,19,31,.86));backdrop-filter:blur(12px);border-radius:18px;padding:18px;min-height:132px;box-shadow:0 8px 26px rgba(0,0,0,.18)}
.nw-label{color:#7f99ae;font-size:.74rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.nw-big{color:#fff;font-size:1.75rem;font-weight:820;margin:.35rem 0}.nw-small{color:#9fb3c5;font-size:.86rem}
.verdict{border-left:4px solid #36d6b4;background:linear-gradient(90deg,rgba(54,214,180,.12),rgba(11,27,43,.3));padding:18px 20px;border-radius:12px;margin:10px 0 20px}
.guard{border-left:4px solid #ff9f68;background:rgba(255,159,104,.08);padding:14px 18px;border-radius:10px}
[data-testid="stMetric"]{background:rgba(12,27,42,.82);backdrop-filter:blur(10px);border:1px solid #24465d;padding:14px;border-radius:16px}[data-testid="stMetricLabel"]{color:#86a2b7}[data-testid="stMetricValue"]{color:#f5fbff}
.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{background:#0a1725;border:1px solid #173a52;border-radius:12px;padding:8px 16px}.stTabs [aria-selected="true"]{border-color:#66e3ff!important;color:#66e3ff!important}
[data-testid="stDataFrame"]{border:1px solid #173a52;border-radius:14px;overflow:hidden}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    req = {
        'evidence': BASE/'evidence_classification.json',
        'paired': BASE/'paired_future_session_comparisons.csv',
        'participants': BASE/'participant_summary.csv',
        'overall': BASE/'overall_summary.csv',
        'robust': BASE/'statistical_robustness_summary.json',
        'loo': BASE/'leave_one_participant_out.csv',
    }
    missing=[str(p) for p in req.values() if not p.exists()]
    if missing: raise FileNotFoundError('Missing required validated outputs:\n'+'\n'.join(missing))
    return (json.loads(req['evidence'].read_text()), pd.read_csv(req['paired']), pd.read_csv(req['participants']),
            pd.read_csv(req['overall']).iloc[0], json.loads(req['robust'].read_text()), pd.read_csv(req['loo']))

def prepared_participants():
    found=[]
    for p in FULL_COHORT:
        if (OUTPUTS/f'participant_{p:02d}_X.npy').exists() and (OUTPUTS/f'participant_{p:02d}_y.npy').exists(): found.append(p)
    return found

def pct(x): return f'{100*float(x):.1f}%'

def style_chart(chart):
    return chart.configure_view(strokeOpacity=0).configure_axis(gridColor='#173047',domainColor='#355067',tickColor='#355067',labelColor='#9eb2c4',titleColor='#bcd0df').configure_legend(labelColor='#bcd0df',titleColor='#e8f2fa')

def hero():
    st.markdown('''<div class="nw-hero"><div class="nw-kicker">Longitudinal BCI investigation</div><div class="nw-title">NEUROWEAVE</div><div class="nw-sub">When BCI performance changes across sessions, NeuroWeave asks what changed: the decoder, the recorded signal environment, or evidence we still cannot separate.</div><div class="nw-flow"><span class="nw-step"><b>01</b> Select cohort</span><span class="nw-step"><b>02</b> Inspect participant</span><span class="nw-step"><b>03</b> Compare sessions</span><span class="nw-step"><b>04</b> Weigh evidence</span><span class="nw-step"><b>05</b> Issue verdict</span><span class="nw-step"><b>06</b> Recommend next measurement</span></div></div>''',unsafe_allow_html=True)

def cohort_controls(paired):
    prepared=prepared_participants()
    st.sidebar.markdown('## Investigation controls')
    if BACKGROUND_VIDEO_LOADED:
        st.sidebar.caption('◉ Neural background: AdobeStock_480629528')
    else:
        st.sidebar.warning('Background video not found in assets/.')
    cohort=st.sidebar.radio('Cohort', ['Full dataset · 18 participants','Validated evidence · P3–P9','Prepared locally'], index=1)
    if cohort.startswith('Full'): selectable=FULL_COHORT
    elif cohort.startswith('Validated'): selectable=VALIDATED
    else: selectable=prepared or FULL_COHORT
    participant=st.sidebar.selectbox('Participant', ['Cohort overview']+selectable)
    st.sidebar.caption('Full cohort = dataset scope. Validated cohort = participants currently included in the P3–P9 inferential result.')
    st.sidebar.markdown('---')
    st.sidebar.markdown(f'**Dataset coverage**  {len(FULL_COHORT)}/18')
    st.sidebar.markdown(f'**Prepared locally**  {len(prepared)}/18')
    st.sidebar.markdown(f'**Validated evidence**  {paired.participant.nunique()}/18')
    return cohort,participant,prepared

def cohort_map(participants, prepared):
    rows=[]
    validated=set(participants.participant.astype(int))
    for p in FULL_COHORT:
        status='Validated evidence' if p in validated else ('Prepared locally' if p in prepared else 'Dataset only')
        rows.append({'Participant':str(p),'Status':status})
    df=pd.DataFrame(rows)
    chart=alt.Chart(df).mark_circle(size=620,stroke='#dff7ff',strokeWidth=.7).encode(
        x=alt.X('Participant:N',sort=[str(i) for i in FULL_COHORT],axis=alt.Axis(labelAngle=0)),
        color=alt.Color('Status:N',scale=alt.Scale(domain=['Validated evidence','Prepared locally','Dataset only'],range=['#36d6b4','#9b7bff','#29445a'])),
        tooltip=['Participant:N','Status:N']).properties(height=125)
    st.altair_chart(style_chart(chart),width='stretch')

def overview(evidence,paired,participants,overall,prepared,cohort,selected):
    st.markdown('## Investigation command center')
    cohort_map(participants,prepared)
    ci=evidence['primary_result']['clustered_bootstrap_95_ci']
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric('Full dataset','18 participants')
    c2.metric('Validated cohort','7 participants')
    c3.metric('Future-session tests',int(overall.future_session_comparisons))
    c4.metric('Frozen → adaptive',f"{pct(overall.mean_frozen_balanced_accuracy)} → {pct(overall.mean_adaptive_balanced_accuracy)}")
    c5.metric('Mean adaptation gain',f"+{100*overall.mean_adaptation_gain:.1f} pp")
    st.markdown(f'''<div class="verdict"><div class="nw-label">Current cohort verdict · moderate support</div><div class="nw-big">Decoder adaptation helps on average, but not universally.</div><div class="nw-small">Validated P3–P9 evidence: clustered 95% CI for mean gain {ci[0]:+.3f} to {ci[1]:+.3f}. Six of seven participants improved on average. This is a studied-sample result, not a neuroplasticity claim.</div></div>''',unsafe_allow_html=True)
    if selected!='Cohort overview' and int(selected) not in set(participants.participant.astype(int)):
        st.info(f'Participant {selected} is part of the full dataset scope but is not in the current P3–P9 validated inferential cohort. NeuroWeave will not fabricate a verdict for this participant.')
    comp=participants[['participant','mean_frozen','mean_adaptive']].melt(id_vars='participant',var_name='Model',value_name='Balanced accuracy')
    comp['Model']=comp['Model'].map({'mean_frozen':'Frozen Session-0','mean_adaptive':'Cumulative adaptive'})
    comp['participant']=comp['participant'].astype(str)
    bars=alt.Chart(comp).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(x=alt.X('participant:N',sort=[str(i) for i in VALIDATED],title='Validated participant'),xOffset='Model:N',y=alt.Y('Balanced accuracy:Q',scale=alt.Scale(domain=[0,1])),color=alt.Color('Model:N',scale=alt.Scale(range=['#3a86c8','#66e3ff'])),tooltip=['participant:N','Model:N',alt.Tooltip('Balanced accuracy:Q',format='.3f')]).properties(height=340)
    chance=alt.Chart(pd.DataFrame({'chance':[.5]})).mark_rule(color='#ffb86b',strokeDash=[5,5]).encode(y='chance:Q')
    st.altair_chart(style_chart(bars+chance),width='stretch')

def participant_investigation(paired,participants,selected):
    valid=sorted(paired.participant.unique())
    p=valid[0] if selected=='Cohort overview' or selected not in valid else selected
    p=st.selectbox('Validated participant to investigate',valid,index=valid.index(p),key='investigation_participant')
    sub=paired[paired.participant==p].copy(); sub['session']=sub['session'].astype(int); sub=sub.sort_values('session')
    summary=participants[participants.participant==p].iloc[0]
    st.markdown(f'## Participant {p} · longitudinal investigation')
    a,b,c,d=st.columns(4)
    a.metric('Frozen mean',pct(summary.mean_frozen)); b.metric('Adaptive mean',pct(summary.mean_adaptive),delta=f'{100*summary.mean_gain:+.1f} pp'); c.metric('Positive sessions',f'{int(summary.positive_gains)}/5'); d.metric('Negative sessions',int(summary.negative_gains))
    long=sub.melt(id_vars='session',value_vars=['frozen_balanced_accuracy','adaptive_balanced_accuracy'],var_name='Decoder',value_name='Balanced accuracy'); long['Decoder']=long.Decoder.map({'frozen_balanced_accuracy':'Frozen','adaptive_balanced_accuracy':'Adaptive'})
    line=alt.Chart(long).mark_line(point=alt.OverlayMarkDef(size=90),strokeWidth=3).encode(x=alt.X('session:O',title='Future session'),y=alt.Y('Balanced accuracy:Q',scale=alt.Scale(domain=[0,1])),color=alt.Color('Decoder:N',scale=alt.Scale(range=['#4c8dca','#66e3ff'])),tooltip=['session:O','Decoder:N',alt.Tooltip('Balanced accuracy:Q',format='.3f')]).properties(height=320)
    st.altair_chart(style_chart(line),width='stretch')
    gain=alt.Chart(sub).mark_bar(cornerRadiusTopLeft=5,cornerRadiusTopRight=5).encode(x=alt.X('session:O',title='Future session'),y=alt.Y('adaptation_gain:Q',title='Adaptive − frozen'),color=alt.condition('datum.adaptation_gain >= 0',alt.value('#36d6b4'),alt.value('#ff7b68')),tooltip=['session:O',alt.Tooltip('adaptation_gain:Q',format='+.3f')]).properties(height=230)
    st.altair_chart(style_chart(gain),width='stretch')
    best=sub.loc[sub.adaptation_gain.idxmax()]; worst=sub.loc[sub.adaptation_gain.idxmin()]
    x,y=st.columns(2)
    x.markdown(f'''<div class="nw-card"><div class="nw-label">Strongest adaptation evidence</div><div class="nw-big">Session {int(best.session)} · {best.adaptation_gain:+.3f}</div><div class="nw-small">Largest observed adaptive minus frozen balanced-accuracy gain for this participant.</div></div>''',unsafe_allow_html=True)
    y.markdown(f'''<div class="nw-card"><div class="nw-label">Strongest counterexample</div><div class="nw-big">Session {int(worst.session)} · {worst.adaptation_gain:+.3f}</div><div class="nw-small">Largest observed session-level challenge to a universal adaptation-benefit claim.</div></div>''',unsafe_allow_html=True)

def evidence_lab(evidence,robust,loo,participants):
    st.markdown('## Evidence lab → verdict')
    p=evidence['primary_result']; ci=p['clustered_bootstrap_95_ci']
    cards=[('Effect size',f"+{100*p['mean_adaptation_gain']:.1f} pp",'Average adaptive gain'),('Bootstrap interval',f'{ci[0]:+.3f} → {ci[1]:+.3f}','Participant-clustered 95% CI'),('Wilcoxon',f"p = {p['wilcoxon_p_two_sided']:.5f}",'Supports positive participant-level shift'),('Sign test',f"p = {p['sign_test_p_two_sided']:.3f}",'Does not reach 0.05')]
    cols=st.columns(4)
    for col,(lab,big,small) in zip(cols,cards): col.markdown(f'<div class="nw-card"><div class="nw-label">{lab}</div><div class="nw-big">{big}</div><div class="nw-small">{small}</div></div>',unsafe_allow_html=True)
    st.markdown('### Competing explanations')
    h1,h2,h3=st.columns(3)
    h1.markdown('<div class="nw-card"><div class="nw-label">Hypothesis A</div><div class="nw-big">⚙ Decoder adaptation</div><div class="nw-small">Moderately supported in the validated sample because mean gain is positive and robust to participant removal.</div></div>',unsafe_allow_html=True)
    h2.markdown('<div class="nw-card"><div class="nw-label">Hypothesis B</div><div class="nw-big">📡 Session / interface shift</div><div class="nw-small">Still plausible. Current signal-shift measurements do not identify the physical cause of change.</div></div>',unsafe_allow_html=True)
    h3.markdown('<div class="nw-card"><div class="nw-label">Hypothesis C</div><div class="nw-big">🧠 Neural change</div><div class="nw-small">Unresolved. Current evidence cannot establish neuroplasticity or causal neural adaptation.</div></div>',unsafe_allow_html=True)
    st.markdown(f'''<div class="verdict"><div class="nw-label">NeuroWeave verdict</div><div class="nw-big">{evidence['support_level'].title()} support for adaptation benefit</div><div class="nw-small">{evidence['supported_conclusion']}</div></div>''',unsafe_allow_html=True)
    st.markdown('<div class="guard"><b>Scientific guardrail</b><br>This result does not establish neuroplasticity, universal benefit, the physical cause of drift, or population-level generalization.</div>',unsafe_allow_html=True)
    st.markdown('### What should we measure next?'); st.success(evidence['recommended_next_measurement'])

def coverage(prepared,participants):
    st.markdown('## Full cohort coverage')
    st.write('The dataset contains 18 participants. NeuroWeave separates dataset scope from validated evidence so the interface can show the full cohort without overstating which participants support the current verdict.')
    validated=set(participants.participant.astype(int)); rows=[]
    for p in FULL_COHORT:
        rows.append({'Participant':p,'Dataset':'Included','Prepared locally':'Yes' if p in prepared else 'No','Current validated inference':'Yes' if p in validated else 'No'})
    st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch',height=430)
    st.caption('To expand the inferential cohort beyond P3–P9, run the same frozen/adaptive/session-aware evaluation and participant-level robustness analysis before marking additional participants as validated.')

def methods():
    st.markdown('## Methods & scientific boundaries')
    st.markdown('''**Dataset scope:** Kumar2024, 18 participants, 6 sessions.  
**Validated analysis shown here:** participants 3–9, 35 future-session comparisons.  
**Preprocessing:** 8–30 Hz, 0–5 s windows, 128 Hz, 22 EEG channels.  
**Frozen baseline:** Session-0 trained model tested on later sessions.  
**Adaptive model:** cumulative prior-session retraining, never trained on the session currently being tested.  
**Inference:** participant-clustered bootstrap, participant-level Wilcoxon/sign tests, leave-one-participant-out sensitivity.''')
    st.warning('NeuroWeave is a research prototype and does not diagnose neurological conditions or establish neuroplasticity.')

def main():
    try: evidence,paired,participants,overall,robust,loo=load_data()
    except Exception as e: st.error(str(e)); st.stop()
    hero(); cohort,selected,prepared=cohort_controls(paired)
    tabs=st.tabs(['🧭 Investigation','👤 Participant','⚖ Evidence → Verdict','◉ Cohort coverage','🔬 Methods'])
    with tabs[0]: overview(evidence,paired,participants,overall,prepared,cohort,selected)
    with tabs[1]: participant_investigation(paired,participants,selected)
    with tabs[2]: evidence_lab(evidence,robust,loo,participants)
    with tabs[3]: coverage(prepared,participants)
    with tabs[4]: methods()

if __name__=='__main__': main()
