def cdhit_input():
    if config["params"]["predict"]["do"]:
        return expand(
            os.path.join(
                config["output"]["predict"],
                "{sample}/{sample}.cds.fa"),
            sample=SAMPLES.index.unique())
    else:
        return SAMPLES["fa"].dropna().tolist()


rule derep_gene_cdhit_prepare:
    input:
        cdhit_input
    output:
        cds = os.path.join(config["output"]["cdhit"], "input/all.cds.fa"),
        metadata = os.path.join(config["output"]["cdhit"], "input/all.metadata.tsv.gz")
    params:
        rename = config["params"]["cdhit"]["rename"]
    run:
        import gzip
        from Bio import SeqIO

        mg_count = 0

        if (len(cdhit_input) == 1) and (not params.rename):
            shell('''ln -s {input} {output.cds}''')
            shell('''touch {output.metadata}''')
        else:
            with open(output.cds, 'w') as fh, gzip.open(output.metadata, 'wb') as mh:
                if params.rename:
                    mh.write("mg_id\tcds_id\tmg_name\tcds_name\n")
                for i in input:
                    mg_count += 1
                    cds_count = 0
                    for seq_record in SeqIO.parse(i, "fasta"):
                        cds_count += 1
                        if rename:
                            mh.write(
                                f"MG_{mg_count}\tCDS_{cds_count}\t{i}\t{seq_record.name}\n")
                            seq_record.id = f"MG_{mg_count}-CDS_{cds_count}"
                            seq_record.name = ""
                            seq_record.description = ""
                        SeqIO.write(seq_record, fh, "fasta")


rule derep_gene_cdhit:
    input:
        os.path.join(config["output"]["cdhit"], "input/all.cds.fa")
    output:
        nr = os.path.join(config["output"]["cdhit"], "output/all.cds.nr.fa")
    log:
        os.path.join(config["output"]["cdhit"], "logs/cdhit.log")
    threads:
        config["params"]["dereplicate"]["cdhit"]["threads"]
    params:
        sequence_identity_threshold = config["params"]["dereplicate"]["cdhit"]["sequence_identity_threshold"],
        alignment_coverage_for_shorter_sequence = config["params"]["dereplicate"]["cdhit"]["alignment_coverage_for_shorter_sequence"],
        word_length = config["params"]["dereplicate"]["cdhit"]["word_length"],
        use_global_sequence_identity = config["params"]["dereplicate"]["cdhit"]["use_global_sequence_identity"],
        memory_limit = config["params"]["dereplicate"]["cdhit"]["memory_limit"],
        cluster_description_length = config["params"]["dereplicate"]["cdhit"]["cluster_description_length"],
        default_algorithm = config["params"]["dereplicate"]["cdhit"]["default_algorithm"],
        both_alignment = config["params"]["dereplicate"]["cdhit"]["both_alignment"]
    shell:
        '''
        cd-hit-est -i {input} -o {output} \
        -c {params.sequence_identity_threshold} \
        -n {params.word_length} \
        -G {params.use_global_sequence_identity} \
        -aS {params.alignment_coverage_for_shorter_sequence} \
        -M {params.memory_limit} \
        -d {params.cluster_description_length} \
        -g {params.default_algorithm} \
        -r {params.both_alignment} \
        -T {threads} >{log} 2>&1
        '''


rule derep_gene_cdhit_all:
    input:
        os.path.join(config["output"]["cdhit"], "output/all.cds.nr.fa")
