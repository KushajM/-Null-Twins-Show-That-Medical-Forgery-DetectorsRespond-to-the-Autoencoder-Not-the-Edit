"""Build the paper's result figures as PDFs.

Inputs are result files only (no image of MedForge is ever plotted: C-UDA):
  * work/e0/out_local/e2/e2_table.csv                    -> fig_medforge.pdf
  * docs/council/round3/experiments/local/r3_box_audit.csv -> fig_medforge.pdf
      (Reasoner verdicts per modality, from the saved Reasoner outputs)
  * paper/data/operating_points.csv                      -> fig_operating.pdf
      (copied from docs/council/round3/experiments/local/r3_operating_points.csv)
  * paper/data/oracle_calibration_by_seed.csv            -> fig_oracle.pdf
      (derived from work/e0/out_local/scores*/ parquets, calibration only)
  * work/e0/out_local/figsrc/*.png (our own release arms) -> teaser_draft.pdf

Run derive_numbers.py first.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "work", "e0", "out_local")
DATA = os.path.join(ROOT, "paper", "data")
FIG = os.path.join(ROOT, "paper", "figures")
R3 = os.path.join(ROOT, "docs", "council", "round3", "experiments", "local")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
})
COL_W = 3.25  # inches, CVPR single column
C_RED, C_GREY, C_BLUE, C_GOLD, C_GREEN = "#c0392b", "#9aa0a6", "#2e6da4", "#d4a017", "#3c8d5a"


def label_bars(ax, bars, fmt="{:.3f}", dy=0.012, fs=6):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + dy, fmt.format(h),
                ha="center", va="bottom", fontsize=fs)


# --------------------------------------------------------------- MedForge
def fig_medforge():
    e2 = pd.read_csv(os.path.join(OUT, "e2", "e2_table.csv"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL_W * 2.05, 1.75),
                               gridspec_kw=dict(width_ratios=[1.05, 1.0], wspace=0.28))

    box = pd.read_csv(os.path.join(R3, "r3_box_audit.csv"))
    arms = [("R", "real", "unedited\nscan"), ("N_jpeg", "real", "JPEG q95\nonly"),
            ("N_sd", "real", "SD auto-\nencoder"), ("N_sdxl", "real", "SDXL auto-\nencoder"),
            ("R", "forged", "MedForge\nforgery")]
    w = 0.36
    for i, (mod, lab, c) in enumerate([("brain-mri", "brain MRI", "#4d4d4d"), ("fundus", "fundus", "#a6a6a6")]):
        vals = [100 * float(box[(box.modality == mod) & (box.arm == k) & (box.kind == kind)].fake_rate.iloc[0])
                for k, kind, _ in arms]
        x = np.arange(len(arms)) + (i - 0.5) * w
        bars = a.bar(x, vals, w * 0.92, color=c, label=lab)
        for bb, v in zip(bars, vals):
            a.text(bb.get_x() + bb.get_width() / 2, v + 2, "%.0f" % v if v >= 99.95 else "%.1f" % v,
                   ha="center", va="bottom", fontsize=5.0)
    a.set_xticks(range(len(arms)))
    a.set_xticklabels([t for _, _, t in arms])
    a.set_ylim(0, 118)
    a.set_yticks([0, 25, 50, 75, 100])
    a.set_ylabel("flagged as deepfake (%)")
    a.legend(frameon=False, loc="upper left", ncol=2, handlelength=1.0, borderaxespad=0.0,
             columnspacing=0.9, bbox_to_anchor=(0.0, 1.03))
    a.set_title("(a) MedForge-Reasoner verdicts; no pixel edited in the middle three", loc="left")

    scorers = [("Reasoner", "MedForge-Reasoner", C_RED),
               ("V0", "Mesorch (standard)", C_GOLD),
               ("V1", "Mesorch + null-twin neg.", C_GREEN)]
    mods = [("brain-mri", "brain MRI"), ("fundus", "fundus")]
    w = 0.26
    for i, (sc, lab, c) in enumerate(scorers):
        ys, lo, hi = [], [], []
        for m, _ in mods:
            r = e2[(e2.scorer == sc) & (e2.arm == "N_sd") & (e2.modality == m) & (e2.kind == "null_arm")].iloc[0]
            ys.append(r.auc); lo.append(r.auc - r.lo); hi.append(r.hi - r.auc)
        x = np.arange(len(mods)) + (i - 1) * w
        bb = b.bar(x, ys, w * 0.92, color=c, label=lab, yerr=[lo, hi],
                   error_kw=dict(lw=0.6, capsize=1.5))
        for xx, yy, hh in zip(x, ys, hi):
            b.text(xx, yy + hh + 0.01, "%.3f" % yy, ha="center", va="bottom", fontsize=5.5)
    b.axhline(0.5, color="k", lw=0.6, ls=":")
    b.set_xticks(range(len(mods)))
    b.set_xticklabels([t for _, t in mods])
    b.set_ylim(0.4, 1.17)
    b.set_ylabel("AUC (unedited vs. SD twin)")
    b.set_title("(b) Separating an unedited scan from its SD-autoencoder twin", loc="left")
    b.legend(frameon=False, loc="upper center", ncol=3, handlelength=1.0, borderaxespad=0.0,
             columnspacing=0.9, bbox_to_anchor=(0.5, 1.02))
    fig.savefig(os.path.join(FIG, "fig_medforge.pdf"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# ------------------------------------------------------- operating points
OP_ROWS = [("V0", "Mesorch, standard"), ("V1", "Mesorch + null twins"),
           ("V1d", "Mesorch + null twins, distilled\u2021"),
           ("sub_raw", "subtraction"), ("sub_std", "subtraction, standardised"),
           ("p1n", "paired (FC-Siam-diff)\u2021"), ("p2", "+ benign negatives"),
           ("p3_0.03", "+ invariance, \u03bb=0.03 (rule)"), ("p3_0.1", "+ invariance, \u03bb=0.1")]
OP_MODS = [("ALL", "all"), ("ct", "CT"), ("endoscopy", "endo."), ("histopathology", "histo."),
           ("mri", "MRI"), ("ultrasound", "US"), ("xray", "X-ray")]


def fig_operating():
    """Worst FPR over negative types at the pooled calibration 95%-TPR threshold."""
    d = pd.read_csv(os.path.join(DATA, "operating_points.csv"))
    M = np.array([[float(d[(d.model == k) & (d.modality == m)].worst_fpr.iloc[0]) for m, _ in OP_MODS]
                  for k, _ in OP_ROWS])
    fig, ax = plt.subplots(figsize=(COL_W, 2.05))
    im = ax.imshow(M, cmap="Reds", vmin=0, vmax=1, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, "%.0f" % (100 * v) if v >= 0.095 else "%.1f" % (100 * v), ha="center",
                    va="center", fontsize=5.6, color="white" if v > 0.6 else "black")
    ax.set_xticks(range(len(OP_MODS))); ax.set_xticklabels([t for _, t in OP_MODS])
    ax.set_yticks(range(len(OP_ROWS))); ax.set_yticklabels([t for _, t in OP_ROWS])
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for y in (2.5, 4.5):
        ax.axhline(y, color="white", lw=1.6)
    ax.axvline(0.5, color="white", lw=1.6)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_ticks([0, 0.5, 1]); cb.set_ticklabels(["0%", "50%", "100%"]); cb.ax.tick_params(labelsize=5.5, length=1.5)
    cb.outline.set_visible(False)
    fig.savefig(os.path.join(FIG, "fig_operating.pdf"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# ------------------------------------------------------------ oracle mask
def fig_oracle():
    """Per-modality oracle-mask gain, by edit family (calibration only)."""
    d = pd.read_csv(os.path.join(DATA, "oracle_calibration_by_seed.csv"))
    names = {"ALL": "all", "ct": "CT", "endoscopy": "endo.", "histopathology": "histo.",
             "mri": "MRI", "ultrasound": "US", "xray": "X-ray"}
    panels = [("b_vs_c", ["ALL", "ct", "endoscopy", "histopathology", "mri", "ultrasound", "xray"],
               "(a) injection: null twin vs. injected lesion (B-vs-C)"),
              ("b_vs_d", ["ALL", "ct", "endoscopy", "mri", "ultrasound"],
               "(b) removal: null twin vs. removed lesion (B-vs-D)")]
    models = [("Mesorch + null-twin negatives", "single image (3 seeds)", C_GREEN),
              ("oracle mask channel", "same, trained with the true mask (3 seeds)", C_BLUE)]
    fig, axes = plt.subplots(2, 1, figsize=(COL_W, 2.45),
                             gridspec_kw=dict(height_ratios=[1, 1], hspace=0.62))
    w = 0.36
    for ax, (task, mods, title) in zip(axes, panels):
        fz = [float(d[(d.model == "frozen, max inside true mask") & (d.task == task)
                      & (d.modality == mod)].auc.iloc[0]) for mod in mods]
        for i, (m, lab, c) in enumerate(models):
            ys, es = [], []
            for mod in mods:
                s = d[(d.model == m) & (d.task == task) & (d.modality == mod)].auc.to_numpy(float)
                ys.append(s.mean()); es.append(s.std(ddof=0))
            x = np.arange(len(mods)) + (i - 0.5) * w
            ax.bar(x, ys, w * 0.92, color=c, label=lab if ax is axes[0] else None, yerr=es,
                   error_kw=dict(lw=0.5, capsize=1.0))
            for j, (xx, yy, ee) in enumerate(zip(x, ys, es)):
                top = max(yy + ee, fz[j]) if i == 0 else yy + ee
                ax.text(xx, top + 0.012, "%.2f" % yy, ha="center", va="bottom", fontsize=4.6)
        ax.scatter(np.arange(len(mods)) - 0.5 * w, fz, marker="_", s=40, color="k", lw=1.0,
                   zorder=5, label="single image, read only inside the true mask" if ax is axes[0] else None)
        ax.axhline(0.5, color="k", lw=0.5, ls=":")
        ax.set_xticks(range(len(mods))); ax.set_xticklabels([names[m] for m in mods])
        ax.set_ylim(0.4, 1.1); ax.set_ylabel("AUC (calibration)")
        ax.set_title(title, loc="left", fontsize=6.5)
    fig.legend(frameon=False, ncol=2, loc="lower center", fontsize=5.3, handlelength=1.0,
               columnspacing=0.6, borderaxespad=0.0, bbox_to_anchor=(0.5, 0.955))
    fig.savefig(os.path.join(FIG, "fig_oracle.pdf"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# --------------------------------------------------------- teaser (draft)
def _crop_box(mask, scale=2.6, min_side=96):
    ys, xs = np.nonzero(mask > 0)
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    side = max(min_side, int(scale * max(ys.max() - ys.min(), xs.max() - xs.min())))
    h, w = mask.shape
    side = min(side, h, w)
    y0 = int(np.clip(cy - side / 2, 0, h - side)); x0 = int(np.clip(cx - side / 2, 0, w - side))
    return y0, x0, side


def fig_teaser_draft():
    src = os.path.join(OUT, "figsrc")
    rows = [("mri", "injection", "injection_sd", "MRI, injection"),
            ("ultrasound", "removal", "removal_sd", "ultrasound, removal"),
            ("ct", "injection", "injection_sd", "CT, injection")]
    cols = ["source (A)", "null twin (B)", "forgery (C / D)", "mask",
            "|A - B| x4\n(autoencoder only)", "|B - forgery| x4\n(the edit)"]
    fig, axes = plt.subplots(len(rows), len(cols), figsize=(COL_W * 2.05, 1.13 * len(rows)))
    for r, (mod, fam, arm, title) in enumerate(rows):
        L = lambda name: np.asarray(Image.open(os.path.join(src, "%s__%s__%s.png" % (mod, fam, name))).convert("L"), float)
        A, B, X = L("real"), L("null_sd"), L(arm)
        M = L("masks")
        y0, x0, s = _crop_box(M)
        cut = lambda im: im[y0:y0 + s, x0:x0 + s]
        panels = [cut(A), cut(B), cut(X), cut(M), np.abs(cut(A) - cut(B)) * 4, np.abs(cut(B) - cut(X)) * 4]
        for c, p in enumerate(panels):
            ax = axes[r, c]
            if c < 4:
                ax.imshow(p, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
            else:
                ax.imshow(np.clip(p, 0, 255), cmap="magma", vmin=0, vmax=255, interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            if r == 0:
                ax.set_title(cols[c], fontsize=6.5)
        axes[r, 0].set_ylabel(title, fontsize=6.5)
    fig.subplots_adjust(wspace=0.03, hspace=0.06)
    fig.savefig(os.path.join(FIG, "teaser_draft.pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(FIG, "teaser_draft.png"), bbox_inches="tight", pad_inches=0.02, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    for stale in ("fig_threshold.pdf", "fig_threshold_preview.png"):
        if os.path.exists(os.path.join(FIG, stale)):
            os.remove(os.path.join(FIG, stale))
    fig_medforge()
    fig_operating()
    fig_oracle()
    fig_teaser_draft()
    for f in sorted(os.listdir(FIG)):
        print(f, os.path.getsize(os.path.join(FIG, f)))
