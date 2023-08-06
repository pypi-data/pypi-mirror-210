from textwrap import dedent
from freyja_plot import __version__
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description=dedent("""
        A python module for plotting aggregated `freyja demix` lineage abundances. 
        `freyja_plot` is not currently set up for CLI, but conceivably could be in the future. 
        For now, it is best used as a module in a python script. 
    """))
    parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
    parser.parse_args()

if __name__ == "__main__":
    main()