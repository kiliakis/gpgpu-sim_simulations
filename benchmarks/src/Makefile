CUDA_VERSION=$(shell nvcc --version | grep release | sed -re 's/.*release ([0-9]+\.[0-9]+).*/\1/')
CUDA_VERSION_MAJOR=$(shell nvcc --version | grep release | sed -re 's/.*release ([0-9]+)\..*/\1/')
BINDIR=$(shell pwd)/../bin/$(CUDA_VERSION)
BINSUBDIR?=release
SETENV=export BINDIR=$(BINDIR); \
   	export BINSUBDIR=$(BINSUBDIR); \
   	export ROOTOBJDIR=obj_$(CUDA_VERSION);\

PARBOIL_SETENV := CUDA_PATH=$(CUDA_INSTALL_PATH)
PARBOIL_MAKE_ARGS := -f $(shell pwd)/cuda/parboil/common/mk/Makefile \
	BUILDDIR=build/cuda_default \
	PARBOIL_ROOT=$(shell pwd)/cuda/parboil \
	PLATFORM=default \
	BUILD=cuda \
	SRCDIR=src/cuda

ifeq ($(shell test $(CUDA_VERSION_MAJOR) -gt 4; echo $$?),0)
	MAKE_ARGS := GENCODE_SM10= 
endif

check_environment:
	 # bash ../data_dirs/get_data.sh
	 @if [ ! -n "$(CUDA_INSTALL_PATH)" ]; then \
		echo "ERROR *** CUDA_INSTALL_PATH not set; please see README.ISPASS-2009"; \
		exit 201; \
	 elif [ ! -d "$(CUDA_INSTALL_PATH)" ]; then \
	 	echo "ERROR *** CUDA_INSTALL_PATH=$(CUDA_INSTALL_PATH) invalid (directory does not exist)."; \
		exit 202; \
	 else \
		NVCC_PATH=`which nvcc`; \
		if [ $$? = 1 ]; then \
			echo ""; \
			echo "ERROR ** nvcc (from CUDA Toolkit) was not found in PATH but required to build the ISPASS 2009 benchmarks."; \
			echo "         Try adding $(CUDA_INSTALL_PATH)/bin/ to your PATH environment variable."; \
			echo "         Please also be sure to read README.ISPASS-2009 if you have not done so."; \
			echo ""; \
			exit 206; \
		else\
			CUDA_VERSION=`nvcc --version | grep release | sed -re 's/.*release ([0-9]+\.[0-9]+).*/\1/'`; \
			if [ "$(CUDA_VERSION)"=="2.3" -o "$(CUDA_VERSION)"=="3.1" -o "$(CUDA_VERSION)"=="4.0" -o "$(CUDA_VERSION)"=="4.2" ]; then \
				true;\
			else \
				echo "Only CUDA 2.3, 3.1, 4.0 and 4.2 are supported. Your cuda Version is $(CUDA_VERSION)"; \
				exit 207;\
			fi\
		fi \
	fi

###################################################################################################3
# Rodinia 2.0 Functional Test Stuff
###################################################################################################3
rodinia_2.0-ft: check_environment
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/backprop
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/bfs
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/heartwall
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/hotspot
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/kmeans
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/lud
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/nn
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/nw
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/pathfinder
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/srad
	$(SETENV) make $(MAKE_ARGS) -C cuda/rodinia/2.0-ft/streamcluster

clean_rodinia_2.0-ft:
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/backprop
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/bfs
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/heartwall
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/hotspot
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/kmeans
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/lud
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/nn
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/nw
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/pathfinder
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/srad
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/rodinia/2.0-ft/streamcluster

###################################################################################################3
# GPU Computing SDK Version 4.1.15
###################################################################################################3
sdk: check_environment
	$(SETENV) make $(MAKE_ARGS) all -C cuda/sdk/

clean_sdk:
	$(SETENV) make $(MAKE_ARGS) clean -C cuda/sdk/

###################################################################################################3
# Parboil Benchmark Suite Version 0.2
###################################################################################################3
parboil: check_environment
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/spmv-parboil-0.2 -C cuda/parboil/benchmarks/spmv/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/stencil-parboil-0.2 -C cuda/parboil/benchmarks/stencil/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/tpacf-parboil-0.2 -C cuda/parboil/benchmarks/tpacf/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/lbm-parboil-0.2 -C cuda/parboil/benchmarks/lbm/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/mri-gridding-parboil-0.2 -C cuda/parboil/benchmarks/mri-gridding/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/sad-parboil-0.2 -C cuda/parboil/benchmarks/sad/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/bfs-parboil-0.2 -C cuda/parboil/benchmarks/bfs/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/histo-parboil-0.2 -C cuda/parboil/benchmarks/histo/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/sgemm-parboil-0.2 -C cuda/parboil/benchmarks/sgemm/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/mri-q-parboil-0.2 -C cuda/parboil/benchmarks/mri-q/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) default BIN=$(BINDIR)/$(BINSUBDIR)/cutcp-parboil-0.2 -C cuda/parboil/benchmarks/cutcp/

clean_parboil:
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/spmv-parboil-0.2 -C cuda/parboil/benchmarks/spmv/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/stencil-parboil-0.2 -C cuda/parboil/benchmarks/stencil/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/tpacf-parboil-0.2 -C cuda/parboil/benchmarks/tpacf/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/lbm-parboil-0.2 -C cuda/parboil/benchmarks/lbm/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/mri-gridding-parboil-0.2 -C cuda/parboil/benchmarks/mri-gridding/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/sad-parboil-0.2 -C cuda/parboil/benchmarks/sad/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/bfs-parboil-0.2 -C cuda/parboil/benchmarks/bfs/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/histo-parboil-0.2 -C cuda/parboil/benchmarks/histo/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/sgemm-parboil-0.2 -C cuda/parboil/benchmarks/sgemm/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/mri-q-parboil-0.2 -C cuda/parboil/benchmarks/mri-q/
	$(PARBOIL_SETENV) make $(PARBOIL_MAKE_ARGS) clean BIN=$(BINDIR)/$(BINSUBDIR)/cutcp-parboil-0.2 -C cuda/parboil/benchmarks/cutcp/



all: check_environment rodinia_2.0-ft sdk parboil

cleanall: clean_rodinia_2.0-ft clean_sdk clean_parboil
	../data_dirs/clean_data.sh
