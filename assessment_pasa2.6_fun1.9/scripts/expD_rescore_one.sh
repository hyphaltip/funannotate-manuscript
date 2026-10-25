#!/usr/bin/bash -l
# Score one finished experiment D step-B directory against the re-downloaded RefSeq GFF3, then run BUSCO on its proteins.
# Same commands as the tail of arm_opt.sh (step B), for runs whose predict step finished but whose scoring failed because
# the RefSeq GFF3 files had been removed.
#   sbatch expD_rescore_one.sh <experiment_B>/<genome>/<arm>.B
# BUSCO_ONLY=1 skips the scoring (score.tsv already written); SKIP_BUSCO=1 skips BUSCO. It must run as a login shell (the first
# line) so that `module load busco` works, as in arm_opt.sh; without it `module load` fails with `conda: unrecognized arguments: --stack`.
#SBATCH -p stajichlab -c 8 --mem 32G -t 08:00:00
#SBATCH --exclude=c[01-30]
#SBATCH -o logs/rescore_%x_%j.out -e logs/rescore_%x_%j.err
set -euo pipefail
W=${1:?arm directory (<genome>/<arm>.B)}
E=$(cd "$(dirname "$W")/.." && pwd)
G=$(dirname "$W")
NAME=$(basename "$G")
AD=$(basename "$W"); AD=${AD%.B}
X=/bigdata/stajichlab/shared/projects/BFD/Fungi_BFD_runs/pasa_train_performance_evaluate
REFDIR=${REFDIR:-$E/refseq_gff_redownload}
ACC=$(awk -F'\t' -v g="$NAME" 'NR>1 && $1==g {n=split($10,a,"/"); sub(/\.gff\.gz$/,"",a[n]); print a[n]}' "$E/genomes.tsv")
REF=$REFDIR/$ACC.gff.gz
[ -s "$REF" ] || { echo "missing $REF"; exit 2; }
PRED=$(ls "$W"/out/predict_results/*.gff3 | grep -v '\.tbl' | head -1)
module load gffcompare
if [ -z "${BUSCO_ONLY:-}" ]; then
rm -f "$W/score.tsv"
/usr/bin/python3.12 "$X/refseq_benchmark/predict_scorer.py" score \
    --ref-gff3 "$REF" --pred-gff3 "$PRED" --holdout "$G/split.holdout_chroms.txt" \
    --genome "$NAME" --variant "$AD" --out "$W/score.tsv"
fi
[ -n "${SKIP_BUSCO:-}" ] && { echo done; exit 0; }
module load busco/5.8.0
TMPD=${SCRATCH:-/tmp}/rescore_$$
mkdir -p "$TMPD"
busco -i "$(ls "$W"/out/predict_results/*.proteins.fa)" -m proteins -l /srv/projects/db/BUSCO/v10/lineages/fungi_odb10 \
    -o busco -c 8 --offline -f --out_path "$TMPD" > "$W/busco.log" 2>&1 || true
cp "$TMPD"/busco/short_summary*.txt "$W/busco_short_summary.txt" 2>/dev/null || true
rm -rf "$TMPD"
echo done
