
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
		docker: 'public.ecr.aws/k1t6h9x8/phyloflow/spruce'
	}
}
