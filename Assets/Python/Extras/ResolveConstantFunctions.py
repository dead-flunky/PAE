#!/usr/bin/python
# vim: set fileencoding=utf-8

# Change source code to omit mutliple function calls.

import sys
import os
import glob
import re

Mod = "PieAncientEuropeV"
ModOut = "PAE_Opt"
# Mod = "Test"

PyModPath = os.path.join("Mods", Mod, "Assets", "Python")
PyOutPath = os.path.join("Mods", ModOut, "Assets", "Python")
SourceFolders = [
    os.path.join("..", "Assets", "Python"),  # Vanilla
    os.path.join("..", "Warlords", "Assets", "Python"),  # WL
    os.path.join("Assets", "Python"),  # BTS
    PyModPath,  # Mod
]

try:
    from CvPythonExtensions import *
    gc = CyGlobalContext()
    ArtFileMgr = CyArtFileMgr()
    localText = CyTranslator()
except:
    class CyGlobalContext:  # Dummy declarations for testing
        def getInfoTypeForString(self, sStr):
            return -1111

        def getMAX_PLAYERS(self):
            return 1888

        def getMAX_TEAMS(self):
            return 1888

        def getBARBARIAN_PLAYER(self):
            return 1888

        def getBARBARIAN_TEAM(self):
            return 1888

    gc = CyGlobalContext()


def undefined_warner(handler, *lArgs):
    s = str(handler(*lArgs))
    if(s) == "-1":
        print("Warning: %s(%s) returns %s" % (
            handler.__name__, ", ".join(lArgs), s))

    return s


def empty_str(_):
    return ""


def getInterfaceArtInfo(sArt):
    return "'" + ArtFileMgr.getInterfaceArtInfo(sArt).getPath() + "'"

Replace_descriptors = {
    "self_instance": (
        r'^.*'+__name__+'.*$', 0, '%s', empty_str
    ),
    "getInfoTypeForString": (
        r'(self\.)?gc.getInfoTypeForString\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
        2, '%s',  # Resolving of args for Function handler
        gc.getInfoTypeForString,  # Function handler
    ),
    "findInfoTypeNum": (
        r'CvUtil.findInfoTypeNum\([^,]*,[^,]*,\s*[\'"]([^\'"]*)[\'"]\s*\)',
        1, '%s',  # Resolving of args for Function handler
        gc.getInfoTypeForString,  # Function handler
    ),
    "getInterfaceArtInfo": (
        r'ArtFileMgr.getInterfaceArtInfo\(\s*[\'"]([^\'"]*)[\'"]\s*\).getPath\(\)',
        1, '%s',
        getInterfaceArtInfo,
    ),
}
# def findInfoTypeNum(infoGetter, numInfos, typeStr):

Constant_substitutions = {
    "max_players": ["gc.getMAX_PLAYERS()", gc.getMAX_PLAYERS()],
    "max_teams": ["gc.getMAX_TEAMS()", gc.getMAX_TEAMS()],
    "barb_player": ["gc.getBARBARIAN_PLAYER()", gc.getBARBARIAN_PLAYER()],
    "barb_team": ["gc.getBARBARIAN_TEAM()", gc.getBARBARIAN_TEAM()],
}


def replace_key_functions(fsource, ftarget):
    f = file(fsource, 'rU')
    f2 = file(ftarget, 'w')
    l = f.readline()
    while(l):
        # Ignore Lines without identation"
        if l[0] == "\t" or l[:2] == "  ":
            l2 = replaceLoop(l)
        else:
            l2 = l

        f2.write(l2)
        l = f.readline()

    f2.close()
    f.close()


def replaceLoop(codeline):
    out = codeline

    # check if single comment line
    if len(out[:out.find("#")].strip()) == 0:
        return out

    for fname in Constant_substitutions:
        tConst = Constant_substitutions[fname]
        out = out.replace(tConst[0], str(tConst[1]))

    for fname in Replace_descriptors:
        tDesc = Replace_descriptors[fname]  # Tuple
        matches = list(re.finditer(tDesc[0], out))
        if len(matches) == 0:
            continue

        out2 = ""
        prev_end = 0
        for m in matches:
            out2 += out[prev_end:m.start()]
            # Parse arg (currenty only one arg supported)
            arg1 = tDesc[2] % (m.group(tDesc[1]),)
            # Evaluate expression
            out2 += str(undefined_warner(tDesc[3], arg1))
            prev_end = m.end()

        out2 += out[prev_end:]
        out = out2

    return out


def main(forceUpdate=False, basedir=PyModPath, outdir=PyOutPath):

    # List of files, which already exists.
    target_files = glob.glob(outdir+"/*.py") +\
        glob.glob(outdir+"/*/*.py") + glob.glob(outdir+"/*/*/*.py")

    # Collection of files which should be parsed.
    # ("source path", timestamp_source, "target_path", timestamp_target)
    files = []

    # Map source file path to target file path and add timestamp.
    # This allows filtering of unchanged files
    # and filtering of double file (files with same target)
    # Note that basedir will vary.
    def addTargetTs(basedir, targets, s):
        t = s.replace(basedir, outdir, 1)
        if t in target_files:
            return (t, os.path.getctime(t))
        else:
            return (t, None)

    for basedir in SourceFolders:
        source_files = glob.glob(basedir+"/*.py") +\
            glob.glob(basedir+"/*/*.py") +\
            glob.glob(basedir+"/*/*/*.py")

        files.extend(
            [(x, os.path.getctime(x)) + addTargetTs(basedir, target_files, x)
             for x in source_files]
        )


    # Note that above list contain duplicates because some files exists at
    # multiple source folders. The duplicates had the same target paths.
    # We will just hold the latest instance.
    tmp = [(x[2],x) for x in files]
    files = dict(tmp).values()

    # Sort by timestamp, optional
    # files.sort(key=lambda xx: xx[1])

    # Ignore this file due parsing
    this_file_name = __name__ + ".py"

    for tF in files:
        # Check if target file is newer as source file
        if(tF[3] is not None and tF[3] > tF[1] and not forceUpdate):
            print("Skip", tF[0])
            continue

        s = tF[0]
        t = tF[2]
        targetDir = t[:t.rfind(os.path.sep)]
        fname = t[t.rfind(os.path.sep)+1:]

        if fname == this_file_name:
            continue

        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)

        print("Update '%s' -> '%s'" % (s, t))
        replace_key_functions(s, t)


if __name__ == "__main__":
    try:
        bForce = bool(int(sys.argv[1]))
    except:
        bForce = False

    main(bForce)
