THEMES = green
DEFAULT_THEME = green
SOURCE_DIRECTORY = sass
BUILD_DIRECTORY = build
INSTALLATION_DIRECTORY = ../Themes/default/styles
SOURCE_FILES = $(shell find ${SOURCE_DIRECTORY} -name '*.scss')

define THEME_template =
INPUT_FILE_$1 = ${SOURCE_DIRECTORY}/theme-${1}/main.scss
OUTPUT_FILE_$1 = ${BUILD_DIRECTORY}/theme-${1}.css

.PHONY: all-$1 install-$1 validate-$1

all: all-$1

all-$1: $${OUTPUT_FILE_$1}

$${OUTPUT_FILE_$1}: ${SOURCE_FILES} | ${BUILD_DIRECTORY}
	sass --no-source-map $${INPUT_FILE_$1}:$$@

install: install-$1

install-$1: all-$1 | ${INSTALLATION_DIRECTORY}
	cp $${OUTPUT_FILE_$1} ${INSTALLATION_DIRECTORY}

validate: validate-$1

validate-$1: all-$1
	-css-validator --profile=css3svg --warning=2 $${OUTPUT_FILE_$1}

endef

.DEFAULT_GOAL = all

.PHONY: all clean distclean install validate

install:
	cd ${INSTALLATION_DIRECTORY} \
		&& cp theme-${DEFAULT_THEME}.css theme-default.css

${BUILD_DIRECTORY} ${INSTALLATION_DIRECTORY}:
	mkdir -p $@

clean:
	${RM} -r ${BUILD_DIRECTORY}

distclean: clean
	${RM} -r ${INSTALLATION_DIRECTORY}

$(foreach theme,${THEMES},$(eval $(call THEME_template,${theme})))
