import ROOT

f = ROOT.TFile('tester.root','RECREATE')
h1 = ROOT.TH1I('test1','',10,0,10)
h2 = ROOT.TH2D('test2','',10,0,10,10,0,10)
h3 = ROOT.TH3F('test3','',10,0,10,10,0,10,10,0,10)

for i in range(1,11):
    h1.SetBinContent(i,i)
    for j in range(1,11):
        h2.SetBinContent(i,j,i+j)
        for k in range(1,11):
            h3.SetBinContent(i,j,k,i+j+k)

f.cd()
h1.Write()
h2.Write()
h3.Write()
f.Close()