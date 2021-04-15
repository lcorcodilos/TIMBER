from TIMBER.Analyzer import analyzer
a = analyzer('locations/Zprime1500_18.txt') # open file
a.Cut('myNFatJetCut', 'nFatJet>0') # Make a cut
a.Define('pt0','FatJet_pt[0]') # Define a variable
h = a.DataFrame.Histo1D('pt0') # Draw the variable (note we cannot draw 'FatJet_pt[0]')
h.Draw('histe') # Actions won't execute until here since it's the first time we're "measuring"
raw_input('') # Hold for input so we can wait for system to draw