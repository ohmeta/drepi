# Dereplicate genomes or genes

## Instalation

```sh
mamba install -c bioconda drepi [WIP]
# or
mamba install -c ohmeta drepi
```

## Run
### help

```sh
usage: drepi [-h] [-v]  ...
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

optional arguments:
-h, --help     show this help message and exit
-v, --version  print software version and exit

available subcommands:

init         init project
drep_genomes dereplicate genomes
drep_genes   dereplicate genes
```

### init

```sh
drepi init -d . -s genes.tsv
# or
drepi init -d . -s genomes.tsv
```

### run

#### dereplicate genes
```
drepi drep_genes all
```

#### deprelicate genomes

```
drepi drep_genomes all
```

