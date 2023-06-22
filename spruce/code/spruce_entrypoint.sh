## This is the script that runs *inside* the container and receives the arguments
## from the 'docker run' command to pass to the spruceexecutable

## This script must be called with the list of files that are samples
## as defined by spruce 'in-files'.


echo "spruce_entrypoint.sh begin."
echo "list of input files is: $@"

# TODO: spruce pipeline
build_dir="/spruce"

DATA=$1
# INTERVAL=$2
CLIQUE="spruce.cliques"

echo "SPRUCE: Enumerating cliques"
$build_dir/cliques -s -1 $DATA > $CLIQUE

echo "SPRUCE: Running enumerate"
$build_dir/enumerate -clique $CLIQUE -t 2 -v 3 $DATA > spruce.res
gzip -c spruce.res > spruce.res.gz
echo "SPRUCE: Running rank"
zcat spruce.res.gz | $build_dir/rank - > spruce.merged.res
echo "SPRUCE: Visualize"
zcat spruce.res.gz | $build_dir/visualize -i 0 -a - > spruce.res.txt
zcat spruce.res.gz | $build_dir/visualize -i 0 -j - > spruce.res.json

echo "spruce_entrypoint.sh finished."
