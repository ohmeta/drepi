#!/usr/bin/env snakemake

import drepi

shell.executable("bash")

SAMPLES = parse_samples(config)


include: "../rules/checkm.smk"
include: "../rules/drep.smk"
include: "../rules/galah.smk"


rule all:
    input:
        rules.checkm_all.input,
        rules.dereplicate_drep_all.input,
        rules.dereplicate_galah_all.input
