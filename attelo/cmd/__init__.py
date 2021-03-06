"""
attelo subcommands
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from . import\
    decode,\
    enfold,\
    evaluate,\
    learn,\
    report

SUBCOMMANDS = [learn, decode, enfold, evaluate, report]
