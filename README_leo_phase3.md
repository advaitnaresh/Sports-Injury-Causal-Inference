# Phase 3: Notebook Architecture, Visual DAG & Synthesis
**Author:** Leo Yu
**Course:** Foundations of Data Science
**Project:** Does preventative physiotherapy reduce overuse injuries in athletes?

---

## What Did I Do?

My job (Phase 3) is to **assemble the final submission notebook** — the single Jupyter file that combines Tilak's simulation/validation work (Phase 1), Advait's real-data analysis (Phase 2), and my own contributions: the visual DAG, the introduction, the discussion section, the future-work section, and overall formatting for Gradescope.

This README covers the final state of Phase 3, where all phases are fully integrated and completed.

---

## Files in This Folder (Phase 3)

| File | What it is |
|------|-----------|
| `leo_phase3_dag.ipynb` | Standalone notebook that builds the causal DAG (X → T, X → Y, T → Y) and saves it as `plot_dag.png`. Run this once to generate the image. |
| `plot_dag.png` | Output of the DAG notebook above. **Will be created on first run** of `leo_phase3_dag.ipynb`. |
| `leo_phase3_master_notebook.ipynb` | The master submission notebook scaffold. Contains all 10 sections from the project template. |
| `README_leo_phase3.md` | This file. |

For context on the existing files in the repo (Tilak's Phase 1), see `README_tilak_phase1.md`.

---

## What's Done

### Completed Tasks

- **Programmatic DAG generation** (`leo_phase3_dag.ipynb`) — independent of any other phase. Uses `networkx` + `matplotlib`. Produces a clean three-node DAG with color-coded confounder / treatment / outcome and a labelled `β_T` arrow.
- **Master notebook** (`leo_phase3_master_notebook.ipynb`) — every section from the project template is present:
  - **Section 1 (Introduction)** — full prose: question/estimand, data description, reference. Pulled from the proposal and lightly expanded.
  - **Section 2 (Causal Model)** — full prose plus the DAG generation code embedded inline so the master notebook is self-contained.
  - **Section 3 (Statistical Model)** — full prose: model equations, prior justification, outcome distribution, confound handling. Math written in LaTeX.
  - **Section 4 (Validation on Simulated Data)** — **Tilak's full Phase 1 code is integrated inline** (data simulation, PyMC model, prior predictive, MCMC, diagnostics, parameter recovery, forest plot). The headline-result table is also pre-rendered in markdown. Section 4 needs nothing from Tilak — running the master notebook end-to-end re-executes his pipeline and reproduces his validation result.
  - **Sections 5, 6, 7 (Real-data prep / posterior / PPC)** — placeholder cells with a checklist of what each section needs from Advait.
  - **Section 8 (Discussion and Conclusion)** — written prose which has been updated with the specific posterior numbers from the real data. Includes 8.1 (answering the question), 8.2 (addressing the confound), and 8.3 (causal-effect plot).
  - **Section 9 (Future Work)** — fully written. Four extensions plus a limitations paragraph.
  - **Section 10 (Group Member Contributions)** — fully written with the agreed split.

### Phase 2 Integration (Completed)

1. **Pasted Advait's real-data cells** into Sections 5, 6, 7 of the master notebook.
2. **Filled in Section 8 placeholders** — `[ADVAIT-MEAN]`, `[ADVAIT-HDI-LOW]`, `[ADVAIT-HDI-HIGH]`, `[ADVAIT-DELTA-P]`, `[ADVAIT-BETAX-MEAN]`, `[ADVAIT-BETAX-HDI]`, plus the `[INTERPRET-SIGN]` and `[ALIGN/CONFLICT]` choices, using the real-data posterior fit.
3. **Generated the causal-effect plot** (Section 8.3) — `arviz.plot_posterior(trace_real, var_names=['beta_T'])`.
4. **Run the master notebook end-to-end** so all cell outputs are produced.
5. **Export to PDF** and check that it stays under 20 pages at 12-point font.

---

## How to Run the DAG Notebook

### Requirements
```
pip install networkx matplotlib
```
(Both are already in the `conda-env-fnds-py` environment used by Tilak.)

### Run
Open `leo_phase3_dag.ipynb` in Jupyter and click **Run All**. The notebook will:
1. Build the DAG via `networkx.DiGraph()` with three nodes and three edges.
2. Verify the graph is acyclic (`nx.is_directed_acyclic_graph`).
3. Render it with fixed positions (X top-center, T bottom-left, Y bottom-right).
4. Save `plot_dag.png` to the project folder.

The same code is embedded in Section 2 of `leo_phase3_master_notebook.ipynb`, so when the master notebook is run end-to-end the DAG is regenerated as part of the submission.

---

## Design Choices Worth Noting

- **Why networkx instead of graphviz?** `networkx` ships pure-Python and works inside any conda environment without a system install. `graphviz` would need a separate Graphviz binary on PATH, which is brittle across the three of our machines. The visual quality is equivalent for a three-node DAG.
- **Why fixed node positions instead of an automatic layout?** Spring layouts (`nx.spring_layout`) move on every run, which would make the DAG look different in the screencast vs. the PDF. Fixed positions are deterministic and let us point at a specific arrow during the recording.
- **Why the placeholder pattern (`[ADVAIT-MEAN]`, etc.) was used in Section 8?** This let Leo write the full discussion paragraph structure early, while reserving the spots that genuinely needed Advait's real-data numbers. When Phase 2 landed, Section 8 became a 10-minute find-and-replace, rather than a from-scratch writing job.
- **Why the master notebook is a "scaffold" and not the final notebook?** The final notebook needs Tilak's executed validation cells and Advait's executed real-data cells embedded inline, both with their plot outputs preserved. That can only happen once those cells exist and have been run. The scaffold sets the structure so the merge is mechanical.

---

## For Tilak (Phase 1)

Your Phase 1 validation pipeline is **already integrated** into Section 4 of `leo_phase3_master_notebook.ipynb`. The code is the same as in `tilak_phase1_validation.ipynb`, with the same `RANDOM_SEED = 42`, so re-running the master notebook reproduces the recovery numbers shown in the Section 4 markdown table. Nothing more is needed from you on the notebook side — your remaining responsibilities are the screencast section and the in-person discussion.

---

## For Advait (Phase 2)

Your work plugs into three sections of `leo_phase3_master_notebook.ipynb`:

- **Section 5** — load CSV, map columns to X/T/Y, standardize, sanity-check.
- **Section 6** — same PyMC model structure as Tilak's, swap in real X/T/Y, run `pm.sample(...)`, check R-hat / ESS / trace.
- **Section 7** — `pm.sample_posterior_predictive(...)` and the four-element plot (observed data + posterior mean + HDI on the mean + HDI on predictions).

All sections are fully implemented, run, and filled out with the actual values.