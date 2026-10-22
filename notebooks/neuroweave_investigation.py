import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path

    import marimo as mo
    import pandas as pd

    return Path, json, mo, pd


@app.cell
def _(Path, json, pd):
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    RESULTS_DIR = (
        PROJECT_ROOT
        / "results"
        / "combined_participants_3_to_9"
    )

    EVIDENCE_DIR = PROJECT_ROOT / "evidence"

    comparison_path = (
        RESULTS_DIR
        / "paired_future_session_comparisons.csv"
    )

    participant_path = (
        RESULTS_DIR
        / "participant_summary.csv"
    )

    leave_one_out_path = (
        RESULTS_DIR
        / "leave_one_participant_out.csv"
    )

    cross_session_evidence_path = (
        EVIDENCE_DIR
        / "valency_cross_session.json"
    )

    adaptation_evidence_path = (
        EVIDENCE_DIR
        / "valency_decoder_adaptation.json"
    )

    required_paths = [
        comparison_path,
        participant_path,
        leave_one_out_path,
    ]

    missing_files = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "The following required files are missing:\n"
            + "\n".join(missing_files)
        )

    session_results = pd.read_csv(comparison_path)
    participant_summary = pd.read_csv(participant_path)
    leave_one_out = pd.read_csv(leave_one_out_path)

    def load_evidence(path):
        if not path.exists():
            return {
                "query_id": path.stem,
                "papers": [],
                "status": "missing",
            }

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        data["status"] = "loaded"
        return data

    cross_session_evidence = load_evidence(
        cross_session_evidence_path
    )

    adaptation_evidence = load_evidence(
        adaptation_evidence_path
    )
    return (
        adaptation_evidence,
        cross_session_evidence,
        leave_one_out,
        participant_summary,
        session_results,
    )


@app.cell
def _(mo):
    mo.md("""
    # NeuroWeave Interactive Evidence Investigation

    ### When performance changes across sessions, what changed?

    NeuroWeave compares a frozen decoder with a causal cumulative
    decoder, preserves harmful adaptation outcomes, evaluates
    participant-level robustness, and connects experimental findings
    with scientific literature retrieved through Valency MCP Bond.

    **Validated cohort:** Participants 3–9
    **Future-session comparisons:** 35
    **Primary metric:** Balanced accuracy
    """)
    return


@app.cell
def _(participant_summary, session_results):
    overall_frozen = session_results[
        "frozen_balanced_accuracy"
    ].mean()

    overall_adaptive = session_results[
        "adaptive_balanced_accuracy"
    ].mean()

    overall_gain = session_results[
        "adaptation_gain"
    ].mean()

    positive_sessions = int(
        (session_results["adaptation_gain"] > 0).sum()
    )

    negative_sessions = int(
        (session_results["adaptation_gain"] < 0).sum()
    )

    zero_sessions = int(
        (session_results["adaptation_gain"] == 0).sum()
    )

    improving_participants = int(
        (participant_summary["mean_gain"] > 0).sum()
    )

    participant_count = int(
        participant_summary["participant"].nunique()
    )
    return (
        improving_participants,
        negative_sessions,
        overall_adaptive,
        overall_frozen,
        overall_gain,
        participant_count,
        positive_sessions,
        zero_sessions,
    )


@app.cell
def _(
    improving_participants,
    mo,
    negative_sessions,
    overall_adaptive,
    overall_frozen,
    overall_gain,
    participant_count,
    positive_sessions,
    zero_sessions,
):
    mo.hstack(
        [
            mo.stat(
                value=f"{overall_frozen:.3f}",
                label="Frozen mean",
                bordered=True,
            ),
            mo.stat(
                value=f"{overall_adaptive:.3f}",
                label="Adaptive mean",
                bordered=True,
            ),
            mo.stat(
                value=f"{overall_gain:+.3f}",
                label="Mean adaptation gain",
                bordered=True,
            ),
            mo.stat(
                value=f"{improving_participants}/{participant_count}",
                label="Participants improving",
                bordered=True,
            ),
        ],
        widths="equal",
    )

    mo.hstack(
        [
            mo.stat(
                value=str(positive_sessions),
                label="Sessions helped",
                bordered=True,
            ),
            mo.stat(
                value=str(negative_sessions),
                label="Sessions harmed",
                bordered=True,
            ),
            mo.stat(
                value=str(zero_sessions),
                label="Zero-gain sessions",
                bordered=True,
            ),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo, session_results):
    participant_options = sorted(
        session_results["participant"]
        .astype(int)
        .unique()
        .tolist()
    )

    participant_selector = mo.ui.dropdown(
        options=participant_options,
        value=9,
        label="Select a participant",
    )

    participant_selector
    return (participant_selector,)


@app.cell
def _(participant_selector, session_results):
    selected_participant = int(
        participant_selector.value
    )

    participant_rows = (
        session_results[
            session_results["participant"]
            == selected_participant
        ]
        .sort_values("session")
        .reset_index(drop=True)
    )
    return participant_rows, selected_participant


@app.cell
def _(mo, participant_rows):
    session_options = (
        participant_rows["session"]
        .astype(int)
        .tolist()
    )

    default_session = (
        2 if 2 in session_options else session_options[0]
    )

    session_selector = mo.ui.dropdown(
        options=session_options,
        value=default_session,
        label="Select a future session",
    )

    session_selector
    return (session_selector,)


@app.cell
def _(participant_rows, session_selector):
    selected_session = int(
        session_selector.value
    )

    selected_row = participant_rows[
        participant_rows["session"]
        == selected_session
    ].iloc[0]

    frozen_value = float(
        selected_row["frozen_balanced_accuracy"]
    )

    adaptive_value = float(
        selected_row["adaptive_balanced_accuracy"]
    )

    selected_gain = float(
        selected_row["adaptation_gain"]
    )

    if selected_gain > 0:
        selected_direction = "Adaptation helped"
        selected_color = "#18b59b"
        selected_icon = "▲"
    elif selected_gain < 0:
        selected_direction = "Adaptation hurt"
        selected_color = "#ef6259"
        selected_icon = "▼"
    else:
        selected_direction = "No adaptation gain"
        selected_color = "#8898a7"
        selected_icon = "●"
    return (
        adaptive_value,
        frozen_value,
        selected_color,
        selected_direction,
        selected_gain,
        selected_icon,
        selected_session,
    )


@app.cell
def _(
    adaptive_value,
    frozen_value,
    mo,
    selected_color,
    selected_direction,
    selected_gain,
    selected_icon,
    selected_participant,
    selected_session,
):
    mo.md(f"""
    ## Selected investigation

    **Participant {selected_participant}, Session {selected_session}**

    <div style="
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
        margin-top:12px;
    ">
        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid #315468;
            background:#0b1c28;
        ">
            <div style="color:#91a6b5;font-size:13px;">
                FROZEN DECODER
            </div>
            <div style="
                color:#f5fbff;
                font-size:34px;
                font-weight:700;
            ">
                {frozen_value:.3f}
            </div>
        </div>

        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid #315468;
            background:#0b1c28;
        ">
            <div style="color:#91a6b5;font-size:13px;">
                ADAPTIVE DECODER
            </div>
            <div style="
                color:#f5fbff;
                font-size:34px;
                font-weight:700;
            ">
                {adaptive_value:.3f}
            </div>
        </div>

        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid {selected_color};
            background:#0b1c28;
        ">
            <div style="color:#91a6b5;font-size:13px;">
                ADAPTATION GAIN
            </div>
            <div style="
                color:{selected_color};
                font-size:34px;
                font-weight:700;
            ">
                {selected_icon} {selected_gain:+.3f}
            </div>
            <div style="
                color:{selected_color};
                font-weight:600;
            ">
                {selected_direction}
            </div>
        </div>
    </div>
    """)
    return


@app.cell
def _(mo):
    harmful_only = mo.ui.switch(
        value=False,
        label="Show only harmful adaptation outcomes",
    )

    harmful_only
    return (harmful_only,)


@app.cell
def _(harmful_only, session_results):
    if harmful_only.value:
        displayed_session_results = session_results[
            session_results["adaptation_gain"] < 0
        ].copy()
    else:
        displayed_session_results = (
            session_results.copy()
        )

    displayed_session_results["outcome"] = (
        displayed_session_results[
            "adaptation_gain"
        ].apply(
            lambda value: (
                "Helped"
                if value > 0
                else "Hurt"
                if value < 0
                else "Zero"
            )
        )
    )

    displayed_session_results = (
        displayed_session_results[
            [
                "participant",
                "session",
                "frozen_balanced_accuracy",
                "adaptive_balanced_accuracy",
                "adaptation_gain",
                "outcome",
            ]
        ]
        .sort_values(
            ["participant", "session"]
        )
        .reset_index(drop=True)
    )
    return (displayed_session_results,)


@app.cell
def _(displayed_session_results, mo):
    mo.md("## Future-session evidence")

    mo.ui.table(
        displayed_session_results,
        pagination=True,
        page_size=10,
        selection=None,
        show_column_summaries=True,
        freeze_columns_left=["participant", "session"],
    )
    return


@app.cell
def _(mo, session_results):
    participant_nine = (
        session_results[
            session_results["participant"] == 9
        ]
        .sort_values("session")
        .reset_index(drop=True)
    )

    p9_session_two = participant_nine[
        participant_nine["session"] == 2
    ].iloc[0]

    p9_session_five = participant_nine[
        participant_nine["session"] == 5
    ].iloc[0]

    p9_s2_frozen = float(
        p9_session_two["frozen_balanced_accuracy"]
    )

    p9_s2_adaptive = float(
        p9_session_two["adaptive_balanced_accuracy"]
    )

    p9_s2_gain = float(
        p9_session_two["adaptation_gain"]
    )

    p9_s5_frozen = float(
        p9_session_five["frozen_balanced_accuracy"]
    )

    p9_s5_adaptive = float(
        p9_session_five["adaptive_balanced_accuracy"]
    )

    p9_s5_gain = float(
        p9_session_five["adaptation_gain"]
    )

    mo.md(
        f"""
        ## Participant 9: the reversal that changes the decision

        <div style="
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:18px;
        ">
            <div style="
                padding:20px;
                border-radius:16px;
                background:#29181b;
                border:1px solid #ef6259;
            ">
                <div style="
                    color:#ef6259;
                    font-weight:700;
                    font-size:14px;
                ">
                    SESSION 2 · WARNING
                </div>

                <div style="
                    font-size:22px;
                    margin-top:12px;
                ">
                    Frozen {p9_s2_frozen:.3f}
                    → Adaptive {p9_s2_adaptive:.3f}
                </div>

                <div style="
                    color:#ef6259;
                    font-size:30px;
                    font-weight:700;
                    margin-top:8px;
                ">
                    {p9_s2_gain:+.3f}
                </div>

                <div>
                    Adaptation harmed this future session.
                </div>
            </div>

            <div style="
                padding:20px;
                border-radius:16px;
                background:#102824;
                border:1px solid #18b59b;
            ">
                <div style="
                    color:#18b59b;
                    font-weight:700;
                    font-size:14px;
                ">
                    SESSION 5 · REVERSAL
                </div>

                <div style="
                    font-size:22px;
                    margin-top:12px;
                ">
                    Frozen {p9_s5_frozen:.3f}
                    → Adaptive {p9_s5_adaptive:.3f}
                </div>

                <div style="
                    color:#18b59b;
                    font-size:30px;
                    font-weight:700;
                    margin-top:8px;
                ">
                    {p9_s5_gain:+.3f}
                </div>

                <div>
                    Adaptation rescued this future session.
                </div>
            </div>
        </div>

        > The same participant contains evidence both for and against
        > adaptation. The correct decision is conditional, not universal.
        """
    )
    return


@app.cell
def _(mo, participant_summary):
    exclusion_options = [
        "None"
    ] + participant_summary["participant"].astype(
        int
    ).astype(str).tolist()

    exclusion_selector = mo.ui.dropdown(
        options=exclusion_options,
        value="None",
        label="Exclude one participant",
    )

    exclusion_selector
    return (exclusion_selector,)


@app.cell
def _(exclusion_selector, participant_summary):
    if exclusion_selector.value == "None":
        robustness_rows = participant_summary.copy()
        exclusion_label = "No participant excluded"
    else:
        excluded_value = int(
            exclusion_selector.value
        )

        robustness_rows = participant_summary[
            participant_summary["participant"]
            != excluded_value
        ].copy()

        exclusion_label = (
            f"Participant {excluded_value} excluded"
        )

    robustness_mean_gain = float(
        robustness_rows["mean_gain"].mean()
    )

    robustness_participant_count = int(
        robustness_rows["participant"].nunique()
    )

    robustness_direction = (
        "Mean adaptation gain remains positive"
        if robustness_mean_gain > 0
        else "Mean adaptation gain is not positive"
    )
    return (
        exclusion_label,
        robustness_direction,
        robustness_mean_gain,
        robustness_participant_count,
    )


@app.cell
def _(
    exclusion_label,
    mo,
    robustness_direction,
    robustness_mean_gain,
    robustness_participant_count,
):
    robustness_color = (
        "#18b59b"
        if robustness_mean_gain > 0
        else "#ef6259"
    )

    mo.md(
        f"""
        ## Participant-level robustness challenge

        **{exclusion_label}**

        <div style="
            padding:20px;
            border-radius:16px;
            background:#0b1c28;
            border:1px solid {robustness_color};
        ">
            <div style="
                color:#91a6b5;
                font-size:13px;
            ">
                REMAINING PARTICIPANTS
            </div>

            <div style="
                font-size:26px;
                font-weight:700;
            ">
                {robustness_participant_count}
            </div>

            <div style="
                color:#91a6b5;
                font-size:13px;
                margin-top:12px;
            ">
                UPDATED MEAN GAIN
            </div>

            <div style="
                color:{robustness_color};
                font-size:34px;
                font-weight:700;
            ">
                {robustness_mean_gain:+.6f}
            </div>

            <div style="
                color:{robustness_color};
                font-weight:700;
            ">
                {robustness_direction}
            </div>
        </div>
        """
    )
    return


@app.cell
def _(leave_one_out, mo):
    mo.md(
        """
        ### Precomputed leave-one-participant-out results

        These values come from the final statistical-robustness analysis.
        """
    )

    mo.ui.table(
        leave_one_out,
        pagination=False,
        selection=None,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## NeuroWeave hypothesis verdict

    <div style="
        display:grid;
        grid-template-columns:repeat(2,1fr);
        gap:16px;
    ">
        <div style="
            padding:18px;
            border-radius:14px;
            background:#102824;
            border:1px solid #18b59b;
        ">
            <strong style="color:#18b59b;">
                Decoder adaptation
            </strong>
            <p>
                Moderately supported within the studied sample.
            </p>
        </div>

        <div style="
            padding:18px;
            border-radius:14px;
            background:#292214;
            border:1px solid #efb95a;
        ">
            <strong style="color:#efb95a;">
                Recording/session drift
            </strong>
            <p>
                Plausible, but the physical cause is unresolved.
            </p>
        </div>

        <div style="
            padding:18px;
            border-radius:14px;
            background:#271a20;
            border:1px solid #ef6259;
        ">
            <strong style="color:#ef6259;">
                Decision-boundary effects
            </strong>
            <p>
                Important competing explanation requiring
                calibration-focused testing.
            </p>
        </div>

        <div style="
            padding:18px;
            border-radius:14px;
            background:#211b30;
            border:1px solid #9d80ff;
        ">
            <strong style="color:#9d80ff;">
                Neural adaptation
            </strong>
            <p>
                Not established by accuracy changes alone.
            </p>
        </div>
    </div>
    """)
    return


@app.cell
def _(adaptation_evidence, cross_session_evidence, pd):
    evidence_records = []

    evidence_sources = [
        cross_session_evidence,
        adaptation_evidence,
    ]

    for evidence_group in evidence_sources:
        query_id = evidence_group.get(
            "query_id",
            "unknown",
        )

        hypothesis = evidence_group.get(
            "hypothesis",
            "unknown",
        )

        for paper in evidence_group.get(
            "papers",
            [],
        ):
            limitation = paper.get(
                "limitation",
                paper.get(
                    "counterevidence_or_limitation",
                    "",
                ),
            )

            evidence_records.append(
                {
                    "query": query_id,
                    "hypothesis": hypothesis,
                    "direction": paper.get(
                        "evidence_direction",
                        "",
                    ),
                    "year": paper.get(
                        "year"
                    ),
                    "paper": paper.get(
                        "title",
                        "",
                    ),
                    "finding": paper.get(
                        "key_finding",
                        "",
                    ),
                    "limitation": limitation,
                    "doi": paper.get(
                        "doi",
                        "",
                    ),
                    "source": paper.get(
                        "source_url",
                        "",
                    ),
                }
            )

    evidence_table = pd.DataFrame(
        evidence_records
    )
    return (evidence_table,)


@app.cell
def _(evidence_table, mo):
    mo.md(
        """
        ## Scientific literature via Valency MCP Bond

        The table combines experimental interpretation with retrieved
        literature evidence, counterevidence, and limitations.
        """
    )

    if evidence_table.empty:
        evidence_display = mo.callout(
            "No Valency evidence files were found. Add the JSON files "
            "to the evidence folder and rerun the notebook.",
            kind="warn",
        )
    else:
        evidence_display = mo.ui.table(
            evidence_table,
            pagination=True,
            page_size=5,
            selection=None,
            show_column_summaries=False,
            freeze_columns_left=[
                "direction",
                "year",
            ],
        )

    evidence_display
    return


@app.cell
def _(mo):
    mo.md("""
    ## Final scoped verdict

    > **Moderate support for an adaptation benefit within the
    > validated P3–P9 sample.**

    The average adaptation effect is positive and remains positive
    under leave-one-participant-out analysis. However, adaptation
    produced harmful and zero-gain outcomes. NeuroWeave therefore
    does not recommend enabling adaptation blindly.

    ### Claims supported

    - Cumulative prior-session adaptation improves balanced accuracy
      on average within the studied sample.
    - The benefit varies across participants and sessions.
    - Monitoring should precede the adaptation decision.

    ### Claims not supported

    - Adaptation helps every participant or every session.
    - Accuracy improvement proves neuroplasticity.
    - The experiment identifies the physical cause of EEG drift.
    - The result generalizes to all BCI users.

    ### Highest-value next measurements

    1. Run a training-size-matched comparison.
    2. Evaluate a selective-adaptation policy.
    3. Collect electrode impedance or contact-quality measurements.
    4. Record cap-position metadata.
    5. Examine direct task-related EEG-pattern stability.
    """)
    return


if __name__ == "__main__":
    app.run()
