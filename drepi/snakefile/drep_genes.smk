#!/usr/bin/env snakemake

import sys
import os
import metapi
import pandas as pd

shell.executable("bash")


def parse_samples(config):
    samples_df = pd.read_csv(config["params"]["samples"], sep="\t").set_index(
        "id", drop=False
    )

    cancel = False
    if "fa" in samples_df.columns:
        for sample_id in samples_df.index.unique():
            if "." in sample_id:
                print(f"{sample_id} contain '.', please remove '.', now quiting :)")
                cancel = True
            fa_list = samples_df.loc[[sample_id], "fa"].dropna().tolist()
            if len(fa_list) > 1:
                print(f"{sample_id} have many fasta files")
                cancel = True
            else:
                if not os.path.exists(fa_list[0]):
                    print(f"{fa_list[0]} not exists")
                    cancel = True

                elif fa_list[0].endswith(".gz"):
                    print(f"{fa_list[0]} need plain text format, not support gzip format")
                    cancel = True
    else:
        print("wrong header: {header}".format(header=samples_df.columns))
        cancel = True

    if cancel:
        sys.exit(-1)
    else:
        return samples_df


SAMPLES = parse_samples(config)


include: "../rules/predict.smk"
include: "../rules/drep_cdhit.smk"
include: "../rules/drep_linclust.smk"


rule all:
    input:
        rules.predict_all.input,
        rules.drep_gene_cdhit_all.input,
        rules.drep_protein_linclust_all.input
