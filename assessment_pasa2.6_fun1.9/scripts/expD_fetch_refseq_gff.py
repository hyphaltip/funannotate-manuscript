#!/usr/bin/env python3
"""Download the RefSeq GFF3 (GCF_*) for the experiment D genomes from NCBI.

Usage: expD_fetch_refseq_gff.py <experiment_B dir> [outdir]

Reads expD_genomes.tsv and genomes.tsv in the experiment_B directory. The accession of each genome is taken from its
`refseq_gff` column (the file name stem, e.g. GCF_000349305.1). The GFF3 is fetched from
https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/NNN/NNN/NNN/<accession>_<assembly name>/ and stored as
<outdir>/<accession>.gff.gz (default <experiment_B>/refseq_gff_redownload), the name the scorer's `refseq_gff` column used.
Writes <outdir>/refseq_gff_redownload.tsv with the source URL, size, md5, and the annotation release stated in the file header.
Existing non-empty files are kept.
"""
import csv
import gzip
import hashlib
import os
import re
import sys
import time
import urllib.request

BASE = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF"


def fetch(url, tries=4):
    for n in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return r.read()
        except Exception as err:  # noqa: BLE001
            if n == tries - 1:
                raise
            time.sleep(5 * (n + 1))


def accession_dir(acc):
    digits = acc.split("_")[1].split(".")[0]
    return "%s/%s/%s/%s/" % (BASE, digits[0:3], digits[3:6], digits[6:9])


def main(argv):
    exp = argv[1]
    out = argv[2] if len(argv) > 2 else os.path.join(exp, "refseq_gff_redownload")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(exp, "expD_genomes.tsv")) as f:
        wanted = [row["genome"] for row in csv.DictReader(f, delimiter="\t")]
    with open(os.path.join(exp, "genomes.tsv")) as f:
        info = {row["name"]: row for row in csv.DictReader(f, delimiter="\t")}
    rows = []
    for g in wanted:
        acc = os.path.basename(info[g]["refseq_gff"]).replace(".gff.gz", "")
        dest = os.path.join(out, acc + ".gff.gz")
        listing = fetch(accession_dir(acc)).decode()
        dirs = sorted(set(re.findall(r'href="(%s_[^"/]+)/"' % re.escape(acc), listing)))
        if len(dirs) != 1:
            raise SystemExit("%s: expected one directory for %s, found %s" % (g, acc, dirs))
        url = "%s%s/%s_genomic.gff.gz" % (accession_dir(acc), dirs[0], dirs[0])
        if not (os.path.isfile(dest) and os.path.getsize(dest) > 0):
            data = fetch(url)
            with open(dest + ".part", "wb") as h:
                h.write(data)
            os.replace(dest + ".part", dest)
        with open(dest, "rb") as h:
            raw = h.read()
        release = ""
        with gzip.open(dest, "rt") as h:
            for line in h:
                if not line.startswith("#"):
                    break
                if line.startswith("#!annotation-source") or line.startswith("#!genome-build"):
                    release += line.strip() + "; "
        rows.append((g, acc, url, len(raw), hashlib.md5(raw).hexdigest(), release.strip()))
        print(g, acc, len(raw), flush=True)
    with open(os.path.join(out, "refseq_gff_redownload.tsv"), "w") as h:
        h.write("genome\taccession\turl\tbytes\tmd5\theader\n")
        for r in rows:
            h.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__":
    main(sys.argv)
