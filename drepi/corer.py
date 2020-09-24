#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import textwrap

import metapi

WORKFLOWS_GENOMES = [
    "predict_all",
    "checkm_all",
    "drep_drep_all",
    "drep_galah_all",
    "drep_all",
    "all",
]

WORKFLOWS_GENES = [
    "predict_all",
    "drep_cdhit_all",
    "drep_linclust_all",
    "drep_all",
    "all",
]


def run_snakemake(args, unknown, snakefile, workflow):
    conf = metapi.parse_yaml(args.config)

    if not os.path.exists(conf["params"]["samples"]):
        print("Please specific samples list on init step or change config.yaml manualy")
        sys.exit(1)

    cmd = [
        "snakemake",
        "--snakefile",
        snakefile,
        "--configfile",
        args.config,
        "--cores",
        str(args.cores),
    ] + unknown

    if args.conda_create_envs_only:
        cmd += ["--use-conda", "--conda-create-envs-only"]
    else:
        cmd += [
            "--rerun-incomplete",
            "--keep-going",
            "--printshellcmds",
            "--reason",
            "--until",
            args.task,
        ]

        if args.use_conda:
            cmd += ["--use-conda"]

        if args.list:
            cmd += ["--list"]
        elif args.run:
            cmd += [""]
        elif args.debug:
            cmd += ["--debug-dag", "--dry-run"]
        elif args.dry_run:
            cmd += ["--dry-run"]
        elif args.qsub:
            cmd += [
                "--cluster-config",
                args.cluster,
                "--jobs",
                str(args.jobs),
                "--latency-wait",
                str(args.wait),
                '--cluster "qsub -S /bin/bash -cwd \
                -q {cluster.queue} -P {cluster.project} \
                -l vf={cluster.mem},p={cluster.cores} \
                -binding linear:{cluster.cores} \
                -o {cluster.output} -e {cluster.error}"',
            ]

    cmd_str = " ".join(cmd).strip()
    print(f"Running drepi {workflow}:\n{cmd_str}")

    env = os.environ.copy()
    proc = subprocess.Popen(
        cmd_str,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
    )
    proc.communicate()


class drepi_config:
    sub_dirs = [
        "envs",
        "results",
        "logs/predict",
        "logs/checkm",
        "logs/drep_drep",
        "logs/drep_galah",
        "logs/drep_cdhit",
        "logs/drep_linclust",
    ]

    def __init__(self, work_dir):
        self.work_dir = os.path.realpath(work_dir)
        self.drepi_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_file = os.path.join(self.drepi_dir, "config", "config.yaml")
        self.cluster_file = os.path.join(self.drepi_dir, "config", "cluster.yaml")
        self.snake_file = os.path.join(self.drepi_dir, "Snakefile")
        self.envs_dir = os.path.join(self.drepi_dir, "envs")

        self.new_config_file = os.path.join(self.work_dir, "config.yaml")
        self.new_cluster_file = os.path.join(self.work_dir, "cluster.yaml")

    def __str__(self):
        message = """

  _______
  \  ___ `'.                 __.....__   _________   _...._      .--.
   ' |--.\  \            .-''         '. \        |.'      '-.   |__|
   | |    \  ' .-,.--.  /     .-''"'-.  `.\        .'```'.    '. .--.
   | |     |  '|  .-. |/     /________\   \\      |       \     \|  |
   | |     |  || |  | ||                  | |     |        |    ||  |
   | |     ' .'| |  | |\    .-------------' |      \      /    . |  |
   | |___.' /' | |  '-  \    '-.____...---. |     |\`'-.-'   .'  |  |
  /_______.'/  | |       `.             .'  |     | '-....-'`    |__|
  \_______|/   | |         `''-...... -'   .'     '.
               |_|                       '-----------'



Thanks for using drepi.

A metagenomics project has been created at %s


if you want to create fresh conda environments:

        drepi drep_genomes --conda_create_envs_only
        drepi drep_genes --conda_create_envs_only

if you have environments:

        drepi --help
        drepi init --help
        drepi drep_genomes --help
        drepi drep_genes --help
""" % (
            self.work_dir
        )

        return message

    def create_dirs(self):
        """
        create project directory
        """
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

        for sub_dir in drepi_config.sub_dirs:
            os.makedirs(os.path.join(self.work_dir, sub_dir), exist_ok=True)

        for i in os.listdir(self.envs_dir):
            shutil.copyfile(
                os.path.join(self.envs_dir, i),
                os.path.join(self.work_dir, os.path.join("envs", i)),
            )

    def get_config(self):
        """
        get default configuration
        """
        config = metapi.parse_yaml(self.config_file)
        cluster = metapi.parse_yaml(self.cluster_file)
        return (config, cluster)


def init(args, unknown):
    if args.workdir:
        project = drepi_config(args.workdir)
        print(project.__str__())
        project.create_dirs()

        conf, cluster = project.get_config()

        conf["envs"]["bioenv3.7"] = os.path.join(
            os.path.realpath(args.workdir), "envs/bioenv3.7.yaml"
        )
        conf["envs"]["bioenv3.6"] = os.path.join(
            os.path.realpath(args.workdir), "envs/bioenv3.6.yaml"
        )

        if args.samples:
            conf["params"]["samples"] = args.samples

        metapi.update_config(
            project.config_file, project.new_config_file, conf, remove=False
        )
        metapi.update_config(
            project.cluster_file, project.new_cluster_file, cluster, remove=False
        )
    else:
        print("Please supply a workdir!")
        sys.exit(-1)


def drep_genes(args, unknown):
    snakefile = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), "Snakefile/drep_genes.smk"
    )
    run_snakemake(args, unknown, snakefile, "drep_genes")


def drep_genomes(args, unknown):
    snakefile = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), "Snakefile/drep_genomes.smk"
    )
    run_snakemake(args, unknown, snakefile, "drep_genomes")


def main():
    banner = """

  _______
  \  ___ `'.                 __.....__   _________   _...._      .--.
   ' |--.\  \            .-''         '. \        |.'      '-.   |__|
   | |    \  ' .-,.--.  /     .-''"'-.  `.\        .'```'.    '. .--.
   | |     |  '|  .-. |/     /________\   \\      |       \     \|  |
   | |     |  || |  | ||                  | |     |        |    ||  |
   | |     ' .'| |  | |\    .-------------' |      \      /    . |  |
   | |___.' /' | |  '-  \    '-.____...---. |     |\`'-.-'   .'  |  |
  /_______.'/  | |       `.             .'  |     | '-....-'`    |__|
  \_______|/   | |         `''-...... -'   .'     '.
               |_|                       '-----------'


            Omics for All, Open Source for All

Dereplicate genomes or genes
"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner),
        prog="drepi",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print software version and exit",
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-d",
        "--workdir",
        metavar="WORKDIR",
        type=str,
        default="./",
        help="project workdir, default: ./",
    )

    run_parser = argparse.ArgumentParser(add_help=False)
    run_parser.add_argument(
        "--config",
        type=str,
        default="./config.yaml",
        help="config.yaml, default: ./config.yaml",
    )
    run_parser.add_argument(
        "--cluster",
        type=str,
        default="./cluster.yaml",
        help="cluster.yaml, default: ./cluster.yaml",
    )
    run_parser.add_argument(
        "--cores", type=int, default=8, help="CPU cores, default: 8"
    )
    run_parser.add_argument(
        "--jobs", type=int, default=80, help="qsub job numbers, default: 80"
    )
    run_parser.add_argument(
        "--list",
        default=False,
        action="store_true",
        help="list pipeline rules",
    )
    run_parser.add_argument(
        "--run",
        default=False,
        action="store_true",
        help="run pipeline",
    )
    run_parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="debug pipeline",
    )
    run_parser.add_argument(
        "--dry_run",
        default=False,
        action="store_true",
        help="dry run pipeline",
    )
    run_parser.add_argument(
        "--qsub",
        default=False,
        action="store_true",
        help="qsub pipeline",
    )
    run_parser.add_argument(
        "--wait", type=int, default=60, help="wait given seconds, default: 60"
    )
    run_parser.add_argument(
        "--use_conda", default=False, action="store_true", help="use conda environment"
    )
    run_parser.add_argument(
        "--conda_create_envs_only",
        default=False,
        action="store_true",
        help="conda create environments only",
    )

    subparsers = parser.add_subparsers(title="available subcommands", metavar="")
    parser_init = subparsers.add_parser(
        "init",
        parents=[common_parser],
        prog="drep init",
        help="init project",
    )
    parser_drep_genomes = subparsers.add_parser(
        "drep_genomes",
        parents=[common_parser, run_parser],
        prog="drepi drep_genomes",
        help="dereplicate genomes",
    )
    parser_drep_genes = subparsers.add_parser(
        "drep_genes",
        parents=[common_parser, run_parser],
        prog="drepi drep_genes",
        help="dereplicate genes",
    )

    parser_init.add_argument(
        "-s",
        "--samples",
        type=str,
        default=None,
        help="""desired input:
samples list, tsv format required.
        the header is: [id, fna]
""",
    )
    parser_init.set_defaults(func=init)

    parser_drep_genes.add_argument(
        "task",
        metavar="TASK",
        nargs="?",
        type=str,
        default="all",
        choices=WORKFLOWS_GENES,
        help="pipeline end point. Allowed values are " + ", ".join(WORKFLOWS_GENES),
    )
    parser_drep_genes.set_defaults(func=drep_genes)

    parser_drep_genomes.add_argument(
        "task",
        metavar="TASK",
        nargs="?",
        type=str,
        default="all",
        choices=WORKFLOWS_GENOMES,
        help="pipeline end point. Allowed values are " + ", ".join(WORKFLOWS_GENOMES),
    )
    parser_drep_genomes.set_defaults(func=drep_genomes)

    args, unknown = parser.parse_known_args()

    try:
        if args.version:
            print("drepi version %s" % drepi.__version__)
            sys.exit(0)
        args.func(args, unknown)
    except AttributeError as e:
        print(e)
        parser.print_help()


if __name__ == "__main__":
    main()
