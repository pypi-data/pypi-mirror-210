import argparse
import sys

from clementine.version import __version__


def main():
  parser = argparse.ArgumentParser(
      prog='clementine',
      description='🍊 clementine is a sweet little Python package.',
  )
  parser.version = f'🍊 clementine v{__version__}'
  parser.add_argument('-v', '--version', action='version')

  parser.parse_args()
  if len(sys.argv) == 1:
    parser.print_help()


if __name__ == '__main__':
  main()
