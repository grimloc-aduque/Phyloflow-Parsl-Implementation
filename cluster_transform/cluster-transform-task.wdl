
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
		docker: 'public.ecr.aws/k1t6h9x8/phyloflow/cluster_transform'
		}
}

