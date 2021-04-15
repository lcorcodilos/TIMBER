from time import time
from argparse import ArgumentParser

from TIMBER.Analyzer import analyzer

parser = ArgumentParser()
parser.add_argument('-s', type=str, dest='setname',
                    action='store', required=True,
                    help='Setname to process.')
parser.add_argument('-y', type=str, dest='era',
                    action='store', required=True,
                    help='Year of set (16, 17, 18).')
args = parser.parse_args()

a = analyzer('locations/%s_%s.txt'%(args.setname,args.year))