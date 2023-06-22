import sys
import pandas as pd
import argparse
import ast
from dataclasses import dataclass, asdict


@dataclass
class Clustered(object):
    sample_index: int
    sample_label: str
    character_label: str
    character_index: int
    vaf_lb: float
    vaf_mean: float
    vaf_ub: float
    x: int = 1  # TODO: use inferred
    y: int = 1
    mu: float = 1

    def to_line(self):
        return '\t'.join(list(map(str, [self.sample_index, self.sample_label, self.character_label,
                         self.character_index, self.vaf_lb, self.vaf_mean, self.vaf_ub,
                         self.x, self.y, self.mu])))


SUPPORT_CLUSTER = ["pyclone", "pyclone_vi", "pyclone-vi"]


def main(args):
    success = False
    if args.type not in SUPPORT_CLUSTER:
        raise Exception('Can only understand input from ' +
                        ', '.join(SUPPORT_CLUSTER))
    
    if args.alpha <= 0 or args.alpha > 1:
        raise Exception('Tail probability alpha is not in (0, 1]')

    if args.type == "pyclone":
        list_clustered, n_cluster, n_sample = get_cluster_pyclone(args.cluster, args.alpha)
    elif args.type == "pyclone_vi" or args.type == "pyclone-vi":
        list_clustered, n_cluster, n_sample = get_cluster_pyclone_vi(args.cluster, args.pyclone_vi, args.alpha)

    write_spruce(list_clustered, n_cluster, n_sample, args.output)
    success = True
    return success


def get_cluster_pyclone(cluster_file, alpha):
    df_clusters = pd.read_csv(cluster_file, sep='\t')
    # mutation_id
    # sample_id
    # cluster_id
    # cellular_prevalence
    # cellular_prevalence_std
    # variant_allele_frequency
    list_clustered = []
    grouped = df_clusters.groupby(["sample_id", "cluster_id"])
    sample_to_id = {s: i for i, s in enumerate(
        df_clusters["sample_id"].unique())}
    for (sample_name, cluster_id), group in grouped:
        vaf_lb = group["variant_allele_frequency"].quantile(alpha/2)
        vaf_mean = group["variant_allele_frequency"].mean()
        vaf_ub = group["variant_allele_frequency"].quantile(1 - alpha/2)
        list_clustered.append(Clustered(sample_to_id[sample_name],
                                        sample_name,
                                        cluster_id,
                                        cluster_id,
                                        vaf_lb,
                                        vaf_mean,
                                        vaf_ub))
    n_cluster = len(df_clusters["cluster_id"].unique())
    n_sample = len(sample_to_id)
    return list_clustered, n_cluster, n_sample


def get_cluster_pyclone_vi(cluster_file, tsv_files, alpha):
    df_clusters = pd.read_csv(cluster_file, sep='\t',
                              dtype={"mutation_id": bytes, "sample_id": bytes})
    # We need ast.literal_eval(x).decode("utf-8") since the csv file output by pyclone-vi
    # contains literal "b'xxx_id'" in the csv file, we only want the string "xxx_id" inside.
    # May change this to a better way in the future.
    df_clusters["mutation_id"] = df_clusters["mutation_id"].apply(lambda x: ast.literal_eval(x).decode("utf-8"))
    df_clusters["sample_id"] = df_clusters["sample_id"].apply(lambda x: ast.literal_eval(x).decode("utf-8"))
    df_input = pd.read_csv(tsv_files, sep='\t').set_index(["sample_id", "mutation_id"])
    df_input["VAF"] = df_input["alt_counts"] / (df_input["ref_counts"] + df_input["alt_counts"])
    list_clustered = []
    grouped = df_clusters.groupby(["sample_id", "cluster_id"])
    sample_to_id = {s: i for i, s in enumerate(
        df_clusters["sample_id"].unique())}
    for (sample_name, cluster_id), group in grouped:
        vaf = df_input.loc[(group["sample_id"], group["mutation_id"]), "VAF"]
        vaf_lb = vaf.quantile(alpha/2)
        vaf_mean = vaf.mean()
        vaf_ub = vaf.quantile(1 - alpha/2)
        list_clustered.append(Clustered(sample_to_id[sample_name],
                                        sample_name,
                                        cluster_id,
                                        cluster_id,
                                        vaf_lb,
                                        vaf_mean,
                                        vaf_ub))
    n_cluster = len(df_clusters["cluster_id"].unique())
    n_sample = len(sample_to_id)
    return list_clustered, n_cluster, n_sample


def write_spruce(list_clustered, n_cluster, n_sample, tsv_file):
    with open(tsv_file, 'w') as ofile:
        print("writing data as tsv to : " + str(tsv_file))
        ofile.write(f"{n_sample} #m\n")
        ofile.write(f"{n_cluster} #n\n")
        ofile.write(
            "#sample_index	sample_label	character_index	character_label	vaf_lb	vaf_mean	vaf_ub	x	y	mu\n")
        for clu in list_clustered:
            ofile.write(clu.to_line() + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Cluster transform")
    parser.add_argument("-t", "--type", type=str,
                        help="input type", choices=SUPPORT_CLUSTER)
    parser.add_argument("-c", "--cluster", type=str,
                        help="cluster file, in tsv format")
    parser.add_argument("-v", "--pyclone-vi", type=str,
                        help="pyclone-vi input file, in tsv format")
    parser.add_argument("-a", "--alpha", type=float, help="the tail probability")
    parser.add_argument("-o", "--output", type=str,
                        help="output data file for SPRUCE")
    args = parser.parse_args(None if sys.argv[1:] else ['-h'])

    succeeded = main(args)

    if succeeded:
        exit_code = 0
    else:
        exit_code = 1

    sys.exit(exit_code)
