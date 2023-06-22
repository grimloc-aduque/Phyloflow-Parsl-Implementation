from typing import List, Dict, Tuple
import json
import pandas as pd
import argparse, sys
import pysam
from collections import defaultdict
import urllib.parse
import gzip
import numpy as np


def parse_vcf_samples(vcf_file: str) -> Tuple[List[Dict], Dict]:
    """Parse VEP output format to get sample info.

    Args:
        vcf_file (str): path to VCF file

    Returns:
        List[Dict]: list of sample info
        Dict: sample to id mapping
    """
    vcf = pysam.VariantFile(vcf_file)
    temp = []
    sample2id = {}
    idx = 1
    for rec in vcf.header.records:
        if rec.key == "normal_sample":
            temp.append({"sample_id": idx, "name": rec.value, "type": "normal"})
            sample2id[rec.value] = idx
            idx += 1
        elif rec.key == "tumor_sample":
            temp.append({"sample_id": idx, "name": rec.value, "type": "tumor"})
            sample2id[rec.value] = idx
            idx += 1
    return temp, sample2id


def parse_vep_variants(vep_file: str, program: str="moss") -> Tuple[List[Dict], Dict]:
    """Parse VEP output format.

    VEP details are written in INFO field CSQ.

    Args:
        vep_file (str): path to VEP output file

    Returns:
        List[Dict]: list of variant info
    """
    vep = pysam.VariantFile(vep_file)
    samples = vep.header.samples
    fields = vep.header.info["CSQ"].description.split(": ")[1].split("|")
    index = {field.lower(): i for i, field in enumerate(fields)}
    variants = []
    variants2id = {}
    idx = 0
    for rec in vep:
        annotation = rec.info["CSQ"][0].split("|")
        if program == "moss":
            vaf = [rec.samples[sample]["TCOUNT"] / rec.samples[sample]["DP"] if rec.samples[sample]["TCOUNT"] > 0 else 0
                for sample in samples ]
            vaf_counts = [[rec.samples[sample]["TCOUNT"], rec.samples[sample]["DP"]] for sample in samples ]
        elif program == "mutect":
            vaf = [rec.samples[sample]["AD"][1] / (rec.samples[sample]["AD"][0] + rec.samples[sample]["AD"][1]) if rec.samples[sample]["AD"][1] > 0 else 0
                for sample in samples ]
            vaf_counts = [[rec.samples[sample]["AD"][1], (rec.samples[sample]["AD"][0] + rec.samples[sample]["AD"][1])] for sample in samples ]
        aa_change = urllib.parse.unquote(annotation[index['hgvsp']].split(':')[-1])
        # if "/" in annotation[index["amino_acids"]]:
        #     # TODO: Let VEP output HGSV notation
        #     # aa_ref, aa_var = annotation[index["amino_acids"]].split("/")
        #     # aa_change += f"p.{aa_ref}{annotation[index['protein_position']]}{aa_var}"
        #     # print(aa_change)
        if "PASS" in rec.filter:
            variants.append({
                "SNV_id":               idx,
                "chr":                  rec.contig,
                "start":                rec.start+1,
                "reference":            rec.ref,
                "variant":              rec.alts[0],
                "strand":               annotation[index["strand"]],
                "consequence":          annotation[index["consequence"]],
                "symbol":               annotation[index["symbol"]],
                "gene":                 annotation[index["gene"]],
                "vaf":                  vaf,
                "vaf_counts":           vaf_counts,
                "amino_acid_change":    aa_change,
                # "tier": 'tier1',
                # "type": 'SNP',
                # "ucsc_cons": '1',
                # "cgc_gene": '1',
                # "drug": '',
                # "drug_pathway": ''
            })
            variants2id[f"{rec.contig}:{rec.start+1}"] = idx
            idx += 1
    return variants, variants2id

def skip_lines(file, n_skip):
    for i in range(n_skip):
        # print(next(file), end='')
        next(file)

def parse_spruce_result(spruce_file: str, sample2id: dict) -> List[Dict]:
    with (
        gzip.open(spruce_file, "rt") if (
            spruce_file.endswith("gzip") or
            spruce_file.endswith("gz")
        ) else open(spruce_file, "rt")
     ) as spruce:
        n_sol = int(next(spruce).strip().split()[0])
        sols = []
        for i in range(n_sol):
            while True:
                line = next(spruce)
                if len(line.strip()) > 0:
                    break
            k = int(line.split()[0])
            m = int(next(spruce).split()[0])
            n = int(next(spruce).split()[0])
            skip_lines(spruce, k*m + 1) # observed F
            sample_ids = [sample2id[sample] for sample in next(spruce).strip().split()]
            skip_lines(spruce, 2)
            skip_lines(spruce, n * 2 + 1) # tree (A)
            skip_lines(spruce, 2 + n + 1)
            skip_lines(spruce, 2)
            usage = []
            for _ in range(m):
                usage.append([float(x) for x in next(spruce).strip().split()])
            sols.append({
                "prevalence": np.array(usage),
            })
            skip_lines(spruce, 3 + k*m + 4) # inferred F
        return sols, sample_ids

def parse_spruce(spruce_json: str, spruce_res: str, sample2id: dict) -> List[defaultdict]:
    res, sample_ids = parse_spruce_result(spruce_res, sample2id)
    with open(spruce_json, "r") as ifile:
        spruce = json.load(ifile)
        spruce_convert = {int(node["id"]): node["label"].strip("()").split(",")[0] for node in spruce["nodes"]}
        trees = []
        for key, sol in spruce.items():
            if key.startswith("sol"):
                idx_sol = int(key.split('_')[1])
                tree = {
                    "tree_id": int(idx_sol),
                    "tree_name": f"tree_{idx_sol}",
                    "tree_score": None,
                    "nodes": [
                        {
                            "node_name": spruce_convert[i],
                            "prevalence": [
                                {
                                    "sample_id": int(sample_id),
                                    "value": float(prevalence),
                                }
                                for sample_id, prevalence in zip(sample_ids, res[idx_sol]["prevalence"][:, i])
                            ],
                            "children": []
                        }
                        for i in spruce_convert
                    ]
                }
                for edge in sol:
                    for node in tree["nodes"]:
                        if node["node_name"] != "*":
                            node["cluster_id"] = int(node["node_name"])
                        if node["node_name"] == spruce_convert[edge["source"]]:
                            node["children"].append(spruce_convert[edge["target"]])
                trees.append(tree)
        return trees


def parse_cluster_assign(cluster_file: str, sample_to_id: dict, variants_to_id) -> List[Dict]:
    """Parse cluster assignment file.

    Args:
        cluster_file (str): path to cluster assignment file

    Returns:
        List[Dict]: list of cluster info
    """
    clusters = []
    df_cluster = pd.read_csv(cluster_file, sep='\t')
    df_cluster["mutation_id"] = df_cluster["mutation_id"].str.strip("b\'\"")
    df_cluster["sample_id"] = df_cluster["sample_id"].str.strip("b\'\"")
    grouped = df_cluster.groupby(["sample_id", "cluster_id"])


    for (sample_name, cluster_id), group in grouped:
        clusters.append({
            "cluster_id": int(cluster_id),
            "sample_name": str(sample_name),
            "sample_id": sample_to_id[sample_name],
            "variants": [variants_to_id[v] for v in group["mutation_id"]]
        })
    return clusters



def main(args):
    data = {
        "version": "phylodiver v0.1.0",
        "samples": [],
        "SNV": [],
        "clusters": [],
        "trees": [],
    }
    samples, sample2id = parse_vcf_samples(args.vep)
    data["samples"] += samples
    variants, variants2id = parse_vep_variants(args.vep, args.program)
    data["SNV"] += variants
    data["clusters"] += parse_cluster_assign(args.cluster, sample2id, variants2id)
    trees = parse_spruce(args.spruce_json, args.spruce_res, sample2id)
    data["trees"] += trees
    with open(args.json, "w") as ofile:
        json.dump(data, ofile, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Aggregate JSON",
        description="Aggregate results, generate a JSON file for visualization")

    parser.add_argument("-j", "--json", help="aggregate JSON file [output]")
    parser.add_argument("-v", "--vep", help="VEP output file [workflow]")
    parser.add_argument("-c", "--cluster", help="Clustering output file [workflow]")
    parser.add_argument("-s", "--spruce-json", help="SPRUCE visualization JSON file [workflow]")
    parser.add_argument("-S", "--spruce-res", help="SPRUCE result file [workflow]")
    parser.add_argument("-p", "--program", help="program for variant calling", required=True, choices=["moss", "mutect"])
    args = parser.parse_args(None if sys.argv[1:] else ['-h'])

    main(args)
