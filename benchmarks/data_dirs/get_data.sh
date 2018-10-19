export DATA_ROOT="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
# rodinia-2.0-ft data
RODINIA_DIR=$DATA_ROOT/cuda/rodinia/2.0-ft
if [ ! -d $RODINIA_DIR ]; then
    wget https://engineering.purdue.edu/tgrogers/gpgpu-sim/benchmark_data/all.gpgpu-sim-app-data.tgz  
    tar xzvf all.gpgpu-sim-app-data.tgz -C $DATA_ROOT
    rm all.gpgpu-sim-app-data.tgz 
fi
