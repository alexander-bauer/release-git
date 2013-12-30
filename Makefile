PROGRAM_NAME := release-git
VERSION := $(shell git describe --dirty=+)

# If the prefix is not yet defined, define it here.
ifndef prefix
prefix = /usr/local
endif

.PHONY: all install clean

$(PROGRAM_NAME): release.py
	cp release.py $(PROGRAM_NAME)
	sed -i 's/VERSION=""/VERSION="$(VERSION)"/' $(PROGRAM_NAME)

all: $(PROGRAM_NAME)

install: all
	test -d $(prefix)/bin || mkdir -p $(prefix)/bin
	install -m 0755 $(PROGRAM_NAME) $(prefix)/bin
	rm $(PROGRAM_NAME)

clean:
	- rm -rf $(PROGRAM_NAME)
