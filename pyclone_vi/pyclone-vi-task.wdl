
task pyclone_vi_clustering{
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

