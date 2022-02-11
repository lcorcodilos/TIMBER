#include "../include/Pileup_weight.h"

Pileup_weight::Pileup_weight(std::string filename_mc, std::vector<std::string> filenames_data,
                      std::string histname_mc, std::string histname_data) {
    init(filename_mc, filenames_data, histname_mc, histname_data);
}

Pileup_weight::Pileup_weight(std::vector<std::string> filenames_data) {
    init("auto", filenames_data, "", "pileup");
}

void Pileup_weight::init(std::string filename_mc, std::vector<std::string> filenames_data,
                         std::string histname_mc, std::string histname_data) {
    _dataHist = hardware::LoadHist("TIMBER/data/Pileup/"+filenames_data[0],histname_data);
    _dataHistUp = hardware::LoadHist("TIMBER/data/Pileup/"+filenames_data[1],histname_data);
    _dataHistDown = hardware::LoadHist("TIMBER/data/Pileup/"+filenames_data[2],histname_data);

    if (filename_mc != "auto") {
        _autoPU = false;
        _mcHist = hardware::LoadHist(filename_mc,histname_mc,false);
    } else {
        _autoPU = true;
        gROOT->cd();
        _mcHist = (TH1*)gDirectory->Get("autoPU")->Clone();
        _mcHist->SetDirectory(0);
        if (!_mcHist) {
            std::cout << "Histogram `autoPU` does not exist in memory. Make sure to run AutoPU in python to generate it." << std::endl;
            throw "ERROR";
        }
    }

    _worker = WeightCalculatorFromHistogram(_mcHist, _dataHist, true, true, false);
    _worker_plus = WeightCalculatorFromHistogram(_mcHist, _dataHistUp, true, true, false);
    _worker_minus = WeightCalculatorFromHistogram(_mcHist, _dataHistDown, true, true, false);
}

std::vector<float> Pileup_weight::eval(int Pileup_nTrueInt) {
    std::vector<float> out(3);
    if (Pileup_nTrueInt < _mcHist->GetNbinsX()) {
        out[0] = _worker.getWeight(Pileup_nTrueInt);
        out[1] = _worker_plus.getWeight(Pileup_nTrueInt);
        out[2] = _worker_minus.getWeight(Pileup_nTrueInt);
    } else {
        out = {1., 1., 1.};
    }
    return out;
}   