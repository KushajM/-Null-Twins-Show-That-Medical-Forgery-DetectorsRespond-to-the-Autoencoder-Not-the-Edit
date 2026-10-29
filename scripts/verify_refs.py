"""Look up every bibliography entry on DBLP (and arXiv for preprints) and log
the top hit, so refs.bib can be checked against an external record.

Output: paper/scripts/verify_refs_log.txt
"""

import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (refs-check)"}

# key -> (dblp query, arXiv id or None)
Q = {
    "guillaro2025bfree": ("Bias-Free Training Paradigm More General AI-generated Image Detection", "2412.17671"),
    "rajan2025aligned": ("Aligned Datasets Improve Detection of Latent Diffusion-Generated Images", "2410.11835"),
    "nebioglu2026inpx": (None, "2602.00192"),
    "ricker2024aeroblade": ("AEROBLADE Training-Free Detection Latent Diffusion Images Autoencoder Reconstruction Error", "2401.17879"),
    "tan2024npr": ("Rethinking the Up-Sampling Operations in CNN-based Generative Network for Generalizable Deepfake Detection", "2312.10461"),
    "ojha2023unifd": ("Towards Universal Fake Image Detectors that Generalize Across Generative Models", "2302.10174"),
    "wang2023dire": ("DIRE for Diffusion-Generated Image Detection", "2303.09295"),
    "luo2024lare2": ("LaRE^2 Latent Reconstruction Error Based Method for Diffusion-Generated Image Detection", None),
    "wang2026end4": ("End4 End-to-end Denoising Diffusion Diffusion-Based Inpainting Detection", "2509.13214"),
    "ji2026hide": ("HIDE Detecting Diffusion-Based Inpainting Latent h-Space Representation", None),
    "zhu2025mesorch": ("Mesoscopic Insights Orchestrating Multi-scale Hybrid Architecture Image Manipulation Localization", "2412.13753"),
    "ma2024imdlbenco": ("IMDL-BenCo Comprehensive Benchmark Codebase Image Manipulation Detection Localization", "2406.10580"),
    "guillaro2023trufor": ("TruFor Leveraging all-round clues for trustworthy image forgery detection and localization", "2212.10957"),
    "chen2021mvss": ("Image Manipulation Detection by Multi-View Multi-Scale Supervision", "2104.06832"),
    "ma2023imlvit": ("IML-ViT Benchmarking Image Manipulation Localization by Vision Transformer", "2307.14863"),
    "liu2022pscc": ("PSCC-Net Progressive Spatio-Channel Correlation Network for Image Manipulation Detection and Localization", "2103.10596"),
    "chen2026medforge": ("MedForge Interpretable Medical Deepfake Detection Forgery-aware Reasoning", "2603.18577"),
    "li2025medforensics": ("Toward Medical Deepfake Detection Comprehensive Dataset Novel Method", "2509.15711"),
    "mirsky2019ctgan": ("CT-GAN Malicious Tampering of 3D Medical Imagery using Deep Learning", "1901.03597"),
    "zingarini2024m3dsynth": ("M3Dsynth dataset of medical 3D images with AI-generated local manipulations", "2309.07973"),
    "grabovski2024btd": ("Back-in-Time Diffusion Unsupervised Detection of Medical Deepfakes", "2407.15169"),
    "ctforensics2026": (None, "2603.01878"),
    "medbanana2025": (None, "2511.00801"),
    "zavrtanik2021draem": ("DRAEM A discriminatively trained reconstruction embedding for surface anomaly detection", "2108.07610"),
    "zavrtanik2021riad": ("Reconstruction by inpainting for visual anomaly detection", None),
    "behrendt2024pddpm": ("Patched Diffusion Models for Unsupervised Anomaly Detection in Brain MRI", "2303.03758"),
    "liu2023lmd": ("Unsupervised Out-of-Distribution Detection with Diffusion Inpainting", "2302.10326"),
    "akyon2022sahi": ("Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection", "2202.06934"),
    "daudt2018fcsiam": ("Fully Convolutional Siamese Networks for Change Detection", "1810.08462"),
    "chen2022bit": ("Remote Sensing Image Change Detection With Transformers", "2103.00208"),
    "bandara2022changeformer": ("A Transformer-Based Siamese Network for Change Detection", "2201.01293"),
    "venkatesan2000hash": ("Robust image hashing Venkatesan", None),
    "swaminathan2006hash": ("Robust and secure image hashing Swaminathan", None),
    "rombach2022ldm": ("High-Resolution Image Synthesis with Latent Diffusion Models", "2112.10752"),
    "podell2024sdxl": ("SDXL Improving Latent Diffusion Models for High-Resolution Image Synthesis", "2307.01952"),
    "suvorov2022lama": ("Resolution-robust Large Mask Inpainting with Fourier Convolutions", "2109.07161"),
    "armato2011lidc": ("Lung Image Database Consortium LIDC Image Database Resource Initiative IDRI completed reference database", None),
    "jha2020kvasirseg": ("Kvasir-SEG A Segmented Polyp Dataset", "1911.07069"),
    "borgli2020hyperkvasir": ("HyperKvasir comprehensive multi-class image and video dataset for gastrointestinal endoscopy", None),
    "aldhabyani2020busi": ("Dataset of breast ultrasound images", None),
    "cheng2015brain": ("Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition", None),
    "borkowski2019lc25000": (None, "1912.12142"),
    "rahman2020tb": ("Reliable Tuberculosis Detection Using Chest X-Ray With Deep Learning, Segmentation and Visualization", None),
    "gebru2021datasheets": ("Datasheets for datasets", "1803.09010"),
    "zhang2025trainingfree": ("Training-Free Image Manipulation Localization Using Diffusion Models", None),
    "nuzhdin2026fused": (None, "2608.28302"),
}


def get(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.URLError:
        # Python's static CA bundle cannot complete some chains on this host;
        # Windows curl (schannel) can.
        import subprocess
        return subprocess.run(["curl.exe", "-s", "-A", UA["User-Agent"], url],
                              capture_output=True, check=True, timeout=60).stdout


def dblp(q):
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode(dict(q=q, format="json", h=3))
    j = json.loads(get(url))
    hits = j.get("result", {}).get("hits", {}).get("hit", [])
    out = []
    for h in hits:
        i = h["info"]
        a = i.get("authors", {}).get("author", [])
        a = a if isinstance(a, list) else [a]
        out.append("%s | %s %s | %s" % (i.get("title"), i.get("venue"), i.get("year"),
                                         ", ".join(x.get("text", "") for x in a[:6])))
    return out


def arxiv(aid):
    x = get("http://export.arxiv.org/api/query?id_list=" + aid)
    ns = {"a": "http://www.w3.org/2005/Atom", "ax": "http://arxiv.org/schemas/atom"}
    e = ET.fromstring(x).find("a:entry", ns)
    if e is None:
        return "not found"
    t = " ".join(e.find("a:title", ns).text.split())
    au = ", ".join(n.find("a:name", ns).text for n in e.findall("a:author", ns)[:8])
    pub = e.find("a:published", ns).text[:10]
    jr = e.find("ax:journal_ref", ns)
    cm = e.find("ax:comment", ns)
    return "%s | %s | %s | journal_ref=%s | comment=%s" % (
        t, au, pub, jr.text if jr is not None else "-",
        " ".join(cm.text.split())[:160] if cm is not None else "-")


lines = []
for k, (q, aid) in Q.items():
    lines.append("== " + k)
    if q:
        try:
            for h in dblp(q):
                lines.append("  dblp : " + h)
        except Exception as ex:  # noqa: BLE001
            lines.append("  dblp : ERROR %r" % ex)
        time.sleep(1.0)
    if aid:
        try:
            lines.append("  arXiv: " + arxiv(aid))
        except Exception as ex:  # noqa: BLE001
            lines.append("  arXiv: ERROR %r" % ex)
        time.sleep(3.1)
    print("\n".join(lines[-4:]), flush=True)

open(os.path.join(HERE, "verify_refs_log.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
