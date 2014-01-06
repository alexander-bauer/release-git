PROGRAM_NAME := release
VERSION := $(shell git describe --dirty=+)

# If the prefix is not yet defined, define it here.
ifndef prefix
prefix = /usr/local
endif

.PHONY: all install clean

all: $(PROGRAM_NAME) man

$(PROGRAM_NAME): release.py
	cp release.py $(PROGRAM_NAME)
	sed -i 's/VERSION=""/VERSION="$(VERSION)"/' $(PROGRAM_NAME)

# Compile man page sources in `doc` to `man`.
man: doc/release.1
	test -d man || mkdir -p man
	gzip -c doc/release.1 > man/release.1.gz

install: all
	test -d $(prefix)/bin || mkdir -p $(prefix)/bin
	test -d $(prefix)/share/man/man1 || mkdir -p $(prefix)/share/man/man1
	install -m 0755 $(PROGRAM_NAME) $(prefix)/bin
	install -m 0644 man/release.1.gz $(prefix)/share/man/man1
	rm $(PROGRAM_NAME)

clean:
	- rm -rf $(PROGRAM_NAME)
