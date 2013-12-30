#!/usr/bin/env python

import os, subprocess

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
            this.label = suffixparts[1]

        # Return this for convenience.
        return this
    
    def str(this):
        return "{}.{}.{}{}{}".format(
            this.major, this.minor, this.patch,
            "" if len(this.label) == 0 else "-", this.label)

    def __init__(this, major=0, minor=0, patch=0, label=""):
        this.major = major
        this.minor = minor
        this.patch = patch
        this.label = label

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

    def __init__(this):
        this.cwd = os.getcwd()
        this.version = this.findVersion()

def main():
    current = Program()
    print current.version.str()

if __name__ == "__main__":
    main()
