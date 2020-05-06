### Makefile for fork of plasTeX project

## See https://stackoverflow.com/a/677212 for `which' vs `command -v'.
## See
##
## https://stackoverflow.com/a/17550243
## https://stackoverflow.com/questions/5618615#comment97811935_34756868
##
## about the `;'.  Without it, one gets a "make: command: Command not
## found" error.
ifneq (,$(shell command -v git ;))
include misc/git.mk
endif

ifneq (,$(shell command -v docker ;))
include misc/docker.mk
endif

ifneq (,$(shell command -v pyenv ;))
include misc/pyenv.mk
endif

### End of file
