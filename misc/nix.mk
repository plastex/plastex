### Makefile rules for Nix

### ==================================================================
### Variables
### ==================================================================

NIX_BUILD_COOKIE = .nix_build_DONE

### ==================================================================
### Targets
### ==================================================================

.DEFAULT_GOAL = all

.PHONY: all clean nix-build

all: ${NIX_BUILD_COOKIE}

${NIX_BUILD_COOKIE}: default.nix misc/*.nix
	nix-build
	touch $@

nix-build: ${NIX_BUILD_COOKIE}

clean:
	${RM} result ${NIX_BUILD_COOKIE}

### End of file
