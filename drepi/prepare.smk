if config["params"]["checkm"]["do"]:
    checkpoint checkm_prepare:
        input:
            config["params"]["genomes.tsv"]
        output:
            directory(os.path.join(config["output"]["checkm"], "genome_links"))
        params:
            suffix = "faa",
            batch_num = config["params"]["checkm"]["batch_num"]
        run:
            import os
            import glob
            import pprint

            if os.path.exists(output[0]):
                os.rmdir(output[0])

            bin_list = []
            for i in input:
                bin_list += [os.path.realpath(j) \
                             for j in glob.glob(os.path.join(os.path.dirname(i), "*.faa"))]

            if len(bin_list) > 0:
                for batch_id in range(0, len(bin_list), params.batch_num):
                    batch_dir = os.path.join(output[0], "bins_%d" % batch_id)
                    os.makedirs(batch_dir, exist_ok=True)

                    for bin_file in bin_list[batch_id:batch_id + params.batch_num]:
                        os.symlink(bin_file,
                                   os.path.join(batch_dir,
                                                os.path.basename(bin_file)))
            else:
                os.makedirs(os.path.join(output[0], "bins_0"), exist_ok=True)
