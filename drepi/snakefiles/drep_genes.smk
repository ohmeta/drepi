#!/usr/bin/env snakemake

import drepi

shell.executable("bash")

SAMPLES = parse_samples(config)


include: "../rules/predict.smk"
include: "../rules/cdhit.smk"
include: "../rules/linclust.smk"


rule all:
    input:
        rules.predict_all.input,
        rules.drep_gene_cdhit_all.input,
        rules.drep_protein_linclust_all.input
