'''@docstring Common.py

Home to commonly used tools available for use that can be generic or HAMMER specific

'''

import json, ROOT
from ROOT import RDataFrame
import CMS_lumi, tdrstyle
from contextlib import contextmanager
###################
# HAMMER specific #
###################
# Returns OR string of triggers that can be given to a cut group
def GetValidTriggers(self,trigList,DataFrame):
    trigOR = ""
    colnames = DataFrame.GetColumnNames()
    for i,t in enumerate(trigList):
        if t in colnames: 
            if trigOR == '': trigOR = "(("+t+"==1)" 
            else: trigOR += " || ("+t+"==1)"
        else:
            print("Trigger %s does not exist in TTree. Skipping." %(t))

    if trigOR != "": 
        trigOR += ")" 
        
    return trigOR

# Draws a cutflow histogram using the report feature of RDF.
def CutflowHist(name,node):
    filters = node.DataFrame.GetFilterNames()
    rdf_report = node.DataFrame.Report()
    ncuts = len(filters)
    h = ROOT.TH1F(name,name,ncuts,0,ncuts)
    for i,filtername in enumerate(filters): 
        cut = rdf_report.At(filtername)
        h.GetXaxis().SetBinLabel(i+1,filtername)
        h.SetBinContent(i+1,cut.GetPass())

    return h

#----------------------------------------------#
# Build N-1 "tree" and outputs the final nodes #
# Beneficial to put most aggressive cuts first #
# Return dictionary of N-1 nodes keyed by the  #
# cut that gets dropped                        #
#----------------------------------------------#
def Nminus1(node,cutgroup):
    # Initialize
    nminusones = {}
    thisnode = node
    thiscutgroup = cutgroup

    # Loop over all cuts (`cut` is the name not the string to filter on)
    for cut in cutgroup.keys():
        # Get the N-1 group of this cut (where N is determined by thiscutgroup)
        minusgroup = thiscutgroup.Drop(cut)
        thiscutgroup = minusgroup
        # Store the node with N-1 applied
        nminusones[cut] = thisnode.Apply(minusgroup)
        
        # If there are any more cuts left, go to the next node with current cut applied (this is how we keep N as the total N and not just the current N)
        if len(minusgroup.keys()) > 0:
            thisnode = thisnode.Cut(cut,cutgroup[cut])
        else:
            nminusones['full'] = thisnode.Cut(cut,cutgroup[cut])

    return nminusones

###########
# Generic #
###########
def CompileCpp(blockcode):
    if isinstance(blockcode,str):
        ROOT.gInterpreter.Declare(blockcode)
    else:
        blockcode_str = open(blockcode,'r').read()
        ROOT.gInterpreter.Declare(blockcode_str)

def openJSON(f):
    return json.load(open(f,'r'), object_hook=ascii_encode_dict) 

def ascii_encode_dict(data):    
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

def GetHistBinningTuple(h):
    # At least 1D (since TH2 and TH3 inherit from TH1)
    if isinstance(h,ROOT.TH1):
        # Variable array vs fixed binning
        if h.GetXaxis().GetXbins().GetSize() > 0:
            xbinning = (h.GetNbinsX(),h.GetXaxis().GetXbins())
        else:
            xbinning = (h.GetNbinsX(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax())
        ybinning = ()
        zbinning = ()
        dimension = 1
    else:
        raise TypeError('ERROR: GetHistBinningTuple() does not support a template histogram of type %s. Please provide a TH1, TH2, or TH3.'%type(h))

    # Check if 2D
    if isinstance(h,ROOT.TH2):
        # Y variable vs fixed binning
        if h.GetYaxis().GetXbins().GetSize() > 0:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXbins())
        else:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXmin(),h.GetYaxis().GetXmax())
        zbinning = ()
        dimension = 2
    # Check if 3D
    elif isinstance(h,ROOT.TH3):
        # Y variable vs fixed binning
        if h.GetYaxis().GetXbins().GetSize() > 0:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXbins())
        else:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXmin(),h.GetYaxis().GetXmax())
        # Z variable vs fixed binning
        if h.GetZaxis().GetXbins().GetSize() > 0:
            zbinning = (h.GetNbinsZ(),h.GetZaxis().GetXbins())
        else:
            zbinning = (h.GetNbinsZ(),h.GetZaxis().GetXmin(),h.GetZaxis().GetXmax())
        dimension = 3

    return xbinning + ybinning + zbinning, dimension

def colliMate(myString,width=18):
    sub_strings = myString.split(' ')
    new_string = ''
    for i,sub_string in enumerate(sub_strings):
        string_length = len(sub_string)
        n_spaces = width - string_length
        if i != len(sub_strings)-1:
            if n_spaces <= 0:
                n_spaces = 2
            new_string += sub_string + ' '*n_spaces
        else:
            new_string += sub_string
    return new_string

def dictStructureCopy(inDict):
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = dictStructureCopy(v1)
        else:
            newDict[k1] = 0
    return newDict

def dictCopy(inDict):
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = dictCopy(v1)
        else:
            newDict[k1] = v1
    return newDict

def executeCmd(cmd,dryrun=False):
    print('Executing: '+cmd)
    if not dryrun:
        subprocess.call([cmd],shell=True)

def dictToLatexTable(dict2convert,outfilename,roworder=[],columnorder=[]):
    # First set of keys are row, second are column
    if len(roworder) == 0:
        rows = sorted(dict2convert.keys())
    else:
        rows = roworder
    if len(columnorder) == 0:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()
    else:
        columns = columnorder

    latexout = open(outfilename,'w')
    latexout.write('\\begin{table}[] \n')
    latexout.write('\\begin{tabular}{|c|'+len(columns)*'c'+'|} \n')
    latexout.write('\\hline \n')

    column_string = ' &'
    for c in columns:
        column_string += str(c)+'\t& '
    column_string = column_string[:-2]+'\\\ \n'
    latexout.write(column_string)

    latexout.write('\\hline \n')
    for r in rows:
        row_string = '\t'+r+'\t& '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t& '
            else:
                row_string += '- \t& '
        row_string = row_string[:-2]+'\\\ \n'
        latexout.write(row_string)

    latexout.write('\\hline \n')
    latexout.write('\\end{tabular} \n')
    latexout.write('\\end{table}')
    latexout.close()

def easyPlot(name, tag, histlist, bkglist=[],signals=[],colors=[],titles=[],logy=False,rootfile=False,xtitle='',ytitle='',dataOff=False,datastyle='pe'):  
    # histlist is just the generic list but if bkglist is specified (non-empty)
    # then this function will stack the backgrounds and compare against histlist as if 
    # it is data. The important bit is that bkglist is a list of lists. The first index
    # of bkglist corresponds to the index in histlist (the corresponding data). 
    # For example you could have:
    #   histlist = [data1, data2]
    #   bkglist = [[bkg1_1,bkg2_1],[bkg1_2,bkg2_2]]

    if len(histlist) == 1:
        width = 800
        height = 700
        padx = 1
        pady = 1
    elif len(histlist) == 2:
        width = 1200
        height = 700
        padx = 2
        pady = 1
    elif len(histlist) == 3:
        width = 1600
        height = 700
        padx = 3
        pady = 1
    elif len(histlist) == 4:
        width = 1200
        height = 1000
        padx = 2
        pady = 2
    elif len(histlist) == 6 or len(histlist) == 5:
        width = 1600
        height = 1000
        padx = 3
        pady = 2
    else:
        raise ValueError('histlist of size ' + str(len(histlist)) + ' not currently supported')

    tdrstyle.setTDRStyle()

    myCan = TCanvas(name,name,width,height)
    myCan.Divide(padx,pady)

    # Just some colors that I think work well together and a bunch of empty lists for storage if needed
    default_colors = [kRed,kMagenta,kGreen,kCyan,kBlue]
    if len(colors) == 0:   
        colors = default_colors
    stacks = []
    tot_hists = []
    legends = []
    mains = []
    subs = []
    pulls = []
    logString = ''

    # For each hist/data distribution
    for hist_index, hist in enumerate(histlist):
        # Grab the pad we want to draw in
        myCan.cd(hist_index+1)
        # if len(histlist) > 1:
        thisPad = myCan.GetPrimitive(name+'_'+str(hist_index+1))
        thisPad.cd()

        # If this is a TH2, just draw the lego
        if hist.ClassName().find('TH2') != -1:
            if logy == True:
                gPad.SetLogy()
            gPad.SetLeftMargin(0.2)
            hist.GetXaxis().SetTitle(xtitle)
            hist.GetYaxis().SetTitle(ytitle)
            hist.GetXaxis().SetTitleOffset(1.5)
            hist.GetYaxis().SetTitleOffset(2.3)
            hist.GetZaxis().SetTitleOffset(1.8)
            if len(titles) > 0:
                hist.SetTitle(titles[hist_index])

            hist.Draw('lego')
            if len(bkglist) > 0:
                print('ERROR: It seems you are trying to plot backgrounds with data on a 2D plot. This is not supported since there is no good way to view this type of distribution.')
        
        # Otherwise it's a TH1 hopefully
        else:
            alpha = 1
            if dataOff:
                alpha = 0
            hist.SetLineColorAlpha(kBlack,alpha)
            if 'pe' in datastyle.lower():
                hist.SetMarkerColorAlpha(kBlack,alpha)
                hist.SetMarkerStyle(8)
            if 'hist' in datastyle.lower():
                hist.SetFillColorAlpha(0,0)
            
            # If there are no backgrounds, only plot the data (semilog if desired)
            if len(bkglist) == 0:
                hist.GetXaxis().SetTitle(xtitle)
                hist.GetYaxis().SetTitle(ytitle)
                if len(titles) > 0:
                    hist.SetTitle(titles[hist_index])
                hist.Draw(datastyle)
            
            # Otherwise...
            else:
                # Create some subpads, a legend, a stack, and a total bkg hist that we'll use for the error bars
                if not dataOff:
                    mains.append(TPad(hist.GetName()+'_main',hist.GetName()+'_main',0, 0.3, 1, 1))
                    subs.append(TPad(hist.GetName()+'_sub',hist.GetName()+'_sub',0, 0, 1, 0.3))

                else:
                    mains.append(TPad(hist.GetName()+'_main',hist.GetName()+'_main',0, 0.1, 1, 1))
                    subs.append(TPad(hist.GetName()+'_sub',hist.GetName()+'_sub',0, 0, 0, 0))

                legends.append(TLegend(0.65,0.6,0.95,0.93))
                stacks.append(THStack(hist.GetName()+'_stack',hist.GetName()+'_stack'))
                tot_hist = hist.Clone(hist.GetName()+'_tot')
                tot_hist.Reset()
                tot_hist.SetTitle(hist.GetName()+'_tot')
                tot_hist.SetMarkerStyle(0)
                tot_hists.append(tot_hist)


                # Set margins and make these two pads primitives of the division, thisPad
                mains[hist_index].SetBottomMargin(0.0)
                mains[hist_index].SetLeftMargin(0.16)
                mains[hist_index].SetRightMargin(0.05)
                mains[hist_index].SetTopMargin(0.1)

                subs[hist_index].SetLeftMargin(0.16)
                subs[hist_index].SetRightMargin(0.05)
                subs[hist_index].SetTopMargin(0)
                subs[hist_index].SetBottomMargin(0.3)
                mains[hist_index].Draw()
                subs[hist_index].Draw()

                # Build the stack
                for bkg_index,bkg in enumerate(bkglist[hist_index]):     # Won't loop if bkglist is empty
                    # bkg.Sumw2()
                    tot_hists[hist_index].Add(bkg)
                    bkg.SetLineColor(kBlack)
                    if logy:
                        bkg.SetMinimum(1e-3)

                    if bkg.GetName().find('qcd') != -1:
                        bkg.SetFillColor(kYellow)

                    else:
                        if colors[bkg_index] != None:
                            bkg.SetFillColor(colors[bkg_index])
                        else:
                            bkg.SetFillColor(default_colors[bkg_index])

                    stacks[hist_index].Add(bkg)

                    legends[hist_index].AddEntry(bkg,bkg.GetName().split('_')[0],'f')
                    
                # Go to main pad, set logy if needed
                mains[hist_index].cd()

                # Set y max of all hists to be the same to accomodate the tallest
                histList = [stacks[hist_index],tot_hists[hist_index],hist]

                yMax = histList[0].GetMaximum()
                maxHist = histList[0]
                for h in range(1,len(histList)):
                    if histList[h].GetMaximum() > yMax:
                        yMax = histList[h].GetMaximum()
                        maxHist = histList[h]
                for h in histList:
                    h.SetMaximum(yMax*1.1)
                    if logy == True:
                        h.SetMaximum(yMax*10)

                
                mLS = 0.06
                # Now draw the main pad
                data_leg_title = hist.GetTitle()
                if len(titles) > 0:
                    hist.SetTitle(titles[hist_index])
                hist.SetTitleOffset(1.5,"xy")
                hist.GetYaxis().SetTitle('Events')
                hist.GetYaxis().SetLabelSize(mLS)
                hist.GetYaxis().SetTitleSize(mLS)
                if logy == True:
                    hist.SetMinimum(1e-3)
                hist.Draw(datastyle)

                stacks[hist_index].Draw('same hist')

                # Do the signals
                if len(signals) > 0: 
                    signals[hist_index].SetLineColor(kBlue)
                    signals[hist_index].SetLineWidth(2)
                    if logy == True:
                        signals[hist_index].SetMinimum(1e-3)
                    legends[hist_index].AddEntry(signals[hist_index],signals[hist_index].GetName().split('_')[0],'L')
                    signals[hist_index].Draw('hist same')

                tot_hists[hist_index].SetFillColor(kBlack)
                tot_hists[hist_index].SetFillStyle(3354)

                tot_hists[hist_index].Draw('e2 same')
                # legends[hist_index].Draw()

                if not dataOff:
                    legends[hist_index].AddEntry(hist,'data',datastyle)
                    hist.Draw(datastyle+' same')

                gPad.RedrawAxis()

                # Draw the pull
                subs[hist_index].cd()
                # Build the pull
                pulls.append(Make_Pull_plot(hist,tot_hists[hist_index]))
                pulls[hist_index].SetFillColor(kBlue)
                pulls[hist_index].SetTitle(";"+hist.GetXaxis().GetTitle()+";(Data-Bkg)/#sigma")
                pulls[hist_index].SetStats(0)

                LS = .13

                pulls[hist_index].GetYaxis().SetRangeUser(-2.9,2.9)
                pulls[hist_index].GetYaxis().SetTitleOffset(0.4)
                pulls[hist_index].GetXaxis().SetTitleOffset(0.9)
                             
                pulls[hist_index].GetYaxis().SetLabelSize(LS)
                pulls[hist_index].GetYaxis().SetTitleSize(LS)
                pulls[hist_index].GetYaxis().SetNdivisions(306)
                pulls[hist_index].GetXaxis().SetLabelSize(LS)
                pulls[hist_index].GetXaxis().SetTitleSize(LS)

                pulls[hist_index].GetXaxis().SetTitle(xtitle)
                pulls[hist_index].GetYaxis().SetTitle("(Data-Bkg)/#sigma")
                pulls[hist_index].Draw('hist')

                if logy == True:
                    mains[hist_index].SetLogy()

                CMS_lumi.CMS_lumi(thisPad, 4, 11)

    if rootfile:
        myCan.Print(tag+'plots/'+name+'.root','root')
    else:
        myCan.Print(tag+'plots/'+name+'.png','png')

def findCommonString(string_list):
    to_match = ''   # initialize the string we're looking for/building
    for s in string_list[0]:    # for each character in the first string
        passed = True
        for istring in range(1,len(string_list)):   # compare to_match+s against strings in string_list
            string = string_list[istring]
            if to_match not in string:                  # if in the string, add more
                passed = False
            
        if passed == True:
            to_match+=s

    if to_match[-2] == '_':
        return to_match[:-2] 
    else:
        return to_match[:-1]                # if not, return to_match minus final character

    return to_match[:-2]
        
def makePullPlot( DATA,BKG):
    BKGUP, BKGDOWN = Make_up_down(BKG)
    pull = DATA.Clone(DATA.GetName()+"_pull")
    pull.Add(BKG,-1)
    sigma = 0.0
    FScont = 0.0
    BKGcont = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        FScont = DATA.GetBinContent(ibin)
        BKGcont = BKG.GetBinContent(ibin)
        if FScont>=BKGcont:
            FSerr = DATA.GetBinErrorLow(ibin)
            BKGerr = abs(BKGUP.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FScont<BKGcont:
            FSerr = DATA.GetBinErrorUp(ibin)
            BKGerr = abs(BKGDOWN.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FSerr != None:
            sigma = sqrt(FSerr*FSerr + BKGerr*BKGerr)
        else:
            sigma = sqrt(BKGerr*BKGerr)
        if FScont == 0.0:
            pull.SetBinContent(ibin, 0.0 )  
        else:
            if sigma != 0 :
                pullcont = (pull.GetBinContent(ibin))/sigma
                pull.SetBinContent(ibin, pullcont)
            else :
                pull.SetBinContent(ibin, 0.0 )
    return pull

def makeUpDown(hist):
    hist_up = hist.Clone(hist.GetName()+'_up')
    hist_down = hist.Clone(hist.GetName()+'_down')

    for xbin in range(1,hist.GetNbinsX()+1):
        errup = hist.GetBinErrorUp(xbin)
        errdown = hist.GetBinErrorLow(xbin)
        nom = hist.GetBinContent(xbin)

        hist_up.SetBinContent(xbin,nom+errup)
        hist_down.SetBinContent(xbin,nom-errdown)

    return hist_up,hist_down

# Taken from Kevin's limit_plot_shape.py
def makeSmoothGraph(h2,h3):
    h2 = TGraph(h2)
    h3 = TGraph(h3)
    npoints = h3.GetN()
    h3.Set(2*npoints+2)
    for b in range(npoints+2):
        x1, y1 = (ROOT.Double(), ROOT.Double())
        if b == 0:
            h3.GetPoint(npoints-1, x1, y1)
        elif b == 1:
            h2.GetPoint(npoints-b, x1, y1)
        else:
            h2.GetPoint(npoints-b+1, x1, y1)
        h3.SetPoint(npoints+b, x1, y1)
    return h3

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)