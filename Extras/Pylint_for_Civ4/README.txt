To inform Pylint or other static code analyser about the Civ4 SDK
function you could use this package. The folder PythonApi contain
a set of classes/function stubs.

Setup:

1. Add the following lines to your Pylint configuration,
   but adapt the folder and mod names on your requirements.

    init-hook='API="[absolute path to this folder]/Civ4PythonApi"'
    init-hook='CIV4="C:\\Civ4"; MOD="PieAncientEuropeV'
    init-hook='import sys; sys.path.append(API); import Civ4Paths'
    init-hook='sys.path.extend(Civ4Paths.civ4_paths(CIV4, MOD))'

  ( Use '--init-hook' but not 'init-hook' if you use it as arguments.)


2. The old code of Civ4 does violate many PEP8 styling rules. We suggest
   to disable several warnings to made the critical warings/errors 
   more present.

    disable=too-many-lines,no-init,old-style-class,no-self-use,unused-argument,too-few-public-methods,too-many-public-methods,interface-not-implemented,too-many-arguments
