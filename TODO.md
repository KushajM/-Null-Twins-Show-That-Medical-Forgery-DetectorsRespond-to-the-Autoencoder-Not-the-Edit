# TODO — pending items for the CVPR 2027 draft

Deadlines (AoE): registration **Nov 10**, paper **Nov 16**, supplementary **Nov 23**, 2026.
Tables freeze on **Oct 26** (round-3 verdict, step 7).
"Owner" is the experiment or workstream that closes the item. Paths are relative to the project root.
Specs: `docs/council/round3/council_verdict.md` ("Experiments to Nov 16") and `docs/council/round3/experiments/E3*.md`.

## Round-3 experiments (required before the paper is final)

| # | item | owner experiment | where it lands in the paper | decision rule (from the verdict) |
|---|---|---|---|---|
| E3a | **Pristine-reference rescoring and SDXL holdout.** Re-score the paired baseline (p1n), + benign negatives (p2), + invariance λ=0.03 (p3) and subtraction with the untouched source A as reference (plus ±2 px shift and 0.98 rescale), calibration first, then test. Score p2, p3 and subtraction on the held-out SDXL arms; compute every model's SDXL-twin FPR beside the FPR on SD twins matched on in-mask MSE. | E3a (`docs/council/round3/experiments/E3a_reference_rescore_sdxl.md`), runner, ≈$2.5–3.3 | Table 4 `SDXL twin` column (every `$\star$`); Sec. 4 "Tasks" (`\TODO{E3a…}`); Sec. 5.2 "Drift beside transfer"; Sec. 5.3 (`\PENDING{Pending E3a…}` on the claim sentence; `\TODO` on pristine reference); limitations "Reference"; supplementary SDXL per modality | Keep the p3 row if, on calibration with reference A, the max FPR over nulls and benign ops is ≤ 0.20 at its own threshold and the B_lama-fitted threshold shifts it by ≤ 0.10, **and** on SDXL its null FPR is ≤ 0.10 at TPR ≥ 0.90 at the SD threshold. If it fails: p3 becomes a diagnostic, delete the claim sentence, and keep subtraction + hash in Table 5. If mode A passes, "null-twin reference" may become "archived reference" for that row; if the perturbations also pass, add "robust to ±2 px / 2% misregistration", otherwise write "requires a pixel-registered reference". |
| E3b | **MedForge matched-degradation job.** 186 existing + 186 fresh untouched scans, scored by the Reasoner, standard and twin-trained Mesorch, per modality: JPEG and lossy JPEG 2000 at each image's SD-round-trip PSNR; CompressAI Cheng2020-anchor at matched PSNR; a local SD null (SD round trip inside a 2–4% box, pasted back, JPEG q95); the fresh sample. | E3b (`docs/council/round3/experiments/E3b_medforge_matched.md`), runner, ≈$3–4 (cap $8) | Sec. 5.1 MedForge paragraph (`\TODO{E3b…}`), Table 3, Fig. 2 caption, limitations "MedForge degradation control" | JPEG/JPEG 2000 ≤ 10% fake: keep "responds to the autoencoder"; ≥ 50%: headline becomes "responds to processing, not edits", with JPEG 2000 as the clinical example. Learned codec ≥ 30%: add "benign learned compression is called fake"; ≤ 10%: do not claim clinical pipelines contain autoencoders. Local null ≥ 30% fake with box IoU ≥ 0.3: add "it localises the autoencoder"; ≤ 10%: rest the local claim on our corpus (Mesorch 0.963 / 0.536). Keep per-modality Reasoner numbers only if the fresh sample reproduces them. |
| E3c | **Block-wise robust hash.** Battiato-style DCT signatures at 16 and 32 px blocks, thresholded on calibration, then test; CPU. | E3c, runner, ≈$0.5 | Table 5 row (`\PENDING{E3c}`), Sec. 4 baselines (`\TODO{E3c…}`), supplementary | If it reaches B-vs-C ≥ 0.95 with every FPR ≤ 0.20, **delete the claim sentence** in Sec. 5.3. Add its row to Table 4. |
| E3d | **p3 seeds 43 and 44** (λ=0.03), on two GPU sizes, calibration and SDXL. | E3d, runner, ≈$7.5 | Sec. 5.3 (`\TODO{E3d…}`), limitations "Test reuse", supplementary | Report mean ± SD; if any seed's worst pooled FPR exceeds 0.20, report that seed on its own. The pre-registered λ rule is locked (`r3_lambda_preregistration.json`). |
| E1b | **Frozen-generator probe positive control.** Run the probe on edits generated at native scale without resize-and-paste-back; calibration only. | E1b, runner, ≈$2.1 | Supplementary paragraph only (`\TODO{E1b…}` in `sec/X_suppl.tex`); one main-text sentence at the end of Sec. 5.4 | Judged by its own rules (erasure, no mechanism, or bug). Pass → the paragraph says resizing and pasting back erase the sampler's evidence. Fail → the probe is at fault; keep the falsified-hypothesis paragraph. Main text stays one sentence either way. |

## Numbers cited only to the verdict (pending r3_step1)

| number | where | note |
|---|---|---|
| "choosing λ by output invariance picks λ=0.1" | Sec. 5.2, "AUC and operating-point selection disagree" | Not in the step-1 outputs. Reproduce the invariance-based choice on calibration (E4 selection log) and cite the file; the rates that follow (18.2% / 20.2% / 27.8%) are already step-1. |

## Other required items

| # | item | owner experiment | where it lands in the paper |
|---|---|---|---|
| 5 | **F5 re-run.** The probe's fusion criterion was computed on only 24 images / 12 split units (`work/e0/out_local/e1_irp/e1_criteria.json`). Re-score windows for all 822 calibration lineages and recompute F5. | E1 (probe falsifier), F5 criterion | supplementary probe paragraph (currently not quoted) |
| 6 | **Licence table.** One row per source with licence, redistribution status and what is released; resolve the repackaged Kaggle sources (X-ray, histopathology, MRI, non-removal endoscopy and ultrasound) that have no recorded upstream licence. | Release / datasheet workstream | Ethics statement, supplementary Sec. B |
| 7 | **Dataset name.** Pick one of NullTwin-Med, LesionTwin, PlaceboEdit (README), re-run the name search, set `\dataset` in `macros.tex`, and rename the public repository before registration. | Team decision (release workstream) | `macros.tex` (one line) |

## Data and traceability

| # | item | owner experiment |
|---|---|---|
| 8 | Re-pull AEROBLADE's per-task CSV and confirm its B-vs-C is the SD-twin value (the summary table's B-vs-C cells were overwritten by LaMa values for NPR and UniFD; see README). Remove the `\S` flag in Table 2. | E6 (synthetic-image baselines) |
| 9 | Pull `e0x/e0e/` (`E0E_REPORT.md`, `e0e_threshold_transfer.csv`) and the SDXL score parquets (`scores_e0x/`) to `work/e0/out_local/`, so Table 4's SDXL-twin column cites a CSV rather than the carried-over values in `R3_STEP1_REPORT.md`. Also pull the calibration parquets for distilled Mesorch and the paired baseline (p1n), so their Table 4 rows can move from test (‡) to calibration like the others. | E0e / E3a |
| 10 | Append `TEST_LOG.md` rows for test numbers the paper quotes that predate the log or were re-derived here: fine-tuned IML-ViT, MVSS-Net and TruFor; NPR, UniFD, AEROBLADE; distilled Mesorch B-vs-D, A-vs-CM, A-vs-B and the paired control's A-vs-C / A-vs-B / CT; and the **p2 / p3 test AUCs** (B-vs-C, B-vs-D, A-vs-B, per modality) computed by `scripts/derive_numbers.py` into `data/paired_family_test_auc.csv`. Nothing was selected on them; λ was fixed on calibration first. | E0p (protocol) |
| 11 | Ship the leak-free splits (1,983 / 822 / 1,151, `docs/council/round2/experiments/local/split_freeze.json`) with the release; the currently published splits are 1,944 / 823 / 1,189. Add the SDXL calibration and test images to the release. | Release workstream |
| 12 | Confirm the X-ray source attribution (cited as the Rahman et al. TB database; marked `% UNVERIFIED` in `refs.bib`) and the brain-MRI aggregate citation. | Dataset documentation |
| 13 | Resolve the remaining `% UNVERIFIED` fields in `refs.bib` (End4 venue, page numbers, full author lists). | Writing |
| 13b | Re-run release audit 4.4 (metadata leakage) with folds grouped by lineage. `work/remote/stage4_audit.py` calls `_cv_auc` without `groups` for 4.4, so the reported maximum of 0.341 is biased low. Update Sec. 3 with the grouped value. | Release audits (stage 4/5) |
| 13c | Cite the Battiato-style block hash and, if the change-detection paragraph keeps a pointer to them, CAAA (CVPR 2024) and DMVN, after verifying the entries; none is in `refs.bib` yet. | Writing |

## Writing and submission

| # | item | owner |
|---|---|---|
| 14 | Compile (no TeX on the drafting machine), fix overfull boxes, and confirm the 8-page limit. Estimate after this revision: ≈ 8–8.3 pages. Trim in this order if over: Table 4 caption; the zero-shot sentence in Sec. 5.1; the localisation threshold sentence; the change-detection paragraph's SAHI sentence. Check that Table 4 (11 columns, `\footnotesize`) fits `\textwidth`; if not, drop the "untouched" column into the caption or go to `\scriptsize`. | Writing |
| 15 | Final teaser: start from `figures/teaser_draft.pdf` (`\teaserdrafttrue`), add each image's detector verdict. | Figures |
| 16 | Anonymity: rename and gate the public repositories or accept the risk; build the supplementary archive (subset, loader, datasheet) and check it for names; keep `\anonlink` as a placeholder. | Release workstream |
| 17 | Supplementary: write the datasheet, licence table, per-modality operating-point tables (from `data/operating_points.csv`), the oracle-mask figure (`figures/fig_oracle.pdf`, moved out of the main text) and the box audit, as outlined in `sec/X_suppl.tex`. | Writing |
| 18 | Optional, if time allows: the oracle-mask models' test tables are sealed; open them only if the paper needs test numbers for that analysis, and log the opening. | E0b (oracle mask) |
| 19 | Before submission, disable the visible `\TODO` / `\PENDING` markers (two lines in `preamble.tex`; one in `macros.tex`). | Writing |

## Closed in this revision

- Model decision (old item 3): settled by the round-3 verdict. No method section; the invariance-trained paired model is one baseline row (Sec. 5.3, Table 5).
- New-method test numbers (old item 4): not applicable.
- Probe positive control (old item 1) → **E1b**; MedForge fresh sample (old item 2) → **E3b**.
