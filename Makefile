.PHONY: all check check-ssh check-ssh-pass check-scp

# Log helpers
NO_COLOR=\033[0m

OK_TAG=OK   #
OK_COLOR=\033[32;01m

WARN_TAG=WARN #
WARN_COLOR=\033[33;01m

ERROR_TAG=ERROR
ERROR_COLOR=\033[31;01m

define log = # level, message
$(if $(findstring ok, $(1)), @printf "$(OK_COLOR)[$(OK_TAG)] $(2)$(NO_COLOR)\n")
$(if $(findstring warn, $(1)), @printf "$(WARN_COLOR)[$(WARN_TAG)] $(2)$(NO_COLOR)\n")
$(if $(findstring error, $(1)), @printf "$(ERROR_COLOR)[$(ERROR_TAG)] $(2)$(NO_COLOR)\n")
endef

# Omega device host, assuming we are connected to it's hotspot this is the default
DEVICE_USER=root
DEVICE_PASSWORD=$(shell cat ./password)
DEVICE_HOST=192.168.3.1
DEVICE_COMBO=$(DEVICE_USER)@$(DEVICE_HOST)
DEVICE_DIR=/root

SSH_PASS_CMD=sshpass -p $(DEVICE_PASSWORD)
SSH_CMD=$(SSH_PASS_CMD) ssh -t $(DEVICE_COMBO)

all: index.html main.py

index.html: check
	$(call log,ok,Creating static directory)
	$(SSH_PASS_CMD) $(SSH_CMD) "mkdir -p /root/static"

	$(call log,ok,Uploading ./static/* to $(DEVICE_DIR)/static/*)
	$(SSH_PASS_CMD) scp ./static/* $(DEVICE_COMBO):$(DEVICE_DIR)/static/

main.py: check
	$(call log,ok,Uploading main.py to $(DEVICE_DIR)/main.py)
	$(SSH_PASS_CMD) scp ./main.py $(DEVICE_COMBO):$(DEVICE_DIR)

	$(call log,ok,Running main.py)
	$(SSH_CMD) "python $(DEVICE_DIR)/main.py"

ssh: check
	$(SSH_CMD)

python-setup: check
	$(SSH_CMD) "opkg update && opkg install python-light python-pip pythonOnionI2C && pip install --user Flask"

# Check all programs are installed
# Make is assumed to be installed since this is running...
check: check-ssh check-ssh-pass check-password check-scp
check-ssh:
ifeq (, $(shell which ssh))
	$(call log,error,ssh is not installed)
	exit 1
endif

check-ssh-pass:
ifeq (, $(shell which sshpass))
	$(call log,error,sshpass is not installed)
	exit 1
endif

check-password:
ifeq ($(DEVICE_PASSWORD),)
	$(call log,error,No password file found)
	exit 1
endif

check-scp:
ifeq (, $(shell which scp))
	$(call log,error,scp is not installed)
	exit 1
endif
