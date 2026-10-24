#!/usr/bin/env bash
cd /bigdata/stajichlab/shared/projects/BFD/Fungi_BFD_runs/pasa_train_performance_evaluate/experiment_B
mkdir -p logs
: > rescore_jobs.tsv
for d in */pasa_opt.B */busco_opt.B */pasa_ctl.B */busco_ctl.B */pasa_opt_r2.B */busco_opt_r2.B; do
  [ -d "$d" ] || continue
  g=${d%%/*}; a=$(basename $d .B)
  id=$(sbatch --parsable -J "R_${g}_${a}" expD_rescore_one.sh "$PWD/$d")
  printf "%s\t%s\t%s\n" "$g" "$a" "$id" >> rescore_jobs.tsv
done
wc -l rescore_jobs.tsv; head -2 rescore_jobs.tsv; tail -1 rescore_jobs.tsv
