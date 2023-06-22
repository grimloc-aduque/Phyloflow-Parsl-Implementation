
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

