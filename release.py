#!/usr/bin/env python

import os, subprocess, sys

RELEASETYPE = {
    "major": 0,
    "minor": 1,
    "patch": 2,
    "prerelease": 3
}

# git uses the subprocess module to invoke git with the given
# arguments, and returns the stripped stdout output and the error
# code.
def git(cwd, args):
    args.insert(0, "git")
    p = subprocess.Popen(args, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.communicate()[0].strip(), p.returncode

class Version:
    def parse(this, string):
        parts = string.strip().split(".")
        
        # Set the major and minor versions. If there are any
        # exceptions, the parent must handle them.
        this.major = int(parts[0])
        this.minor = int(parts[1])
        
        # Split the patch version from the label, if applicable, and
        # assign them.
        suffixparts = parts[2].split("-")
        this.patch = int(suffixparts[0])

        if len(suffixparts) > 1:
            this.prerelease = suffixparts[1]

        # Return this for convenience.
        return this
    
    def str(this):
        return "{}.{}.{}{}{}".format(
            this.major, this.minor, this.patch,
            "" if len(this.prerelease) == 0 else "-", this.prerelease)

    def __init__(this, major=0, minor=0, patch=0, prerelease=""):
        this.major = major
        this.minor = minor
        this.patch = patch
        this.prerelease = prerelease

class Program:
    def findVersion(this):
        version, code = git(this.cwd, ["describe", "--match",
                                       "v*.*.*",
                                       "--tags", "--abbrev=0"])

        if len(version) > 0 and code == 0:
            try:
                # If found, return the parsed version.
                return Version().parse(version[1:])
            except ValueError:
                # If there is an error, assume that the tag was wrong,
                # for some reason.
                pass
        
        # Otherwise, return the zero version.
        return Version()

    def __init__(this, cwd=""):
        this.cwd = cwd if len(cwd) > 0 else os.getcwd()
        this.version = this.findVersion()

def main(argc, argv):
    # releasetype determines what kind of release is being done. It is
    # set in the below if/else block.
    cwd = ""

    # Check if no argument was provided. If not, then assume we are
    # making a commit for the current release.
    if argc == 1:
        releasetype = -1
    elif argc == 2:
        try:
            # If the first argument is a release type, then set the
            # variable.
            releasetype = RELEASETYPE[argv[1]]
        except KeyError:
            # Otherwise, treat it as a path.
            cwd = argv[1]
    elif argc == 3:
        try:
            releasetype = RELEASETYPE[argv[1]]
        except KeyError:
            print "Release type unknown"
            return 1

        cwd = argv[2]
    else:
        print "Too many arguments"
        return 1

    # Get data from the program we're going to be working on.
    try:
        current = Program(cwd)
    except OSError:
        print "Could not open directory"
        return 1

    current = Program(cwd)
    print current.version.str()

if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))
