#!/usr/bin/env python

import os, subprocess, sys

RELEASETYPE = {
    "major": 0,
    "minor": 1,
    "patch": 2,
    "prerelease": 3
}

FLAGMAP = {
    "p": "prerelease"
}

# splitflags is a convenience function which parses the given
# arguments and removes flags and their values from them. It considers
# flags to be any argument of the form "--name", and a value to be any
# argument following a flag. It returns the remaining arguments and
# the flags (which are tuples, with the second element being value) in
# that order.
def splitflags(argv, flagmap):
    newargv, flags = [], []
    currentflag = None
    
    # For each element in the given list, check if it begins with
    # "--". If so, strip the prefix and store that argument
    # temporarily. If the previous element was a flag, consider the
    # current argument a value to that flag, and append a tuple to the
    # "flags" list. If neither of the above is true, append the item
    # to newargv.
    for arg in argv:
        if currentflag != None:
            flags.append((currentflag, arg))
            currentflag = None
        elif len(arg) > 2 and arg[0:2] == "--":
            currentflag = arg[2:]
        elif len(arg) > 1 and arg[0] == "-":
            # If it's not a long-form flag, but instead a short-form
            # flag, try to look it up in the map. If that fails, put
            # it in verbatim.
            try:
                currentflag = flagmap[arg[1:]]
            except KeyError:
                currentflag = arg[1:]
        else:
            newargv.append(arg)

    return newargv, flags

# getflagvalue searches through the given list of tuples linearly and
# return the value matching the given flag. If there is none, it
# returns a blank string.
def getflagvalue(flag, flags):
    for tup in flags:
        if tup[0] == flag:
            return tup[1]
    
    return ""

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
    
    # increment modifies the current version according to the given
    # parameters. A major change is denoted by 0, minor by 1, patch by
    # 2, and a prerelease by 3.
    def increment(this, releasetype, prerelease=""):
        # Perform the appropriate incrementation.
        if releasetype == 0:
            this.major += 1
            this.minor = 0
            this.patch = 0
            this.prerelease = prerelease
        elif releasetype == 1:
            this.minor += 1
            this.patch = 0
            this.prerelease = prerelease
        elif releasetype == 2:
            this.patch += 1
            this.prerelease = prerelease
        elif releasetype == 3:
            this.prerelease = prerelease

        # Return the new version, for convenience.
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
    # Parse the flags, if there are any.
    argv, flags = splitflags(argv, FLAGMAP)
    argc = len(argv)

    # releasetype determines what kind of release is being done. It is
    # set in the below if/else block.
    cwd = ""
    prerelease = getflagvalue("prerelease", flags)

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

    # Increment the appropriate version number, if appropriate.
    current.version.increment(releasetype, prerelease)

    # Tag the latest commit.
    tagname = "v" + current.version.str()
    output, code = git(current.cwd, ["tag", "-a", "-s", tagname])
    if code != 0:
        print output
        return code

    # If all went well, give the new tag name.
    print "Tagged as %q".format(tagname)

if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))
