#!/usr/bin/env python

import os, subprocess, sys, tempfile

VERSION=""

RELEASETYPE = {
    "major": 0,
    "minor": 1,
    "patch": 2,
    "prerelease": 3
}

FLAGMAP = {
    "s": "sign",
    "C": "cwd",
    "p": "prerelease"
}

# ARGFLAGS specifies the flags which require an argument.
ARGFLAGS = { "cwd", "prerelease" }

# splitflags is a convenience function which parses the given
# arguments and removes flags and their values from them. It considers
# flags to be any argument of the form "--name", and a value to be any
# argument following a flag. It returns the remaining arguments and
# the flags (which are tuples, with the second element being value) in
# that order.
def splitflags(argv, flagmap):
    newargv, flags = [], []
    needargfor = None
    
    # For each element in the given list, check if it begins with
    # "--". If so, strip the prefix and store that argument
    # temporarily. If the previous element was a flag, consider the
    # current argument a value to that flag, and append a tuple to the
    # "flags" list. If neither of the above is true, append the item
    # to newargv.
    for arg in argv:
        if needargfor != None:
            flags.append((needargfor, arg))
            needargfor = None
        elif len(arg) > 2 and arg[0:2] == "--":
            flag = arg[2:]
            # If the flag needs an argument, set the state variable.
            if flag in ARGFLAGS:
                needargfor = flag
            else:
                # Otherwise, just append it.
                flags.append((flag, None))

        elif len(arg) > 1 and arg[0] == "-":
            # If it's not a long-form flag, but instead a short-form
            # flag, try to look it up in the map. If that fails, put
            # it in verbatim.
            try:
                flag = flagmap[arg[1:]]
            except KeyError:
                flag = arg[1:]

            # As above, check if it needs an argument, and if not,
            # just put it in the list.
            if flag in ARGFLAGS:
                needargfor = flag
            else:
                flags.append((flag, None))

        else:
            newargv.append(arg)

    return newargv, flags

# getflagvalue searches through the given list of tuples linearly and
# return the value matching the given flag. If it is not a flag which
# accepts a value, it returns True. If there is no such flag, it
# returns the default value.
def getflagvalue(flag, flags, default=None):
    for tup in flags:
        if tup[0] == flag:
            # If there is no value attached to the flag, return True.
            value = tup[1]
            return value if value != None else True
    
    return default

# git uses the subprocess module to invoke git with the given
# arguments, and returns the stripped stdout output and the error
# code.
def git(cwd, args):
    args.insert(0, "git")
    p = subprocess.Popen(args, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.communicate()[0].strip(), p.returncode

# gitEdit invokes the configured git editor on the given file. It
# should never fail, but returns the exit code anyway.
def gitEdit(cwd, filepath):
    # Invoke 'git var GIT_EDITOR' in order to get the name of the
    # user's preferred editor.
    editor, code = git(cwd, ["var", "GIT_EDITOR"])

    # args will be the editor arguments, split dumbly on spaces,
    # followed by the filepath.
    args = editor.split() + [filepath]

    return subprocess.call(args, cwd=cwd)

# gitChangelog invokes 'git log' with a specific format argument,
# between the given top (default "HEAD") and the given ref, and
# returns the output and exit code.
def gitChangelog(cwd, ref, top="HEAD"):
    # Define the refrange as ref..top, which selects only the commits
    # between top and the given ref.
    refrange = ref + ".." + top

    # Before we return, append a line seperator to the output.
    output, code = git(cwd, ["log", "--format=* %s", refrange])
    return output + os.linesep, code

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
    # 2, and a prerelease by 3. If there is a prerelease in the
    # current version, no matter the release type, it is only replaced
    # by the given one.
    def increment(this, releasetype, prerelease=""):
        # If there is a current prerelease, just set the new one. That
        # way, doing any sort of increment from a prerelease just
        # changes or strips the prerelease.
        if len(this.prerelease) > 0:
            this.prerelease = prerelease
            return this

        # Perform the appropriate incrementation.
        this.prerelease = prerelease
        if releasetype == 0:
            this.major += 1
            this.minor = 0
            this.patch = 0
        elif releasetype == 1:
            this.minor += 1
            this.patch = 0
        elif releasetype == 2:
            this.patch += 1

        # Return the new version, for convenience.
        return this

    # last finds the most recent version acording to the given
    # parameters. For example, the last minor version from 0.3.0 would
    # be 0.2.0. It obeys the same releasetype rules as increment. If
    # there is a prerelease given, it does not decrement any version
    # numbers. If there is no previous version of the given type, it
    # returns the same version.
    def last(this, releasetype, prerelease=""):
        lv = Version(this.major, this.minor, this.patch,
                     prerelease=prerelease)

        # If the prerelease was set, then there is no version
        # decrementing.
        if len(prerelease) > 0:
            return lv

        # Perform the appropriate decrementation.
        if releasetype == 0 and lv.major > 0:
            lv.major -= 1
        elif releasetype == 1 and lv.minor > 0:
            lv.minor -= 1
            lv.patch = 0
        elif releasetype == 2 and lv.patch > 0:
            lv.patch -= 1

        return lv

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
                                       "--tags", "--abbrev=0",
                                       this.ref])

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

    def changelog(this):
        return gitChangelog(this.cwd, this.lasttag(), this.ref)

    def lasttag(this):
        return "v" + this.version.last(this.releasetype,
                                       this.lastprerelease).str()

    def __init__(this, releasetype, ref="HEAD", cwd=""):
        this.ref = ref if len(ref) > 0 else "HEAD"
        this.cwd = cwd if len(cwd) > 0 else os.getcwd()
        this.version = this.findVersion()
        this.releasetype = releasetype
        this.lastprerelease = (this.version.prerelease
                               if releasetype == 3 else "")

def usage():
    print """release <releasetype> [committish]
\treleasetype must be either: major, minor, patch, or prerelease. See
\t'man release' for more details."""

def main(argc, argv):
    # Parse the flags, if there are any.
    argv, flags = splitflags(argv, FLAGMAP)
    argc = len(argv)

    # Check if we're doing a dryrun. If so, nothing should be
    # modified.
    dryrun = getflagvalue("dryrun", flags, default=False)
    if dryrun:
        print " - - DRYRUN - - "

    # releasetype determines what kind of release is being done. It is
    # set in the below if/else block.
    cwd = getflagvalue("cwd", flags, default="")
    prerelease = getflagvalue("prerelease", flags, default="")
    signing = getflagvalue("sign", flags, default=False)
    ref = ""

    if argc >= 2:
        try:
            # If the first argument is a release type, then set the
            # variable.
            releasetype = RELEASETYPE[argv[1]]
        except KeyError:
            # If not, raise an error.
            usage()
            return 1
            
    if argc == 3:
        ref = argv[2]
  
    if argc == 1 or argc > 3:
        usage()
        return 1

    # Get data from the program we're going to be working on.
    try:
        current = Program(releasetype, ref, cwd)
    except OSError:
        print "Could not open directory"
        return 1

    # Increment the appropriate version number, if appropriate.
    current.version.increment(releasetype, prerelease)

    # Generate a changelog file.
    with tempfile.NamedTemporaryFile() as changelog:
        changelogString, code = current.changelog()
        if code != 0:
            print "Changelog could not be retrieved ({}..{})".format(
                current.lasttag(), current.ref)
            return

        changelog.write("Version {}\n\nChanged since {}:\n"
                        .format(current.version.str(), current.lasttag()))
        changelog.write(changelogString)
        changelog.flush()

        gitEdit(current.cwd, changelog.name)

        # Tag the latest commit.
        tagname = "v" + current.version.str()


        # Create the tag, using the changelog file as the tag message.
        args = ["tag", "-a", tagname, "-F", changelog.name]
        # If we're instructed to sign the tag, add that argument.
        if signing:
            args.insert(2, "-s")

        if not dryrun:
            output, code = git(current.cwd, args)
            if code != 0:
                print output
                return code
        else:
            print "Would tag commit now"

    # If all went well, give the new tag name.
    print "Tagged as {} {}".format(tagname, "(signed)" if
                                   signing else "")

if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))
