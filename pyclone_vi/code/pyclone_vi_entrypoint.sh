## This is the script that runs *inside* the container and receives the arguments
## from the 'docker run' command to pass to the pyclone-vi executable

## commandline args described: https://github.com/Roth-Lab/pyclone-vi

echo "hello from inside the pyclone-vi container. Does conda work?:"
#conda info
#conda list
#conda env list
#echo "running pyclone-vi help"
#conda run -n pyclone-vi pyclone-vi --help 
#echo "capturing pyclone-vi help to pyclonevi_help.txt"
#conda run -n pyclone-vi pyclone-vi --help >> pyclonevi_help.txt

echo "input args: $@"
conda run -n pyclone-vi pyclone-vi fit --in-file $1 --out-file cluster_fit.hdf5
conda run -n pyclone-vi pyclone-vi write-results-file --in-file cluster_fit.hdf5 --out-file cluster_assignment.tsv
echo "entrypoint.sh complete"
