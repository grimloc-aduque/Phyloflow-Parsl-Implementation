
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

