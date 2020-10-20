'''@addtogroup Plot Plotting Tools
 Functions to easily plot histograms together in various configurations.
 @{
'''
from TIMBER.Tools.CMS import CMS_lumi
import ROOT, collections
from collections import OrderedDict
from TIMBER.Analyzer import HistGroup

def CompareShapes(outfilename,year,prettyvarname,bkgs={},signals={},names={},colors={},scale=True,stackBkg=False):
    '''Create a plot that compares the shapes of backgrounds versus signal.
    If stackBkg, backgrounds will be stacked together and signals will be plot separately.
    Total background and signals are scaled to 1 if scale == True. Inputs organized 
    as dicts so that keys can match across dicts (ex. bkgs and bkgNames).

    @param outfilename (string): Path where plot will be saved.
    @param year (int): Year to determine luminosity value on plot. Options are 16, 17, 18, 1 (for full Run II),
        or 2 (for full Run II but represented as separate years, ie. 2016+2017+2018).
    @param prettyvarname (string): What will be assigned to as the axis title.
    @param bkgs ({string:TH1}, optional): Dictionary of backgrounds to plot. Defaults to {}.
    @param signals ({string:TH1}, optional): Dictionary of signals to plot. Defaults to {}.
    @param names ({string:string}, optional): Formatted version of names for backgrounds and signals to appear in legend. Keys must match those in bkgs and signal. Defaults to {}. 
    @param colors ({string:int}, optional): TColor code for backgrounds and signals to appear in plot. Keys must match those in bkgs and signal. Defaults to {}.
    @param scale (bool, optional): If True, scales total background to unity and signals (separately) to unity. Defaults to True.
    @param stackBkg (bool, optional): If True, backgrounds will be stacked and the total will be normalized to 1 (if scale==True). Defaults to False.
    '''
    # Initialize
    c = ROOT.TCanvas('c','c',800,700)
    legend = ROOT.TLegend(0.6,0.72,0.87,0.88)
    legend.SetBorderSize(0)
    ROOT.gStyle.SetTextFont(42)
    ROOT.gStyle.SetOptStat(0)
    tot_bkg_int = 0
    if stackBkg:
        bkgStack = ROOT.THStack('Totbkg','Total Bkg - '+prettyvarname)
        bkgStack.SetTitle(';%s;%s'%(prettyvarname,'A.U.'))
         # Add bkgs to integral
        for bkey in bkgs.keys():
            tot_bkg_int += bkgs[bkey].Integral()
    else:
        for bkey in bkgs.keys():
            bkgs[bkey].SetTitle(';%s;%s'%(prettyvarname,'A.U.'))

    if colors == None:
        colors = {'signal':ROOT.kBlue,'qcd':ROOT.kYellow,'ttbar':ROOT.kRed,'multijet':ROOT.kYellow}
        
    if scale:
        # Scale bkgs to total integral
        for bkey in bkgs.keys():
            if stackBkg: bkgs[bkey].Scale(1.0/tot_bkg_int)
            else: bkgs[bkey].Scale(1.0/bkgs[bkey].Integral())
        # Scale signals
        for skey in signals.keys():
            signals[skey].Scale(1.0/signals[skey].Integral())

    # Now add bkgs to stack, setup legend, and draw!
    colors_in_legend = []
    procs = OrderedDict() 
    procs.update(bkgs)
    procs.update(signals)
    for pname in procs.keys():
        h = procs[pname]
        # Legend names
        if pname in names.keys(): leg_name = names[pname]
        else: leg_name = pname
        # If bkg, set fill color and add to stack
        if pname in bkgs.keys():
            h.SetFillColorAlpha(colors[pname],0.2 if not stackBkg else 1)
            h.SetLineWidth(0) 
            if stackBkg: bkgStack.Add(h)
            if colors[pname] not in colors_in_legend:
                legend.AddEntry(h,leg_name,'f')
                colors_in_legend.append(colors[pname])
                
        # If signal, set line color
        else:
            h.SetLineColor(colors[pname])
            h.SetLineWidth(2)
            if colors[pname] not in colors_in_legend:
                legend.AddEntry(h,leg_name,'l')
                colors_in_legend.append(colors[pname])

    if stackBkg:
        maximum =  max(bkgStack.GetMaximum(),signals.values()[0].GetMaximum())*1.4
        bkgStack.SetMaximum(maximum)
    else:
        maximum = max(bkgs.values()[0].GetMaximum(),signals.values()[0].GetMaximum())*1.4
        for p in procs.values():
            p.SetMaximum(maximum)
    

    c.cd()
    if len(bkgs.keys()) > 0:
        if stackBkg:
            bkgStack.Draw('hist')
            bkgStack.GetXaxis().SetTitleOffset(1.1)
            bkgStack.Draw('hist')
        else:
            for bkg in bkgs.values():
                bkg.GetXaxis().SetTitleOffset(1.1)
                bkg.Draw('same hist')
    for h in signals.values():
        h.Draw('same hist')
    legend.Draw()

    c.SetBottomMargin(0.12)
    c.SetTopMargin(0.08)
    c.SetRightMargin(0.11)
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Preliminary simulation"
    CMS_lumi.lumi_sqrtS = "13 TeV"
    CMS_lumi.cmsTextSize = 0.6
    CMS_lumi.CMS_lumi(c, year, 11)

    c.Print(outfilename,'png')

def MoneyPlots(name, histlist, bkglist=[],signals=[],colors=[],titles=[],logy=False,xtitle='',ytitle='',dataOff=False,datastyle='pe'):
    '''Tool to produce plots quickly as .root, .pdf, .png, etc.
    If providing TH2s, only plots the data (histlist) with no comparisons.
    If providing TH1s, plots together the data (histlist), total background (individual components as a stack), and signals with pulls in a lower pane.
    Providing multiple data histograms will plot the separate pads on a single canvas. Up to 6 pads are supported.
    See argument descriptions for plotting options.

    @param name (str): Name of output file with extension (file type must be supported by TCanvas.Print()).
    @param histlist ([TH1 or TH2]): List of data histograms.
    @param bkglist ([[TH1]], optional): List of list of background histograms. Index of first list level matches
            against index of histlist. Internal list is the group of backgrounds that will be stacked together
            to create the total background estimate. For example you could have: `histlist = [data1, data2]` and 
            `bkglist = [[bkg1_1,bkg2_1],[bkg1_2,bkg2_2]]`. Defaults to [].
    @param signals ([TH1], optional): List of signal histograms where index corresponds to the index of histlist. Defaults to [].
    @param colors ([int], optional): List of integers corresponding to TColor codes where the index corresponds to the index of histlist. Defaults to [].
    @param titles ([str], optional): List of titles for each histogram where the index corresponds to the index of histlist. Defaults to [] which means the input titles of histlist will be used.
    @param logy (bool, optional): Option to plot log y-axis. Defaults to False.
    @param xtitle (str, optional): X-axis title for all histograms on the canvas. Defaults to '' which means the input titles of histlist will be used.
    @param ytitle (str, optional): Y-axis title for all histograms on the canvas. Defaults to '' which means the input titles of histlist will be used.
    @param dataOff (bool, optional): If True, turns off data from being drawn in all pads. Defaults to False.
    @param datastyle (str, optional): Style in which to draw data. Defaults to 'pe'.

    Raises:
        ValueError: If number of requested pads is greater than 6.
    '''
    # histlist is just the generic list but if bkglist is specified (non-empty)
    # then this function will stack the backgrounds and compare against histlist as if 
    # it is data. The important bit is that bkglist is a list of lists. The first index
    # of bkglist corresponds to the index in histlist (the corresponding data). 
    # For example you could have:
    #   histlist = [data1, data2]
    #   bkglist = [[bkg1_1,bkg2_1],[bkg1_2,bkg2_2]]

    extension = name.split('.')[-1]
    tag = name.split('.')[0]

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

    myCan = TCanvas(tag,tag,width,height)
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
        thisPad = myCan.GetPrimitive(tag+'_'+str(hist_index+1))
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
                pulls.append(MakePullPlot(hist,tot_hists[hist_index]))
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

    myCan.Print(name,extension)

def MakePullPlot( data,bkg):
    '''Generates a pull plot defined as (data-bkg)/sigma where sigma
    is the error of data and bkg added in quadrature.

    @param data (TH1): Histogram of data.
    @param bkg (TH1): Histogram of total background.

    Returns:
        TH1: Histogram of the pull.
    '''
    bkg_up, bkg_down = MakeUpDown(bkg)
    pull = data.Clone(data.GetName()+"_pull")
    pull.Add(bkg,-1)
    for ibin in range(1,pull.GetNbinsX()+1):
        idata = data.GetBinContent(ibin)
        ibkg = bkg.GetBinContent(ibin)

        if idata >= ibkg: # deal with asymmetric bin errors
            idata_err = data.GetBinErrorLow(ibin)
            ibkg_err = abs(bkg_up.GetBinContent(ibin)-bkg.GetBinContent(ibin))
        else:
            idata_err = data.GetBinErrorUp(ibin)
            ibkg_err = abs(bkg_down.GetBinContent(ibin)-bkg.GetBinContent(ibin))

        if idata_err != None: # deal with case when there's no data error (ie. bin content = 0)
            sigma = sqrt(idata_err*idata_err + ibkg_err*ibkg_err)
        else:
            sigma = sqrt(ibkg_err*ibkg_err)

        if sigma != 0 :
            ipull = (pull.GetBinContent(ibin))/sigma
            pull.SetBinContent(ibin, ipull)
        else :
            pull.SetBinContent(ibin, 0.0 )

    return pull

def MakeUpDown(hist):
    '''Creates up and down variations of a histogram
    based on its per-bin errors.

    @param hist (TH1): Histogram from which to create up/down distributions.

    Returns:
        (TH1, TH1): Tuple of (up, down) histograms.
    '''
    hist_up = hist.Clone(hist.GetName()+'_up')
    hist_down = hist.Clone(hist.GetName()+'_down')

    for xbin in range(1,hist.GetNbinsX()+1):
        errup = hist.GetBinErrorUp(xbin)
        errdown = hist.GetBinErrorLow(xbin)
        nom = hist.GetBinContent(xbin)

        hist_up.SetBinContent(xbin,nom+errup)
        hist_down.SetBinContent(xbin,nom-errdown)

    return hist_up,hist_down
## @}