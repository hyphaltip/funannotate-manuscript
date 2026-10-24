#!/usr/bin/env python3
"""Check the re-downloaded RefSeq GFF3 files against scores stored from earlier experiment B arms.

Usage: expD_verify_refseq.py <experiment_B dir> [arm ...]     (default arms: busco_r1 pasa)

For each experiment D genome and arm whose step-B `<arm>.B/score.tsv` exists, re-scores the stored predictions with the new
reference (predict_scorer.py score, gffcompare must be on PATH) and compares every numeric column with the stored row.
Prints one line per genome and arm and a summary; exit status 1 if any column differs.
"""
import csv
import glob
import os
import subprocess
import sys
import tempfile

SCORER = "/bigdata/stajichlab/shared/projects/BFD/Fungi_BFD_runs/pasa_train_performance_evaluate/refseq_benchmark/predict_scorer.py"


def read_row(path):
    with open(path) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return rows[-1] if rows else None


def main(argv):
    exp = argv[1]
    arms = argv[2:] or ["busco_r1", "pasa"]
    refdir = os.path.join(exp, "refseq_gff_redownload")
    with open(os.path.join(exp, "expD_genomes.tsv")) as f:
        genomes = [r["genome"] for r in csv.DictReader(f, delimiter="\t")]
    with open(os.path.join(exp, "genomes.tsv")) as f:
        info = {r["name"]: r for r in csv.DictReader(f, delimiter="\t")}
    bad = checked = 0
    for g in genomes:
        acc = os.path.basename(info[g]["refseq_gff"]).replace(".gff.gz", "")
        ref = os.path.join(refdir, acc + ".gff.gz")
        for arm in arms:
            w = os.path.join(exp, g, arm + ".B")
            stored = os.path.join(w, "score.tsv")
            preds = [p for p in glob.glob(os.path.join(w, "out", "predict_results", "*.gff3")) if ".tbl" not in p]
            if not (os.path.isfile(stored) and preds):
                print("%-45s %-10s skipped (no stored score or predictions)" % (g, arm))
                continue
            with tempfile.TemporaryDirectory() as tmp:
                out = os.path.join(tmp, "score.tsv")
                subprocess.run(
                    [sys.executable, SCORER, "score", "--ref-gff3", ref, "--pred-gff3", preds[0],
                     "--holdout", os.path.join(exp, g, "split.holdout_chroms.txt"), "--genome", g, "--variant", arm, "--out", out],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                new, old = read_row(out), read_row(stored)
            diffs = [k for k in old if k not in ("genome", "variant") and old[k] != new.get(k)]
            checked += 1
            if diffs:
                bad += 1
            print("%-45s %-10s %s" % (g, arm, "identical" if not diffs else "DIFFERS in " + ",".join("%s %s->%s" % (k, old[k], new[k]) for k in diffs)))
    print("checked %d genome/arm pairs, %d differ" % (checked, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
