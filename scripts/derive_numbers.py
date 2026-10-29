"""Derive and cross-check the numbers the paper quotes.

Reads only existing result files (score parquets and report CSVs under
work/e0/out_local/ and docs/council/round2/experiments/). Writes tidy CSVs to
paper/data/. Nothing is trained, nothing is selected, and no split is opened
that TEST_LOG.md does not already record:

  * test rows are read only for fixed models already logged as opened
    (V0, V1, distilled V1, PAIR-NET, zero-shot baselines: TEST_LOG row 1);
  * the oracle-mask models (E0b) are read on CALIBRATION only; their test
    tables stay sealed;
  * p2 / p3 test parquets were opened by round-3 step 1 (TEST_LOG row of
    2026-10-01 21:46); lambda was fixed on calibration before their AUCs
    are read here.

Run:  .venv-mdf\\Scripts\\python.exe paper\\scripts\\derive_numbers.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
E0 = os.path.join(ROOT, "work", "e0")
OUT = os.path.join(E0, "out_local")
DATA = os.path.join(ROOT, "paper", "data")
sys.path.insert(0, E0)
from adapter.mdf_index import TASKS, MODALITIES, qualifies  # noqa: E402
from eval.metrics import auc  # noqa: E402

os.makedirs(DATA, exist_ok=True)
LOG = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def frame(df, task):
    neg, pos, which = TASKS[task]
    s = df[df.arm.isin([neg, pos])].copy()
    s = s[np.fromiter((qualifies(f, which) for f in s.family), bool, len(s))]
    s["y"] = (s.arm == pos).astype(int)
    return s


def auc_of(df, task, modality="ALL", col="score_max"):
    f = frame(df, task)
    if modality != "ALL":
        f = f[f.modality == modality]
    f = f.dropna(subset=[col])
    if f.empty or f.y.nunique() < 2:
        return np.nan, 0
    return float(auc(f.y.to_numpy(int), f[col].to_numpy(float))), len(f)


def check(name, got, want, tol=6e-4):
    ok = abs(got - want) <= tol
    say("  %-58s got %.4f  want %.4f  %s" % (name, got, want, "OK" if ok else "MISMATCH"))
    return ok


def load(rel):
    return pd.read_parquet(os.path.join(OUT, rel))


# --------------------------------------------------------------------------
# 1. Main benchmark, TEST, fixed models (already opened, TEST_LOG row 1)
# --------------------------------------------------------------------------
say("=" * 78)
say("1. Main benchmark (test, fixed models)")
MODELS = {
    "Mesorch (zero-shot)": "scores/scores_zeroshot_mesorch.parquet",
    "TruFor (zero-shot)": "scores/scores_zeroshot_trufor.parquet",
    "IML-ViT (zero-shot)": "scores/scores_zeroshot_iml_vit.parquet",
    "MVSS-Net (zero-shot)": "scores/scores_zeroshot_mvss_net.parquet",
    "PSCC-Net (zero-shot)": "scores/scores_zeroshot_pscc_net.parquet",
    "IML-ViT (standard)": "scores/scores_ft_iml_vit_v0.parquet",
    "TruFor (standard)": "scores/scores_ft_trufor_v0.parquet",
    "MVSS-Net (standard)": "scores/scores_ft_mvss_net_v0.parquet",
    "Mesorch (standard)": "scores/scores_ft_mesorch_v0.parquet",
    "Mesorch + null-twin negatives": "scores/scores_ft_mesorch_v1.parquet",
    "Mesorch + null-twin, distilled": "scores/scores_ft_mesorch_d1__a2p00.parquet",
    "Paired (FC-Siam-diff)": "scores/scores_ft_pairnet_nogate_p1n.parquet",
    "Paired, null discarded": "scores/scores_ft_pairnet_single_p1n.parquet",
}
TASK_COLS = ["a_vs_c", "b_vs_c", "b_vs_d", "a_vs_cm", "a_vs_b"]
rows = []
for name, rel in MODELS.items():
    g = load(rel)
    g = g[g.split == "test"]
    for t in TASK_COLS:
        for m in ["ALL"] + MODALITIES:
            v, n = auc_of(g, t, m)
            rows.append(dict(model=name, task=t, modality=m, auc=v, n=n))
main = pd.DataFrame(rows)
main.to_csv(os.path.join(DATA, "main_benchmark_test.csv"), index=False)
piv = main[main.modality == "ALL"].pivot(index="model", columns="task", values="auc")
say(piv[TASK_COLS].round(4).to_string())

say("Cross-checks against the reports:")
A = lambda mdl, t, m="ALL": float(main[(main.model == mdl) & (main.task == t) & (main.modality == m)].auc.iloc[0])
check("V0 a_vs_c (Deepfakedoctillnow p3: 0.9633)", A("Mesorch (standard)", "a_vs_c"), 0.9633)
check("V0 b_vs_c (p3: 0.5359)", A("Mesorch (standard)", "b_vs_c"), 0.5359)
check("V0 a_vs_b (E1_REPORT: 0.9293)", A("Mesorch (standard)", "a_vs_b"), 0.9293)
check("V1 b_vs_c (p3: 0.7428)", A("Mesorch + null-twin negatives", "b_vs_c"), 0.7428)
check("V1 b_vs_d (0.7786)", A("Mesorch + null-twin negatives", "b_vs_d"), 0.7786)
check("V1 a_vs_cm (0.9312)", A("Mesorch + null-twin negatives", "a_vs_cm"), 0.9312)
check("V1 a_vs_b (E3_REPORT: 0.7036)", A("Mesorch + null-twin negatives", "a_vs_b"), 0.7036)
check("distilled b_vs_c (0.7679)", A("Mesorch + null-twin, distilled", "b_vs_c"), 0.7679)
check("PAIR-NET b_vs_c (0.9840)", A("Paired (FC-Siam-diff)", "b_vs_c"), 0.9840)
check("PAIR-NET b_vs_d (0.9961)", A("Paired (FC-Siam-diff)", "b_vs_d"), 0.9961)
check("PAIR-NET a_vs_cm (0.9882)", A("Paired (FC-Siam-diff)", "a_vs_cm"), 0.9882)
check("PAIR-NET CT b_vs_c (0.9268)", A("Paired (FC-Siam-diff)", "b_vs_c", "ct"), 0.9268)
check("A2 null discarded b_vs_c (0.7255)", A("Paired, null discarded", "b_vs_c"), 0.7255)
check("V1 CT b_vs_c (0.5673)", A("Mesorch + null-twin negatives", "b_vs_c", "ct"), 0.5673)
check("V0 X-ray b_vs_c (0.4997)", A("Mesorch (standard)", "b_vs_c", "xray"), 0.4997)

# fingerprint share: FS = (AUC_AB - 0.5) / (AUC_AC - 0.5)   (E1_REPORT.md def.)
say("Fingerprint share FS = (AUC(A,B)-0.5)/(AUC(A,C)-0.5):")
fs = []
for name in MODELS:
    ac, ab = A(name, "a_vs_c"), A(name, "a_vs_b")
    v = (ab - 0.5) / (ac - 0.5) if ac - 0.5 > 0.05 else np.nan
    fs.append(dict(model=name, a_vs_c=ac, a_vs_b=ab, b_vs_c=A(name, "b_vs_c"), fingerprint_share=v))
fs = pd.DataFrame(fs)
fs.to_csv(os.path.join(DATA, "fingerprint_share_test.csv"), index=False)
say(fs.round(4).to_string())

# --------------------------------------------------------------------------
# 2. Oracle-mask study, CALIBRATION only, 3 seeds
# --------------------------------------------------------------------------
say("=" * 78)
say("2. Oracle mask (calibration only; E0b test tables stay sealed)")
SEEDED = {
    "Mesorch + null-twin negatives": ["scores/scores_ft_mesorch_v1.parquet",
                                      "scores/scores_ft_mesorch_v1__s43.parquet",
                                      "scores/scores_ft_mesorch_v1__s44.parquet"],
    "oracle mask channel": ["scores_e0x/scores_e0b_mask_s42.parquet",
                            "scores_e0x/scores_e0b_mask_s43.parquet",
                            "scores_e0x/scores_e0b_mask_s44.parquet"],
    "zero mask channel (control)": ["scores_e0x/scores_e0b_zeros_s42.parquet"],
}
orows = []
for name, rels in SEEDED.items():
    for si, rel in enumerate(rels):
        g = load(rel)
        g = g[g.split == "calibration"]
        for t in ["b_vs_c", "b_vs_d", "a_vs_b"]:
            for m in ["ALL"] + MODALITIES:
                v, n = auc_of(g, t, m)
                orows.append(dict(model=name, seed=42 + si, task=t, modality=m, auc=v, n=n))
# frozen V1 scored only inside the true mask (E0b-0), seed 42
g = load("scores_e0x/scores_e0b_v1pool.parquet")
g = g[g.split == "calibration"]
for t in ["b_vs_c", "b_vs_d", "a_vs_b"]:
    for m in ["ALL"] + MODALITIES:
        v, n = auc_of(g, t, m, col="score_max_in")
        orows.append(dict(model="frozen, max inside true mask", seed=42, task=t, modality=m, auc=v, n=n))
orc = pd.DataFrame(orows)
orc.to_csv(os.path.join(DATA, "oracle_calibration_by_seed.csv"), index=False)
# population SD over seeds (ddof=0), the convention of the README results sheet
agg = (orc.groupby(["model", "task", "modality"]).auc
       .agg(mean="mean", std=lambda x: float(np.std(x, ddof=0)), count="count").reset_index())
agg.to_csv(os.path.join(DATA, "oracle_calibration_3seed.csv"), index=False)
say(agg[agg.modality.isin(["ALL", "ct"])].round(4).to_string())

G = lambda mdl, t, m="ALL": agg[(agg.model == mdl) & (agg.task == t) & (agg.modality == m)].iloc[0]
say("Cross-checks against README single results sheet:")
check("oracle 3-seed b_vs_c mean (0.7938)", G("oracle mask channel", "b_vs_c")["mean"], 0.7938)
check("oracle 3-seed b_vs_c SD (0.0021)", G("oracle mask channel", "b_vs_c")["std"], 0.0021, 3e-4)
check("oracle 3-seed CT b_vs_c mean (0.5337)", G("oracle mask channel", "b_vs_c", "ct")["mean"], 0.5337)
check("oracle 3-seed b_vs_d mean (0.9364)", G("oracle mask channel", "b_vs_d")["mean"], 0.9364)
check("V1 3-seed b_vs_c mean (0.7242)", G("Mesorch + null-twin negatives", "b_vs_c")["mean"], 0.7242)
check("V1 3-seed b_vs_c SD (0.0042)", G("Mesorch + null-twin negatives", "b_vs_c")["std"], 0.0042, 3e-4)
check("V1 3-seed b_vs_d mean (0.7857)", G("Mesorch + null-twin negatives", "b_vs_d")["mean"], 0.7857)
check("V1 3-seed CT b_vs_c mean (0.5455)", G("Mesorch + null-twin negatives", "b_vs_c", "ct")["mean"], 0.5455)
check("V1 3-seed a_vs_b mean (0.7079)", G("Mesorch + null-twin negatives", "a_vs_b")["mean"], 0.7079)
check("oracle 3-seed CT b_vs_c SD (0.0140)", G("oracle mask channel", "b_vs_c", "ct")["std"], 0.0140, 3e-4)
check("oracle 3-seed b_vs_d SD (0.0058)", G("oracle mask channel", "b_vs_d")["std"], 0.0058, 3e-4)
check("oracle s42 CT b_vs_d (e0b_calibration.csv: 0.8196)",
      float(orc[(orc.model == "oracle mask channel") & (orc.seed == 42) & (orc.task == "b_vs_d")
                & (orc.modality == "ct")].auc.iloc[0]), 0.8196)
check("frozen V1 max-in b_vs_c (0.7228)", G("frozen, max inside true mask", "b_vs_c")["mean"], 0.7228)
check("zero-channel ctrl b_vs_c (0.7259)", G("zero mask channel (control)", "b_vs_c")["mean"], 0.7259)

# --------------------------------------------------------------------------
# 3. MedForge Reasoner hard-label rates, restricted to real sources
# --------------------------------------------------------------------------
say("=" * 78)
say("3. MedForge-Reasoner hard labels (README: R 0.005, N_sd 0.925, N_sdxl 0.720)")
r = load("e2/scores_reasoner.parquet")
hl = []
for arm in ["R", "N_jpeg", "N_sd", "N_sdxl"]:
    s = r[(r.arm == arm) & (r.kind == "real")]
    hl.append(dict(arm=arm, kind="real", n=len(s), deepfake_rate=float(s.hard_label.mean()),
                   n_brain_mri=int((s.modality == "brain-mri").sum()),
                   n_fundus=int((s.modality == "fundus").sum())))
s = r[(r.arm == "R") & (r.kind == "forged")]
hl.append(dict(arm="F (MedForge forgery)", kind="forged", n=len(s), deepfake_rate=float(s.hard_label.mean()),
               n_brain_mri=int((s.modality == "brain-mri").sum()), n_fundus=int((s.modality == "fundus").sum())))
for arm in ["R", "N_jpeg", "N_sd", "N_sdxl"]:
    for mod in ["brain-mri", "fundus"]:
        s = r[(r.arm == arm) & (r.kind == "real") & (r.modality == mod)]
        hl.append(dict(arm=arm, kind="real/" + mod, n=len(s), deepfake_rate=float(s.hard_label.mean())))
hl = pd.DataFrame(hl)
hl.to_csv(os.path.join(DATA, "medforge_reasoner_hardlabel.csv"), index=False)
say(hl.round(4).to_string())
say("parse failures:", int((~r.parsed).sum()), "of", len(r))

# fingerprint share for MedForge-Reasoner from e2_table.csv
e2 = pd.read_csv(os.path.join(OUT, "e2", "e2_table.csv"))
def e2a(sc, arm, mod="ALL"):
    x = e2[(e2.scorer == sc) & (e2.arm == arm) & (e2.modality == mod) & (e2.kind != "hard_label_rate")]
    return float(x.auc.iloc[0])
fs_r = (e2a("Reasoner", "N_sd") - 0.5) / (e2a("Reasoner", "F") - 0.5)
fs_rx = (e2a("Reasoner", "N_sdxl") - 0.5) / (e2a("Reasoner", "F") - 0.5)
say("Reasoner fingerprint share, SD null: %.4f; SDXL null: %.4f" % (fs_r, fs_rx))
json.dump(dict(reasoner_fs_sd=fs_r, reasoner_fs_sdxl=fs_rx),
          open(os.path.join(DATA, "medforge_fingerprint_share.json"), "w"), indent=1)

# --------------------------------------------------------------------------
# 4. Operating points (round-3 step 1), copied and cross-checked
# --------------------------------------------------------------------------
say("=" * 78)
say("4. Operating points (docs/council/round3/experiments/local/r3_operating_points.csv)")
R3 = os.path.join(ROOT, "docs", "council", "round3", "experiments", "local")
op = pd.read_csv(os.path.join(R3, "r3_operating_points.csv"))
op.to_csv(os.path.join(DATA, "operating_points.csv"), index=False)
O = lambda mdl, col, m="ALL": float(op[(op.model == mdl) & (op.modality == m)][col].iloc[0])
check("V1 FPR cal SD nulls (0.940)", O("V1", "fpr_cal_SD_null"), 0.940)
check("p1n FPR test SD nulls (0.136)", O("p1n", "fpr_test_SD_null"), 0.136)
check("sub_raw FPR SD nulls cal (0.438)", O("sub_raw", "fpr_cal_SD_null"), 0.438)
check("sub_raw FPR SD nulls test (0.467)", O("sub_raw", "fpr_test_SD_null"), 0.467)
check("p3_0.03 worst pooled (0.088)", O("p3_0.03", "worst_fpr"), 0.088)
check("p3_0.03 CT SDXL-VAE (0.205)", O("p3_0.03", "fpr_sdxlvae", "ct"), 0.205)
check("p3_0.03 CT TPR (0.800)", O("p3_0.03", "tpr_cal_C_sd", "ct"), 0.800)
check("p1n CT NL-means (0.988)", O("p1n", "fpr_nlmeans", "ct"), 0.988)

# p2 / p3 test AUCs. Descriptive only: lambda was fixed on calibration by the
# pre-registered rule (r3_lambda_preregistration.json) before these were read.
say("p2 / p3 test AUCs (lambda fixed on calibration; nothing selected here)")
PFAM = {
    "Paired (FC-Siam-diff)": "scores/scores_ft_pairnet_nogate_p1n.parquet",
    "p2": "scores/scores_ft_pairnet_nogate_p2.parquet",
    "p3 lam=0.03": "scores/scores_ft_pairnet_nogate_p3__lam0p03.parquet",
    "p3 lam=0.1": "scores/scores_ft_pairnet_nogate_p3__lam0p1.parquet",
    "p3 lam=0.3": "scores/scores_ft_pairnet_nogate_p3__lam0p3.parquet",
}
prow = []
for name, rel in PFAM.items():
    g = load(rel)
    g = g[g.split == "test"]
    for t in ["b_vs_c", "b_vs_d", "a_vs_b"]:
        for m in ["ALL"] + MODALITIES:
            v, n = auc_of(g, t, m)
            prow.append(dict(model=name, task=t, modality=m, auc=v, n=n))
pf = pd.DataFrame(prow)
pf.to_csv(os.path.join(DATA, "paired_family_test_auc.csv"), index=False)
say(pf[pf.modality.isin(["ALL", "ct"])].pivot_table(index="model", columns=["task", "modality"],
                                                    values="auc").round(4).to_string())
P = lambda mdl, t, m="ALL": float(pf[(pf.model == mdl) & (pf.task == t) & (pf.modality == m)].auc.iloc[0])
check("p1n b_vs_c via this block (0.9840)", P("Paired (FC-Siam-diff)", "b_vs_c"), 0.9840)
stale = os.path.join(DATA, "sdxl_threshold_transfer.csv")
if os.path.exists(stale):
    os.remove(stale)

open(os.path.join(DATA, "derive_numbers.log"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
say("wrote", DATA)
