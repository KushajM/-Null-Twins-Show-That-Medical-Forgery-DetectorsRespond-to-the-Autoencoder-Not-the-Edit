"""Static checks for the draft, used because no TeX distribution is installed.

  * every \\cite key exists in refs.bib (and lists uncited entries);
  * every \\ref / \\cref / \\Cref target has a \\label;
  * braces balance in each file (comments stripped);
  * anonymity and private-jargon terms do not appear in the paper text;
  * every line of body text that contains a decimal number or percentage
    carries a "% src:" comment on that line;
  * a rough word count, to estimate length.

Run:  .venv-mdf\\Scripts\\python.exe paper\\scripts\\check_tex.py
"""

import codecs
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.abspath(os.path.join(HERE, ".."))
FILES = [os.path.join(PAPER, "main.tex"), os.path.join(PAPER, "macros.tex"),
         os.path.join(PAPER, "fig", "teaser.tex")] + sorted(glob.glob(os.path.join(PAPER, "sec", "[0-9]*.tex")))

# Identifying tokens are stored rot13-encoded so that this file does not itself contain them.
_IDENT = [codecs.decode(s, "rot13") for s in ("Xnauniyln", "Fnc_Xhfu", "Cyrkr", "@Xhfu")]
BANNED = [re.escape(s) for s in _IDENT] + [
    r"medforensics-v", r"MedForensics v2", r"\bnai_v\d",
    r"\bV1\b", r"\bV0\b", r"world_model", r"\btier\b", r"PAIR-NET", r"\bIRP\b",
    r"\bE0[a-z]\b", r"Gate[ -]?\d", r"SageMaker", r"council",
    r"huggingface\.co", r"github\.com/"]

def strip_comment(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2]); i += 2; continue
        if c == "%":
            return "".join(out), line[i:]
        out.append(c); i += 1
    return "".join(out), ""


def main():
    text = {f: open(f, encoding="utf-8").read() for f in FILES}
    bib = open(os.path.join(PAPER, "refs.bib"), encoding="utf-8").read()
    bibkeys = set(re.findall(r"@\w+\{([^,\s]+),", bib))
    cites, labels, refs = set(), set(), set()
    problems = []
    words = 0
    for f, s in text.items():
        rel = os.path.relpath(f, PAPER)
        depth = 0
        for n, raw in enumerate(s.splitlines(), 1):
            body, com = strip_comment(raw)
            for m in re.finditer(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]*)\}", body):
                cites.update(k.strip() for k in m.group(1).split(","))
            labels.update(re.findall(r"\\label\{([^}]*)\}", body))
            for m in re.finditer(r"\\[cC]?ref\{([^}]*)\}", body):
                refs.update(k.strip() for k in m.group(1).split(","))
            depth += body.count("{") - body.count("\\{") - (body.count("}") - body.count("\\}"))
            for pat in BANNED:
                if re.search(pat, body):
                    problems.append("%s:%d banned term /%s/: %s" % (rel, n, pat, body.strip()[:90]))
            # numbers needing a source: decimals like 0.963, percentages, or counts with a comma
            if rel.startswith("sec") or rel.startswith("fig"):
                has_num = re.search(r"(?<![\w.])\d*\.\d+|\d+(?:\.\d+)?\\%|\d{1,3},\d{3}", body)
                if has_num and "src:" not in com:
                    stripped = re.sub(r"\\(cref|ref|label|cite)\{[^}]*\}", "", body)
                    if re.search(r"(?<![\w.])\d*\.\d+|\d+(?:\.\d+)?\\%|\d{1,3},\d{3}", stripped):
                        problems.append("%s:%d number without src: %s" % (rel, n, body.strip()[:100]))
                words += len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\\[A-Za-z]+", " ", body)))
        if depth != 0:
            problems.append("%s: unbalanced braces (net %+d)" % (rel, depth))
    for k in sorted(cites - bibkeys):
        problems.append("missing bib key: " + k)
    for k in sorted(refs - labels):
        problems.append("undefined label: " + k)
    print("cited keys: %d; bib entries: %d; uncited bib entries: %s"
          % (len(cites), len(bibkeys), sorted(bibkeys - cites)))
    print("labels: %d; refs: %d" % (len(labels), len(refs)))
    print("approx. words in sections + teaser: %d" % words)
    print("\n".join(problems) if problems else "no problems found")


if __name__ == "__main__":
    main()
