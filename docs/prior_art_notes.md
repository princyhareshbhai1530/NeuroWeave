# NEUROWEAVE Prior-Art Research Notebook

## Research questions

1. How do longitudinal BCI studies distinguish user learning from decoder adaptation?
2. What recording variations commonly affect EEG across sessions?
3. What evidence can support neural adaptation without claiming direct proof of neuroplasticity?
4. Which follow-up measurements could separate neural change from electrode or session drift?
5. How should uncertainty and participant heterogeneity be represented in longitudinal BCI analysis?

## Source 1: Co-adaptive training in a multi-day motor-imagery BCI

**Title:** Co-adaptive Training Improves Efficacy of a Multi-Day EEG-Based Motor Imagery BCI Training  
**Link:** https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2019.00362/full  
**Source type:** Peer-reviewed paper

### Scientific question

Does regularly adapting the decoder improve performance during multi-day motor-imagery BCI training compared with keeping the original decoder fixed?

### Dataset and method

The study examined EEG recordings from 18 participants completing a four-day motor-imagery experiment. A fixed-classifier group was compared with an adaptive-classifier group, including within-day and between-day performance changes.

### Main finding

The adaptive group showed a larger performance change after training, while between-day deterioration remained an important challenge.

### Limitation

Performance is influenced by both the participant and the decoder. Improved accuracy with an adaptive classifier does not, by itself, prove neural adaptation.

### Relevance to NeuroWeave

NeuroWeave should compare an unchanged initial-session decoder against a causal adaptive decoder. If improvement appears only after model updating, decoder adaptation is better supported than a neural explanation.

## Source 2: Intra- and inter-subject EEG variability

**Title:** Intra- and Inter-subject Variability in EEG-Based Sensorimotor Brain Computer Interface: A Review  
**Link:** https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2019.00087/full  
**Source type:** Peer-reviewed review paper

### Scientific question

How do within-participant and between-participant differences affect EEG-based sensorimotor BCI performance?

### Main finding

Sensorimotor EEG activity varies over time and across participants. This variability changes feature distributions and can prevent a decoder trained on one session from transferring reliably to another.

### Limitation

The review identifies multiple sources of variability but cannot determine the cause of a specific session-level performance change.

### Relevance to NeuroWeave

Cross-session change must be treated as distribution shift. Frozen-decoder deterioration cannot be attributed to neural adaptation without evaluating recording quality and session effects.

## Source 3: EEG electrode-position variability

**Title:** Variability of EEG Electrode Positions and Their Underlying Brain Regions  
**Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC8865144/  
**Source type:** Peer-reviewed paper

### Scientific question

How much can EEG electrode positions and underlying recorded regions vary even with a fixed cap?

### Dataset and method

The study used simultaneous EEG-fMRI data from 20 participants to locate electrodes and map the brain regions beneath them.

### Main finding

Electrode positions and underlying brain regions varied across participants even when a fixed cap was used.

### Limitation

The study focused on between-participant differences rather than repeated motor-imagery sessions from the same participant.

### Relevance to NeuroWeave

Cap placement is a plausible source of recording drift. NeuroWeave cannot state that placement caused a specific change without position metadata.

## Source 4: Electrode impedance and repeated use

**Title:** The Dependence of Electrode Impedance on the Number of Performed EEG Examinations  
**Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6603518/  
**Source type:** Peer-reviewed paper

### Scientific question

Does repeated use of reusable EEG electrodes affect impedance and recording reliability?

### Main finding

Electrode impedance varied, including among new electrodes, and electrode condition changed with repeated use.

### Limitation

The study examined electrode properties rather than motor-imagery performance or longitudinal neural adaptation.

### Relevance to NeuroWeave

Impedance or contact quality should be measured in every session when possible. Without these data, impedance cannot be named as the cause of a performance change.

## Source 5: Long-term BCI user learning

**Title:** Neural Correlates of User Learning During Long-Term BCI Training for the Cybathlon Competition  
**Link:** https://link.springer.com/article/10.1186/s12984-022-01047-x  
**Source type:** Peer-reviewed paper

### Scientific question

Which behavioural and EEG-pattern changes can help track user learning during long-term BCI training?

### Dataset and method

The study followed one experienced BCI user over an extended training period and combined performance measures with neural-pattern analyses while decoder recalibration occurred infrequently.

### Main finding

Performance and within-class neural patterns changed over time, including evidence related to BCI-skill acquisition and stabilization.

### Limitation

The study examined one highly trained user in a specialized setting, limiting generalization.

### Relevance to NeuroWeave

Task-pattern consistency should be examined in addition to accuracy. Improvement under a stable decoder can support a neural-adaptation interpretation, but it does not directly prove neuroplasticity.

## Source 6: Kumar2024 longitudinal motor-imagery dataset

**Title:** Multi-Session Longitudinal Motor Imagery EEG Dataset  
**Link:** https://nemar.org/dataset/nm000177  
**Source type:** Official dataset documentation

### Scientific question

What repeated EEG data are available for studying motor-imagery skill acquisition and decoder adaptation?

### Dataset

- 18 BCI-naive participants;
- six sessions;
- 22 EEG channels;
- 512 Hz original sampling frequency;
- left-hand and right-hand motor imagery.

### Methodological relevance

The repeated sessions allow an initial-session decoder to be evaluated unchanged on future sessions and compared with causal prior-session adaptation.

### Limitation

The validated NeuroWeave analysis does not include verified session-level impedance or cap-position measurements.

### Relevance to NeuroWeave

The dataset supports a frozen-versus-adaptive longitudinal comparison but cannot directly resolve recording-interface causes.

## Source 7: Motor-imagery proficiency and focused EEG patterns

**Title:** Proficiency in Motor Imagery Is Linked to the Lateralization of Focused ERD Patterns and Beta PDC  
**Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11844094/  
**Source type:** Peer-reviewed paper

### Scientific question

Which EEG characteristics are associated with stronger motor-imagery BCI proficiency?

### Main finding

More proficient participants showed stronger focused and lateralized task-related patterns and associated connectivity differences.

### Limitation

The study reported associations and did not prove that training caused neuroplastic change.

### Relevance to NeuroWeave

Direct task-pattern analyses could strengthen or weaken a neural-adaptation explanation, but these analyses must remain separate from causal neuroplasticity claims.

## Source 8: Resting-state EEG and motor-imagery performance

**Title:** Predicting Motor Imagery Performance From Resting-State EEG Using Dynamic Causal Modeling  
**Link:** https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2020.00321/full  
**Source type:** Peer-reviewed paper

### Scientific question

Can resting-state EEG provide information about later motor-imagery BCI performance?

### Main finding

Resting-state connectivity differed across performance groups, and a resting-state connection was associated with motor-imagery performance across sessions.

### Limitation

Resting-state prediction does not identify whether later performance changes were caused by learning, decoder adaptation, or recording drift.

### Relevance to NeuroWeave

A standardized pre-session resting baseline could reveal whether change is task-specific or reflects broader session-level EEG variation.

## Final prior-art synthesis

The literature shows that longitudinal BCI performance can change because of several interacting mechanisms:

- decoder adaptation;
- participant learning;
- participant state;
- cross-session distribution shift;
- electrode placement;
- electrode impedance or contact quality;
- task-related pattern change;
- decision-boundary or calibration effects.

Prior work supports comparing a stable frozen decoder with an adaptive decoder, but it does not justify treating improved adaptive accuracy as direct evidence of neuroplasticity.

NeuroWeave operationalizes this distinction by:

1. evaluating a Session-0 frozen decoder on unseen future sessions;
2. evaluating a causal cumulative prior-session decoder;
3. preserving positive, negative, and zero adaptation outcomes;
4. quantifying uncertainty at the participant level;
5. reporting competing explanations and unsupported claims;
6. recommending the next measurement needed to reduce uncertainty.

The validated P3–P9 experiment provides moderate support for an average decoder-adaptation benefit within the studied sample. It does not establish neural adaptation or neuroplasticity because direct task-pattern, impedance, contact-quality, cap-position, and resting-state evidence remains unavailable.

## Research position adopted by NeuroWeave

The strongest scientific contribution is not claiming a single cause prematurely. NeuroWeave distinguishes:

- what the current evidence supports;
- what remains plausible;
- what the experiment cannot determine;
- what should be measured next.
