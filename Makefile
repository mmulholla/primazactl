# VERSION defines the project version for the bundle.
# Update this value when you upgrade the version of your project.
# To re-generate a bundle for another specific version without changing the standard setup, you can:
# - use the VERSION as arg of the bundle target (e.g make bundle VERSION=0.0.2)
# - use environment variables to overwrite this value (e.g export VERSION=0.0.2)
VERSION ?= 0.0.1

# Setting SHELL to bash allows bash commands to be executed by recipes.
# Options are set to exit when a recipe line exits non-zero or a piped command fails.
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

PROJECT_DIR := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))

PRIMAZA_REPO = https://github.com/primaza/primaza.git
PRIMAZA_BRANCH = main

.PHONY: all
all: kustomize

##@ General

# The help target prints out all targets with their descriptions organized
# beneath their categories. The categories are represented by '##@' and the
# target descriptions by '##'. The awk commands is responsible for reading the
# entire set of makefiles included in this invocation, looking for lines of the
# file as xyz: ## something, and then pretty-format the target and help. Then,
# if there's a line with ##@ something, that gets pretty-printed as a category.
# More info on the usage of ANSI control characters for terminal formatting:
# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
# More info on the awk command:
# http://linuxcommand.org/lc3_adv_awk.php

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development


ifndef ignore-not-found
  ignore-not-found = false
endif

##@ Build Dependencies


## Location to install dependencies to
LOCALBIN ?= $(PROJECT_DIR)/scripts/bin
$(LOCALBIN):
	mkdir -p $(LOCALBIN)

## Tool Binaries
KUSTOMIZE ?= $(LOCALBIN)/kustomize

## Tool Versions
KUSTOMIZE_VERSION ?= v3.8.7

OUTPUT_DIR ?= $(PROJECT_DIR)/out
$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)
PYTHON_VENV_DIR = $(OUTPUT_DIR)/venv3
HACK_DIR ?= $(PROJECT_DIR)/hack

PRIMAZA_CONFIG = $(PROJECT_DIR)/scripts/bin/primaza_config_latest.yaml

KUSTOMIZE_INSTALL_SCRIPT ?= "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"
.PHONY: kustomize
kustomize: $(KUSTOMIZE) ## Download kustomize locally if necessary.
$(KUSTOMIZE): $(LOCALBIN)
	test -s $(LOCALBIN)/kustomize || { curl -Ss $(KUSTOMIZE_INSTALL_SCRIPT) | bash -s -- $(subst v,,$(KUSTOMIZE_VERSION)) $(LOCALBIN); }

.PHONY: config
config: kustomize ## Get config files from primaza repo.
	rm -rf temp
	git clone $(PRIMAZA_REPO) temp
	cd temp && git checkout $(PRIMAZA_BRANCH)
	$(KUSTOMIZE) build config/default >> temp/config/primaza_config_main.yaml
	rm -rf temp

.PHONY: all
all: lint-python install config

.PHONY: install
install: setup-venv ## Setup the environment for the acceptance tests
	$(PYTHON_VENV_DIR)/bin/pip install -q -r scripts/src/requirements.txt

.PHONY: setup-venv
setup-venv: ## Setup virtual environment
	python3 -m venv $(PYTHON_VENV_DIR)
	$(PYTHON_VENV_DIR)/bin/pip install --upgrade setuptools
	$(PYTHON_VENV_DIR)/bin/pip install --upgrade pip

.PHONY: lint
lint: setup-venv ## Check python code
	PYTHON_VENV_DIR=$(PYTHON_VENV_DIR) $(HACK_DIR)/check-python/lint-python-code.sh

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf $(LOCALBIN)
	rm  $(PRIMAZA_CONFIG)
