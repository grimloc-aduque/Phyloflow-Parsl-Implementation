## This is the script that runs *inside* the container and receives the arguments
## from the wdl runtime to pass to the vcf_transform python code

# This script expects two args
# $1 vcf_type: currently only 'mutect' is supported as an option
# $2 vcf_filename: path to a vcf_file produced by the pipeline type 'vcf_type'
#		Note that when using inside of wdl, wdl will change the filename and mount
#		it into the container for you (and that is the version this script will recieve)

echo "vcf_transform_entrypoint.sh: begin."
echo "vcf_transform_entrypoint.sh: list of input args from wdl runtime: $@"
conda run -n vcf-transform python -B -m py_code.main $1 $2 $3 $4 $5 $6
echo "vcf_transform_entrypoint.sh: finished."
