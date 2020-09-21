// NOT USABLE CURRENTLY WITHOUT PROPPER FILES
using namespace ROOT::VecOps;

namespace analyzer {
    puWeightNom
    TFile *puWeightNom = new TFile("JHUanalyzer/data/pileup/...","READ");
    TFile *puWeightUp = new TFile("JHUanalyzer/data/pileup/...up","READ");
    TFile *puWeightDown = new TFile("JHUanalyzer/data/pileup/...down","READ");

    std::vector<double> PUWeightLookup(int nvtx) {
        std::vector<double> weight;
        double weightNom = 1;
        double weightUp = 1;
        double weightDown = 1;

        weightNom *= puWeightNom->GetBinContent(puWeightNom->FindBin(nvtx));
        weightUp *= puWeightUp->GetBinContent(puWeightUp->FindBin(nvtx));
        weightDown *= puWeightDown->GetBinContent(puWeightDown->FindBin(nvtx));

        weight.push_back(weightNom);
        weight.push_back(weightUp);
        weight.push_back(weightDown);
        return weight;
    }

    std::vector<double> PUWeightCalc(...) {
        ...
    }
}