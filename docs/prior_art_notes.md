# NEUROWEAVE Prior-Art Research Notebook

## Research questions

1. How do longitudinal BCI studies distinguish user learning from decoder adaptation?
2. What recording variations commonly affect EEG across sessions?
3. What evidence can support neural adaptation without claiming direct proof of neuroplasticity?
4. Which follow-up measurements could separate neural change from electrode or session drift?

## Source 1

### Co-adaptive Training Improves Efficacy of a Multi-Day EEG-Based Motor Imagery BCI Training

- Link: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2019.00362/full
- Source type: Peer-reviewed paper
- Scientific question: Does regularly adapting the decoder improve performance during multi-day motor-imagery BCI training compared with keeping the original decoder fixed?
- Dataset: EEG recordings from 18 participants completing a four-day motor-imagery experiment. Nine participants used a classifier fixed from Day 1, while nine used a classifier that was regularly adapted.
- Method: Compared performance changes between a fixed-classifier control group and an adaptive-classifier experimental group, including within-day and between-day changes.
- Main finding: The adaptive group showed a larger performance change after training. The adaptive group improved within days but declined between days, while the fixed group declined both within and between days.
- Limitation: Performance reflects both participant and decoder behavior. Adaptive accuracy alone cannot prove neural adaptation.
- How it affects NEUROWEAVE: A frozen-decoder control is necessary before attributing improvement to the participant.

## Source 2

### Intra- and Inter-subject Variability in EEG-Based Sensorimotor Brain Computer Interface: A Review

- Link: https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2019.00087/full
- Source type: Peer-reviewed review paper
- Scientific question: How do within-participant and between-participant differences affect EEG-based sensorimotor BCI performance?
- Dataset: Review of previous EEG-based sensorimotor BCI studies.
- Method: Reviewed variability in sensorimotor rhythms, BCI predictors, and transfer-learning methods.
- Main finding: Sensorimotor EEG activity varies over time and across participants, changing feature distributions and limiting cross-session model transfer.
- Limitation: The review cannot identify the cause of a change in a specific NEUROWEAVE session.
- How it affects NEUROWEAVE: Cross-session changes must be treated as possible distribution shift until recording and session effects are assessed.

## Source 3

### Variability of EEG Electrode Positions and Their Underlying Brain Regions

- Link: https://pmc.ncbi.nlm.nih.gov/articles/PMC8865144/
- Source type: Peer-reviewed paper
- Scientific question: How much can EEG electrode positions and underlying brain regions vary even with a fixed cap?
- Dataset: Simultaneous EEG-fMRI data from 20 participants.
- Method: Used gel artifacts visible in structural MRI to locate electrodes and map them to underlying brain regions.
- Main finding: Electrode positions varied, and corresponding electrodes did not always cover consistent underlying brain regions.
- Limitation: The study examined between-participant differences rather than repeated motor-imagery sessions within the same participant.
- How it affects NEUROWEAVE: Cap placement is a plausible source of recording drift, but causation cannot be claimed without placement metadata.

## Source 4

### The Dependence of Electrode Impedance on the Number of Performed EEG Examinations

- Link: https://pmc.ncbi.nlm.nih.gov/articles/PMC6603518/
- Source type: Peer-reviewed paper
- Scientific question: Does repeated use of reusable EEG electrodes affect impedance and recording reliability?
- Dataset: Ten new reusable EEG electrodes tested repeatedly after subsequent uses.
- Method: Measured electrode properties using electrochemical impedance spectroscopy.
- Main finding: Electrode impedance varied, including among new electrodes, showing that the recording interface cannot be assumed constant.
- Limitation: The study did not test motor-imagery performance or longitudinal neural adaptation.
- How it affects NEUROWEAVE: Session-level impedance should be measured in future data collection and must not be retrospectively invented.

## Source 5

### Neural Correlates of User Learning During Long-Term BCI Training for the Cybathlon Competition

- Link: https://link.springer.com/article/10.1186/s12984-022-01047-x
- Source type: Peer-reviewed paper
- Scientific question: Which behavioral and EEG-pattern changes can help track user learning during long-term BCI training?
- Dataset: Longitudinal EEG data from one experienced BCI user during preparation for two Cybathlon competitions.
- Method: Combined performance metrics with analyses of changes in neural patterns while decoder recalibration occurred infrequently.
- Main finding: Performance improved over time, and within-class neural-pattern changes helped track skill acquisition and stabilization.
- Limitation: One highly trained user in a specialized competition setting limits generalization.
- How it affects NEUROWEAVE: Task-related pattern consistency should be examined alongside accuracy, but it remains evidence consistent with adaptation rather than proof of neuroplasticity.

## Source 6

### Multi-Session Longitudinal Motor Imagery EEG Dataset

- Link: https://nemar.org/dataset/nm000177
- Source type: Official dataset documentation
- Scientific question: What longitudinal data and session structure are available for studying motor-imagery skill acquisition and decoder adaptation?
- Dataset: EEG recordings from 18 BCI-naive participants across six sessions, with 22 EEG channels recorded at 512 Hz during left-hand and right-hand motor imagery.
- Method: The first session was an offline calibration session, followed by online sessions with visual feedback. The documentation describes Generic Recentering and Personally Assisted Recentering protocols.
- Main finding: The dataset supports repeated cross-session comparisons under different adaptation approaches.
- Limitation: Session-level electrode impedance and cap-position measurements are unavailable in the documentation used here.
- How it affects NEUROWEAVE: The dataset supports a frozen Session-0 experiment, but missing interface metadata limits physical attribution of drift.

## Source 7

### Proficiency in Motor Imagery Is Linked to the Lateralization of Focused ERD Patterns and Beta PDC

- Link: https://pmc.ncbi.nlm.nih.gov/articles/PMC11844094/
- Source type: Peer-reviewed paper
- Scientific question: Which EEG characteristics are associated with stronger motor-imagery BCI proficiency?
- Dataset: EEG recordings from nine healthy participants who trained for four sessions.
- Method: Analyzed event-related synchronization and desynchronization, power spectral density, connectivity, and session accuracy.
- Main finding: More proficient participants showed focused, lateralized alpha ERD and lateralized beta and gamma connectivity patterns.
- Limitation: The small study identified associations and did not prove that training caused neuroplastic changes.
- How it affects NEUROWEAVE: Pattern focus and consistency can supplement accuracy when assessing neural adaptation.

## Source 8

### Predicting Motor Imagery Performance From Resting-State EEG Using Dynamic Causal Modeling

- Link: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2020.00321/full
- Source type: Peer-reviewed paper
- Scientific question: Can resting-state EEG provide information about later motor-imagery BCI performance?
- Dataset: Public motor-imagery data containing pre-experiment resting-state EEG and measurements from two sessions on different days.
- Method: Analyzed directional connectivity between motor-related regions during rest and used regression to predict performance.
- Main finding: Resting-state connectivity differed between lower- and higher-performing groups and was associated with performance in both sessions.
- Limitation: Resting-state connectivity did not identify whether later changes were caused by learning, decoder adaptation, or drift.
- How it affects NEUROWEAVE: A standardized resting baseline could reveal whether session changes extend beyond the motor-imagery task.

## Research synthesis

The literature supports a controlled comparison rather than a single-score claim. A frozen decoder isolates performance without model updating. A cumulative decoder tests whether recalibration helps. Drift and calibration audits test whether the recording distribution or decision boundary changed. Even when several indicators favor neural adaptation, the correct wording is that the evidence is consistent with neural adaptation, not that neuroplasticity was proved.
