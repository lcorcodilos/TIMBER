#####################################################################################################
# Name: TrigTester.py                                                                               #
# Author: Lucas Corcodilos                                                                          #
# Date: 1/2/2020                                                                                    #
# Description: Tests the efficiency of triggers that are NOT included in a specified trigger        #
#     selection. Will print the following for each trigger:                                         #
#         pass(cuts & tested HLT & !(standard HLTs))/pass(cuts & (standard HLTs))                   #
#     The numerical values will be printed and plotted in a histogram for each HLT considered.      #
#     It's recommended to run  TIMBER to slim and skim before using this tool as it will            #
#     simplify the evaluation (for speed and your sanity)                                           #
#####################################################################################################

import ROOT,pprint,sys
from collections import OrderedDict
from optparse import OptionParser

pp = pprint.PrettyPrinter(indent=4)
ROOT.gStyle.SetOptStat(0)

parser = OptionParser(usage="usage: %prog [options]")

parser.add_option('-i', '--input', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-t', '--tree', metavar='TTREE', type='string', action='store',
                default   =   'Events',
                dest      =   'tree',
                help      =   'Name of the tree in the input file with the HLT branches')
parser.add_option('-c', '--cuts', type='string', action='store',
                default   =   '1',
                dest      =   'cuts',
                help      =   'C++ boolean evaluation of branches to select on (excluding triggers)')
parser.add_option('--not', type='string', action='store',
                default   =   '0',
                dest      =   'Not',
                help      =   'C++ boolean evaluation of HLTs to veto that would otherwise be in your selection')
parser.add_option('--ignore', metavar='LIST', type='string', action='store',
                default   =   '',
                dest      =   'ignore',
                help      =   'Comma separated list of strings. Ignore any triggers containing one of these strings in the name (case insensitive).')
parser.add_option('--threshold', type='float', action='store',
                default   =   0.01,
                dest      =   'threshold',
                help      =   'Threshold of (pass events)/(total events) of HLTs tested to determine whether info should be recorded (default to > 0.01)')
parser.add_option('--manual', type='string', action='store',
                default   =   '',
                dest      =   'manual',
                help      =   'Rather than looping over all triggers, supply comma separated list of those to consider.')
parser.add_option('--vs', type='string', action='store',
                default   =   '',
                dest      =   'vs',
                help      =   'Branch name to compare HLTs against. Plots together the distribution of the provided variable for events that pass the top 9 most efficient triggers (vetoing those events that pass the triggers in the `not` option).')
parser.add_option('--noTrig', action='store_true',
                default   =   False,
                dest      =   'noTrig',
                help      =   'Check if there is no positive trigger for the event (should never happen).')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'output',
                help      =   'Output file name (no extension - will be pdf). Defaults to variation of input file name.')

(options, args) = parser.parse_args()

# Quick function for drawing trigger bits vs a variable
def drawHere(name,tree,var,cuts,histWbinning=None):
    # base_hist = ROOT.TH1F(name,name,14,array.array('d',[700,800,900,1000,1100,1200,1300,1400,1500,1700,1900,2100,2500,3000,3500]))
    if histWbinning != None: 
        base_hist = histWbinning.Clone(name)
        base_hist.Reset()

    tree.Draw('%s>>%s'%(var,name),cuts)
    outhist = ROOT.gDirectory.Get(name)
    outhist.GetYaxis().SetTitle("Gain/Current")
    outhist.GetXaxis().SetTitle(var)
    return outhist

# Open file/tree
if options.input.endswith('.root'):
    f = ROOT.TFile.Open(options.input)
    tree = f.Get(options.tree)
else:
    tree = ROOT.TChain(options.tree)
    txt = open(options.input,'r')
    for f in txt.readlines():
        if f != '':
            tree.Add(f.strip())
    txt.close()
possible_trigs = {}

# If just checking if there are no trigger bits for any events...
if options.noTrig:
    all_trigs = []
    for branchObj in tree.GetListOfBranches():
        if 'HLT_' in branchObj.GetName():
            all_trigs.append(branchObj.GetName())

    nEntries= tree.GetEntries()
    for i in range(0, nEntries):
        tree.GetEntry(i)
        found_trig = False
        sys.stdout.write("\r%d/%s" % (i,nEntries))
        sys.stdout.flush()
        for trig in all_trigs:
            trig_bit = getattr(tree,trig)
            if trig_bit != 0: 
                found_trig = True
                break

        if not found_trig: print('\nEvent %s has no trigger bits that are non-zero!' %(i))
    quit()

# Otherwise, establish what we're looking for
fullSelection_string = ''
if options.cuts != '': fullSelection_string += '(%s)'%(options.cuts)
if options.Not != '': 
    if fullSelection_string == '': fullSelection_string += '!(%s)'%(options.Not)
    else: fullSelection_string += '&& !(%s)'%(options.Not)

print('Full selection will be evaluated as '+fullSelection_string)
if options.vs == '': 
    fullSelection = tree.GetEntries(fullSelection_string)
    print('Selected %s events with standard triggers' %fullSelection)
else: 
    fullSelection = drawHere('fullSelection',tree,options.vs,fullSelection_string)
    print('Selected %s events with standard triggers' %fullSelection.Integral())

# Automatically scan all triggers
if options.manual == '':
    for branchObj in tree.GetListOfBranches():
        if 'HLT' in branchObj.GetName():
            # Ignore trigger if requested 
            ignore = False
            for ign in options.ignore.split(','):
                if ign != '' and ign.lower() in branchObj.GetName().lower(): 
                    print('Ignoring '+branchObj.GetName())
                    ignore = True
            if ignore: continue

            # Say what's being processed
            print(branchObj.GetName()+'...')

            # If no comparison against another branch, just count
            if options.vs == '':
                thisTrigPassCount = float(tree.GetEntries('(%s)==1 && %s==1 && !(%s)'%(options.cuts,branchObj.GetName(),options.Not)))
                if thisTrigPassCount/(fullSelection) > options.threshold: possible_trigs[branchObj.GetName()] = '%s/%s = %.2f' % (int(thisTrigPassCount),int(fullSelection),thisTrigPassCount/fullSelection)
            # If comparing against another branch, draw
            else:
                thisTrigPassCount = drawHere('pass_'+branchObj.GetName(),tree,options.vs,'(%s)==1 && %s==1 && !(%s)'%(options.cuts,branchObj.GetName(),options.Not),histWbinning=fullSelection)
                ratio = thisTrigPassCount.Clone('ratio_'+branchObj.GetName())
                ratio.Divide(fullSelection)
                # ratio.Draw('hist')
                # raw_input(ratio.GetName())
                possible_trigs[branchObj.GetName()] = ratio


# Only consider those triggers manually specified
else:
    for trig in options.manual.split(','):
        if trig not in [b.GetName() for b in tree.GetListOfBranches()]:
            continue
        branchObj = tree.GetBranch(trig)
        # If no comparison against another branch, just count
        if options.vs == '':
            thisTrigPassCount = float(tree.GetEntries('(%s)==1 && %s==1 && !(%s)'%(options.cuts,branchObj.GetName(),options.Not)))
            if thisTrigPassCount/(fullSelection) > options.threshold: possible_trigs[branchObj.GetName()] = '%s/%s = %.2f' % (int(thisTrigPassCount),int(fullSelection),thisTrigPassCount/fullSelection)
        # If comparing against another branch, draw
        else:
            thisTrigPassCount = drawHere('pass_'+branchObj.GetName(),tree,options.vs,'(%s)==1 && %s==1 && !(%s)'%(options.cuts,branchObj.GetName(),options.Not),histWbinning=fullSelection)
            ratio = thisTrigPassCount.Clone('ratio_'+branchObj.GetName())
            ratio.Divide(fullSelection)
            possible_trigs[branchObj.GetName()] = ratio

# pp.pprint(possible_trigs)
# Print out results if just counting
if options.vs == '':
    ordered = OrderedDict(sorted(possible_trigs.items(), key=lambda t: float(t[1].split(' = ')[-1]),reverse=True))
    for n,v in ordered.items():
        print ('\t%s: %s'%(n,v))

    # Book histogram
    out = ROOT.TH1F('out','out',len(possible_trigs.keys()),0,len(possible_trigs.keys()))
    out.GetYaxis().SetTitle("Gain/Current")
    out.GetXaxis().SetTitle("")

    # Loop over HLTs/bins and set bin label and content
    bincount = 1
    for k in ordered.keys():
        out.GetXaxis().SetBinLabel(bincount,k.replace('HLT_','')[:25]) # truncate file name so that it fits in bin label
        out.SetBinContent(bincount,float(possible_trigs[k].split(' = ')[-1]))
        bincount+=1

    # Save histogram
    c = ROOT.TCanvas('c','c',1400,700)
    c.SetBottomMargin(0.35)
    out.Draw('hist')
    if options.output == '':
        c.Print('TrigTester_'+options.input.split('.root')[0]+'.pdf','pdf')
    else:
        c.Print(options.output+'.pdf','pdf')

# Draw results as function of options.vs variable
else:
    # Get number of triggers to start
    ntrigs = len(possible_trigs.keys())

    # As long as we have > 9 triggers... (9 chosen for the sake of simplicity in coloring later on)
    while ntrigs>9:
        # Initialize minimum and mintrig name
        minval = 100
        mintrig = ''
        # Loop over all triggers and find minimum
        for k in possible_trigs.keys():
            if possible_trigs[k].Integral() < minval:
                print('Replacing %s(%s) with %s(%s) as min' %(mintrig,minval,k,possible_trigs[k].Integral()))
                minval = possible_trigs[k].Integral()
                mintrig = k

        # Drop the found minimum and reflect this in the ntrigs count
        if mintrig in possible_trigs.keys():
            print('Removing min %s(%s)' %(mintrig,minval))
            del possible_trigs[mintrig]

        ntrigs = ntrigs-1

    # Draw with legend
    c = ROOT.TCanvas('c','c',1400,700)
    color = 1
    l = ROOT.TLegend(0.5,0.4,0.9,0.9)

    # Find maximum
    trig_max = -1
    for k in possible_trigs.keys():
        if possible_trigs[k].GetMaximum()>trig_max:
            trig_max = possible_trigs[k].GetMaximum()

    first = True
    for k in possible_trigs.keys():
        print('%s: %s' %(k,possible_trigs[k].Integral()))
        this_hist = possible_trigs[k]
        if first: this_hist.SetMaximum(trig_max*1.1)
        this_hist.SetLineColor(color)
        this_hist.SetTitle('Trigger test as a function of %s'%options.vs)
        color+=1
        if first: this_hist.Draw('hist')
        else: this_hist.Draw('histsame')
        first = False

        l.AddEntry(this_hist,k,'l')

    l.Draw()

    if options.output == '':
        c.Print('TrigTester_'+sys.argv[1].split('.')[0]+'_vs_'+options.vs+'.pdf','pdf')
    else:
        c.Print(options.output+'.pdf','pdf')
