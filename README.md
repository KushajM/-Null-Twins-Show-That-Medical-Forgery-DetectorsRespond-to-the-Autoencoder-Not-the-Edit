# CVPR 2027 draft — dataset-first paper

First full draft of the CVPR 2027 main-track submission (registration Nov 10, 2026; paper Nov 16;
supplementary Nov 23; all AoE). Review (anonymous) mode, 8 pages plus references.

## Template

- Official kit: <https://github.com/cvpr-org/author-kit>, branch `main` at commit `2917585`
  (2026-05-28). **No CVPR 2027 kit exists yet** (checked 2026-10-01: newest release tag is
  `CVPR2026-v1(latex)`, and `main` carries small post-release fixes to it). This is the **CVPR 2026
  kit**; `\confYear` is set to 2027 in `main.tex`. Swap in the 2027 `cvpr.sty` when it appears.
- Kit files copied unchanged: `cvpr.sty`, `ieeenat_fullname.bst`, `preamble.tex`.
  `kit_main_original.tex` and `sec/kit_X_suppl_original.tex` are the kit's originals, kept for reference.
- Project macros are in `macros.tex` (dataset name, anonymous-link placeholder, teaser switch).

## Build

No TeX distribution is installed on this machine, so **the draft has not been compiled**.
Build with any TeX Live / MiKTeX / Overleaf setup:

```
latexmk -pdf main.tex        # or: pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Instead of compiling, `scripts/check_tex.py` checks citations against `refs.bib`, `\cref` targets,
brace balance, banned (identifying or private) terms, and that every number in the body has a
`% src:` comment. It passes; the only lines it flags are protocol constants (0.5 = chance, the 95%
TPR rule) and layout lengths.

**Length estimate (after the round-3 revision):** about 5,800 words of running text (abstract to
conclusion, ethics included, tables and captions excluded), plus 7 tables (three full-width: datasets,
main benchmark, operating points; four single-column: MedForge, reference-verification baselines,
oracle mask, localisation) and 3 figures (teaser strip,
the full-width MedForge figure, the single-column operating-point heatmap). That comes to roughly
8–8.3 pages before references. Trim order is in `TODO.md` item 14.

## Layout

| path | content |
|---|---|
| `main.tex` | document; inputs `fig/teaser.tex`, `sec/0_abstract.tex` … `sec/7_limitations.tex` |
| `sec/X_suppl.tex` | supplementary outline (datasheet, licence table, per-modality tables); uncomment in `main.tex` |
| `refs.bib` | bibliography; `% UNVERIFIED` marks fields that could not be confirmed |
| `figures/fig_medforge.pdf` | Fig. 2, MedForge: Reasoner verdicts per modality (round-3 box audit) and twin AUCs (`work/e0/out_local/e2/`) |
| `figures/fig_operating.pdf` | Fig. 3, worst FPR per modality at each detector's calibration threshold (round-3 step 1) |
| `figures/fig_oracle.pdf` | oracle mask by edit family and modality (calibration); moved to the supplementary material |
| `figures/teaser_draft.pdf` | draft teaser built from our own release images (`work/e0/out_local/figsrc/`) |
| `figures/*_preview.png` | PNG renders of the figure PDFs, for quick viewing |
| `data/` | tidy CSVs derived from the score parquets (incl. `operating_points.csv`, `paired_family_test_auc.csv`), plus `derive_numbers.log` |
| `scripts/derive_numbers.py` | recomputes and cross-checks numbers from score parquets; writes `data/` |
| `scripts/make_figures.py` | builds every figure from result files (needs `derive_numbers.py` first) |
| `scripts/verify_refs.py` | arXiv lookups for the bibliography (`verify_refs_log.txt`) |
| `scripts/check_tex.py` | static checks (see Build) |
| `TODO.md` | every pending item with its owner experiment |

Rebuild the numbers and figures from the project root (CPU only, a few seconds):

```
.venv-mdf\Scripts\python.exe paper\scripts\derive_numbers.py
.venv-mdf\Scripts\python.exe paper\scripts\make_figures.py
```

`matplotlib` was installed into `.venv-mdf` for the plots; nothing else was installed.

## Number traceability

Every number in the text and tables carries a trailing LaTeX comment `% src: <file>` with a path
relative to the project root. Numbers marked "derived" were recomputed by
`scripts/derive_numbers.py` from score parquets under `work/e0/out_local/scores*/` and `e2/`; its
log shows each recomputation matching the original report (all point estimates reproduce exactly;
seed SDs match once population SD is used, as the results sheet does).

Test numbers are used only for fixed models already opened in `TEST_LOG.md` or reported in
earlier fixed-model tables; the oracle-mask models are read on calibration only (their test tables
stay sealed). Nothing was selected on test.

Round-3 numbers (operating points, box audit, standardised subtraction, λ rule) cite
`docs/council/round3/experiments/local/` (`R3_STEP1_REPORT.md` and its CSVs/JSON), which reproduce
every † number in the round-3 verdict. `derive_numbers.py` copies `r3_operating_points.csv` to
`data/operating_points.csv` with cross-checks, and computes the p2 / p3 test AUCs
(`data/paired_family_test_auc.csv`) from parquets that round-3 step 1 had already opened (TEST_LOG,
2026-10-01 21:46); λ was fixed on calibration before those AUCs were read. A number that appears only
in the verdict is marked `% src: round3/council_verdict.md (pending r3_step1)` and listed in `TODO.md`.
The threshold-transfer headline (5.5% vs 61–91%) and `sdxl_threshold_transfer.csv` were removed.

### Discrepancies found in the sources, and what the draft uses

1. **NPR / UniFD / AEROBLADE B-vs-C.** `work/e0/remote/e9_final_table.py` matches task names with
   `startswith("B_vs_C")`, which also matches `B_vs_C_gan` and overwrites the SD value. So the
   programme summary's B-vs-C for NPR (0.5079) and UniFD (0.5116) are the LaMa-twin values. The
   draft uses the SD values from `e6_baselines_v2.csv` (NPR 0.4999, UniFD 0.5112). AEROBLADE's
   per-task CSV is not local, so its 0.4997 is flagged in Table 2 pending a re-pull.
2. **NPR and UniFD are not zero-shot.** They were fitted on A-vs-C on the training split (4,619
   images), as in their papers; only AEROBLADE is training-free. The draft says so.
3. **MedForge Mesorch JPEG twins.** The results README lists V0/V1 `N_jpeg` as 0.5012 / 0.5047;
   `e2/e2_table.csv` has 0.4970 / 0.4966 (the README seems to predate the real-only filter). The
   draft uses the CSV.
4. **Reasoner hard-label rate for untouched scans.** `e2_table.csv` gives 0.2094 for R and N_jpeg
   because those rows include the 48 forged controls; restricted to real scans it is 1/186 = 0.0054,
   matching the README's 0.5%. The draft uses the parquet-derived real-only rates.
5. **Training-set scaling.** The dossier says 0.732 / 0.727 / 0.743; `table_main.csv` says
   0.735 / 0.732 / 0.743. The draft uses `table_main.csv`.
6. **PSCC-Net zero-shot** scores are degenerate under `score_max`, and the harness falls back to
   `score_mean`; the draft uses the harness table, not a re-derivation.
7. **"Removal is a finding problem"** holds for CT removal (oracle +0.29), while non-CT removal is
   already 0.93–0.99 without the mask; CT injection gains nothing. The draft states it per family
   and per modality rather than as a blanket claim.
8. **Fingerprint share** is defined as in `E1_REPORT.md`: (AUC(A,B) − 0.5)/(AUC(A,C) − 0.5).
   "68–93% across five backbones" is really four fine-tuned backbones that learned the task
   (PSCC-Net did not); the draft says four.
9. **Paired-model margin over twin-trained Mesorch.** The summary's +0.2325 belongs to the gated
   variant; the model the paper uses (no gate) is +0.241 [0.224, 0.259] (`e3_table_bar.csv`). The
   draft does not quote either.
10. **Splits.** The released splits (1,944 / 823 / 1,189) differ from the leak-free benchmark
    splits (1,983 / 822 / 1,151, `split_freeze.json`). The paper describes the leak-free splits, so
    the release must ship them (see TODO).
11. **Frozen-generator probe CI.** README [0.4978, 0.5190] vs `E1_REPORT.md` [0.4969, 0.5185]; the
    draft uses the report.

Round-3 verdict vs step-1 files (the draft uses step 1 in every case):

12. **Paired baseline on NL-means / SDXL-VAE.** Verdict 75% / 69% (injection lineages only); step 1
    78.4% / 70.6% on all lineages, which is the table's convention. CT 98.8% / 96.7% (verdict 99% / 97%).
13. **"22 of 30 normal brains".** The 30 are normal scans of both modalities: brain 12/16, fundus
    10/14. The draft says "22 of the 30 sampled scans labelled normal (12 of 16 brains)".
14. **Subtraction under autoencoder ops.** Verdict 98–99.8% is the test range; the draft quotes the
    calibration values 99.3% (VQ) and 98.4% (SDXL), like every other calibration column.
15. **Per-modality gap to the paired baseline.** The verdict's "+0.008; endoscopy +0.069" mixes the
    standardised pooled gap with the raw endoscopy gap. Standardised endoscopy is +0.074, raw +0.069;
    CT is −0.033 either way. The draft quotes standardised (+0.008, +0.074, −0.033).
16. **Oracle CT injection.** Verdict 0.547 → 0.534; the 3-seed mean in `data/oracle_calibration_3seed.csv`
    is 0.5455 → 0.5337, so the draft keeps 0.546 → 0.534.
17. **Standardised subtraction** 0.976 (verdict) vs 0.9755 (step 1): rounding.
18. **Peer-review figures not used.** `peer_reviews.md` quotes subtraction 45% and the paired baseline
    7.5% on test SD twins; step 1 gives 46.7% and 13.6%, which the draft uses.

## Anonymity

- No author, lab, or Hugging Face / GitHub user names appear anywhere in this folder; the old
  dataset name appears only where the MICCAI 2025 dataset of that name is meant.
- The dataset name is behind `\dataset` (`macros.tex`); the anonymous link is `\anonlink`, a
  placeholder that prints "[anonymous link withheld for review]".
- Risk to resolve before submission: the existing public dataset repository carries the same
  statistics as the paper (3,956 lineages, six modalities), so a reviewer can find it by content.
  Rename and gate it, or accept the risk explicitly (see `docs/council/round2/landscape_and_odds.md`, Sec. 3).

## Dataset-name candidates

Each was searched on 2026-10-01 for an existing medical-imaging or forensics dataset of that name;
none was found.

| name | idea | search result |
|---|---|---|
| **NullTwin-Med** (current macro) | names the control directly | no dataset or model of that name |
| **LesionTwin** | lesion edits, each with a twin | no dataset of that name (unrelated "digital twin" lesion-simulation work exists, e.g. SYN-LUNGS) |
| **PlaceboEdit** | a placebo-controlled edit: the twin gets the procedure without the active ingredient | no dataset of that name |

Rejected: "MedSham" (a UK company name), "ShamScan" (the name of a medical imaging centre).
Also clear: "MedDoppel". Re-run the search on the final name just before registration.

## Teaser figure

The paper shows a placeholder box describing the intended teaser (source, null twin, forgery,
mask, and the two difference maps |A − B| and |B − forgery|). Assessment of the suggested images:

- `docs/figures/removal_examples.png` has real / removal / null twin / |real − removal| for six
  removal lineages, so it lacks a mask column and an injection example, and it shows *failed*
  removals (an MRI crescent void, ultrasound calipers surviving). Useful for the limitations or the
  supplementary, not as a teaser.
- `work/e0/out_local/gen_sdxl/contact_sheet.png` is a 512-px QC sheet (A | B_SDXL | C/D_SDXL | B_SD |
  C/D_SD) with ~100-px thumbnails and no mask or difference map. Not usable as a teaser.
- Instead, `scripts/make_figures.py` builds `figures/teaser_draft.pdf` from the full-resolution
  release images in `work/e0/out_local/figsrc/` (MRI injection, ultrasound removal, CT injection),
  with both difference maps on the same ×4 scale. Set `\teaserdrafttrue` in `macros.tex` to use it.
  No MedForge image may appear (C-UDA).
