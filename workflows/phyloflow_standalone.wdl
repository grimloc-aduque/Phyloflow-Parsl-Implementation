version 1.0

## This standalone version of the full phyloflow workflow contains all tasks
## and docker references inline (no imports).
## This makes it easier to run in some situations where isolated tasks
## that are integrated into a full workflow are difficult.
## The drawback is that the 'true' wdl tasks must be copy-pasted here,
## and this version may therefore lag in development.


#transforms VCF files into the input format of pyclone_vi (mutation clustering)
task vcf_transform{
    input {
        File vcf_file
        String vcf_type #only 'mutect' currently supported
    }

    command {
        pwd
        mkdir pyclone_samples
        out_dir=$(pwd)
        cd /code
        sh vcf_transform_entrypoint.sh ${vcf_type} ${vcf_file} \
            $out_dir/headers.json \
            $out_dir/mutations.json \
            $out_dir/pyclone_vi_formatted.tsv \
            $out_dir/pyclone_samples/
        pwd
        ls -al
        cd ..
        ls -al /
        ls /mnt
    }

    output {
        File response = stdout()
        File err_response = stderr()

        #The metadata and other headers from the vcf file, formatted to json
        File headers_json = 'headers.json'

        #The mutations information extracted from the vcf, as a json list
        #with one object per mutation (row from the vcf). Not all information
        #is retained
        File mutations_json = 'mutations.json'


        #The mutation data formatted to the input of pyclone-vi
        File pyclone_vi_formatted_tsv = 'pyclone_vi_formatted.tsv'

        Array[File] pyclone_formatted_tsvs = glob("pyclone_samples/*.tsv")

        }

    runtime {
        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/vcf_transform:latest'
        }
}

#computes mutation clusters from data originally from a vcf file
task pyclone_vi{
    input {
        File mutations_tsv
    }

    command {
        sh /code/pyclone_vi_entrypoint.sh ${mutations_tsv}
    }

    output {
        File response = stdout()
        File err_response = stderr()

        # contains a row for each mutation, with columns:
        # mutation_id, sample_id, cluster_id, cellular_prevalence,
        # cellular_prevalance_std, cluster_assignment_prob
        File cluster_assignment = 'cluster_assignment.tsv'
        }

    runtime {
        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/pyclone_vi:latest'
        }
}

#transform the clusters output by pyclone_vi to input format of spruce
task cluster_transform{
    input {
        File cluster_tsv_file
        String cluster_type
        Float alpha
        File? pyclone_vi_formatted
    }

    command {
        pwd
        mkdir pyclone_samples
        out_dir=$(pwd)
        cd /code
        sh cluster_transform_entrypoint.sh ${cluster_type} ${cluster_tsv_file} \
            ${alpha} $out_dir/spruce_formatted.tsv \
            ${if defined(pyclone_vi_formatted) then pyclone_vi_formatted else "" }
        pwd
        ls -al
        cd ..
        ls -al /
        ls /mnt
    }

    output {
        File response = stdout()
        File err_response = stderr()

        #The data file formatted to the input of SPRUCE
        File spruce_input = 'spruce_formatted.tsv'

        }

    runtime {
        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/cluster_transform:latest'
        }
}


#computes phylogeny trees from clusters
task spruce_phylogeny {
    input {
        File tsv_data_file
    }

    command {
        sh /code/spruce_entrypoint.sh ${tsv_data_file}
    }

    output {
        File response = stdout()
        File err_response = stderr()

        File cliques = "spruce.cliques"
        File result = "spruce.res.gz"
        File rank_result = "spruce.merged.res"
        File tree_text = "spruce.res.txt"
        File tree_json = "spruce.res.json"
    }

    runtime {
        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/spruce:latest'
    }
}

task aggregate_json{
    input {
        File vep_file
        File cluster_assignment
        File spruce_json
        File spruce_res
        String vcf_type
    }

    command {
        pwd
        mkdir pyclone_samples
        out_dir=$(pwd)
        cd /code
        conda run -n aggregate-json python aggregate_json.py \
            -v ${vep_file} \
            -c ${cluster_assignment} \
            -s ${spruce_json} \
            -S ${spruce_res} \
            -j $out_dir/aggregated.json \
            --program ${vcf_type}
        pwd
        ls -al
        cd ..
        ls -al /
        ls /mnt
    }

    output {
        File response = stdout()
        File err_response = stderr()

        # the aggregated json file
        File aggregated_json = 'aggregated.json'

        }

    runtime {
        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/aggregate_json:latest'
        # docker: 'phyloflow/aggregate-json:latest'
        }
}



#match phylogeny trees (nodes) with a signature database
#and then compute exposure counts that nodes have in common
##task physigs{
##    input {
##        File tree_csv
##        File snv_csv
##        File? signatures
##    }
##
##    command {
##        pwd
##        out_dir=$(pwd)
##        cd /code
##        sh physigs_entrypoint.sh ${tree_csv} ${snv_csv} $out_dir/physigs_tree \
##            ${if defined(signatures) then signatures else "" }
##        pwd
##        ls -al
##        cd ..
##        ls -al /
##        ls /mnt
##    }
##
##    output {
##        File response = stdout()
##        File err_response = stderr()
##
##        File physigs_plot = 'physigs_tree.plot.pdf'
##        File physigs_tree = 'physigs_tree.tree.tsv'
##        File physigs_exposure = 'physigs_tree.exposure.tsv'
##
##
##        }
##
##    runtime {
##        docker: 'public.ecr.aws/k1t6h9x8/phyloflow/physigs:latest'
##        }
##}



workflow phyloflow{

    input {

        File vcf_input_file
        File vep_input_file
        String vcf_type

        Float alpha_for_cluster_transform = 0.05

    }
    call vcf_transform as vcf_to_pyclonevi_in{
        input:
            vcf_file = vcf_input_file,
            vcf_type = vcf_type
    }

    call pyclone_vi as pyclonevi_clustering{
        input:
            mutations_tsv = vcf_to_pyclonevi_in.pyclone_vi_formatted_tsv
    }

    call cluster_transform as clusters_to_spruce_in{
        input:
            cluster_tsv_file = pyclonevi_clustering.cluster_assignment,
            cluster_type = "pyclone-vi",
            alpha = alpha_for_cluster_transform,
            pyclone_vi_formatted = vcf_to_pyclonevi_in.pyclone_vi_formatted_tsv
    }

    call spruce_phylogeny as spruce_tree_building{
        input:
            tsv_data_file = clusters_to_spruce_in.spruce_input
    }

    call aggregate_json as aggregate_json{
        input:
            vep_file = vep_input_file,
            cluster_assignment = pyclonevi_clustering.cluster_assignment,
            spruce_json = spruce_tree_building.tree_json,
            spruce_res = spruce_tree_building.result,
            vcf_type = vcf_type,

    }

    output {
        File input_mutations = vcf_to_pyclonevi_in.pyclone_vi_formatted_tsv
        File pyclone_vi_clusters = pyclonevi_clustering.cluster_assignment
        File spruce_cliques = spruce_tree_building.cliques
        File spruce_result = spruce_tree_building.result
        File spruce_rank_result = spruce_tree_building.rank_result
        File aggregated_json = aggregate_json.aggregated_json
    }

}
