# GPU Computing SDK Version 4.1.15
all:  
	+@$(MAKE) -C ./shared
	+@$(MAKE) -C ./C
	+@$(MAKE) -C ./CUDALibraries
	+@$(MAKE) -C ./OpenCL

clean: 
	+@$(MAKE) -C ./shared clean
	+@$(MAKE) -C ./C clean
	+@$(MAKE) -C ./CUDALibraries clean
	+@$(MAKE) -C ./OpenCL clean

clobber:
	+@$(MAKE) -C ./shared clobber
	+@$(MAKE) -C ./C clobber
	+@$(MAKE) -C ./CUDALibraries clobber
	+@$(MAKE) -C ./OpenCL clobber

# .PHONY: install
# install: 
# 	+@$(MAKE) -C ./C install
# 	+@$(MAKE) -C ./CUDALibraries install
# 	+@$(MAKE) -C ./shared install
# 	+@$(MAKE) -C ./OpenCL install

# .PHONY: uninstall
# uninstall:
# 	+@$(MAKE) -C ./C uninstall
