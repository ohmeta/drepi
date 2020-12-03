rule dereplicate_galah:
    input:
        genome_list = config["params"]["genomes"],
        checkm_table = config["params"]["checkm_table"]
    output:
        os.path.join(config["output"]["galah"], "done")
    params:
        min_completeness = "" if config["params"]["galah"]["min_completeness"] == "" \
            else f'''--min-completeness {config["params"]["galah"]["min_completeness"]}''',
        max_contamination = "" if config["params"]["galah"]["max_contamination"] == "" \
            else f'''--max-contamination {config["params"]["galah"]["max_contamination"]}''',
        ani = config["params"]["galah"]["ani"],
        min_aligned_fraction = config["params"]["galah"]["min_aligned_fraction"],
        fragment_length = config["params"]["galah"]["fragment_length"],
        quality_formula = config["params"]["galah"]["quality_formula"],
        precluster_ani = config["params"]["galah"]["precluster_ani"],
        precluster_method = config["params"]["galah"]["precluster_method"]
    shell:
        '''
        galah cluster \
        --genome-fasta-list {input.genome_list} \
        --checkm-tab-table {input.checkm_table} \
        --min-completeness {params.min_completeness} \
        --max-contamination {params.max_contamination} \
        --ani {params.ani} \
        --min-aligned-fraction {params.min_aligned_fraction} \
        --fragment-length {params.fragment_length} \
        --quality-formula {params.quality_formula} \
        --precluster-ani {params.precluster_ani} \
        --precluster-method {params.precluster_method} \
        --output-cluster-definition {output.cluster_definition} \
        --output-representative-list {output.representative_list} \
        --threads {threads} \
        > {log} 2>&1
        '''
