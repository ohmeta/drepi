if config["params"]["predict"]["do"]:
    rule predict:
        input:
            fa = lambda wildcards: SAMPLES.loc[wildcards.sample, "fa"]
        output:
            pep = os.path.join(config["output"]["predict"], "{sample}/{sample}.pep.fa"),
            cds = os.path.join(config["output"]["predict"], "{sample}/{sample}.cds.fa"),
            gff = os.path.join(config["output"]["predict"], "{sample}/{sample}.gff.fa")
        params:
            mode = config["params"]["predict"]["mode"],
            format = config["params"]["predict"]["format"]
        log:
            os.path.join(config["output"]["predict"], "logs/{sample}.prodigal.log")
        run:
            from Bio import SeqIO

            total_bases = 0
            for seq in SeqIO.parse(input.fa, "fasta"):
                total_bases += len(seq)
            if total_bases < 100000:
                mode = "meta"
            else:
                mode = params.mode

            shell(
                f'''
                prodigal \
                -i {input.fa} \
                -m \
                -a {output.pep} \
                -d {output.cds} \
                -o {output.gff} \
                -f {params.format} \
                -p {mode} \
                2> {log}
                ''')

           
    rule predict_all:
        input:
            expand(
                os.path.join(config["output"]["predict"],
                             "{sample}/{sample}.{object}.fa")
                sample=SAMPLES.index.unique(),
                object=["pep", "cds", "gff"])

else:
    rule predict_all:
        input:
