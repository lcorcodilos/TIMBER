#include <string>
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"

class HistLoader {
    private:
        TFile *file;
        TH1 *hist;
        int dim;
        void checkDim(int x, int y, int z);
    public:
        HistLoader(std::string filename, std::string histname);
        std::vector<float> eval_bybin(int binx, int biny = 0, int binz = 0);
        std::vector<float> eval(float xval, float yval = 0., float zval = 0.);
            
};

HistLoader::HistLoader(std::string filename, std::string histname) {
    file = TFile::Open(filename.c_str());
    hist = (TH1*)file->Get(histname.c_str());
    if (dynamic_cast<TH2*>(hist) != nullptr) {
        dim = 2;
    } else if (dynamic_cast<TH3*>(hist) != nullptr) {
        dim = 3;
    } else {
        dim = 1;
    }
}

void HistLoader::checkDim(int x, int y, int z){
    if (dim == 1) {
        if ((y != 0) || (z != 0)) {
            throw "Dimension of hist is 1 but Y and Z components were provided";
        }
    }
    if (dim == 2) {
        if (z != 0) {
            throw "Dimension of hist is 2 but Z component was provided";
        }
    } 
}

std::vector<float> HistLoader::eval_bybin(int binx, int biny = 0, int binz = 0){
    HistLoader::checkDim(binx,biny,binz);
    std::vector<float> out = {};
    float binval;
    float binup;
    float bindown;
    if (dim == 1){
        out.push_back(hist->GetBinContent(binx));
        out.push_back(hist->GetBinContent(binx) + hist->GetBinErrorUp(binx));
        out.push_back(hist->GetBinContent(binx) - hist->GetBinErrorLow(binx));
    } else if (dim == 2) {
        out.push_back(hist->GetBinContent(binx,biny));
        out.push_back(hist->GetBinContent(binx,biny) + hist->GetBinErrorUp(hist->GetBin(binx,biny)));
        out.push_back(hist->GetBinContent(binx,biny) - hist->GetBinErrorLow(hist->GetBin(binx,biny)));
    } else if (dim == 3) {
        out.push_back(hist->GetBinContent(binx,biny,binz));
        out.push_back(hist->GetBinContent(binx,biny,binz) + hist->GetBinErrorUp(hist->GetBin(binx,biny,binz)));
        out.push_back(hist->GetBinContent(binx,biny,binz) - hist->GetBinErrorLow(hist->GetBin(binx,biny,binz)));
    } else {
        throw "Dimensionality not supported.";
    }

    return out;
}

std::vector<float> HistLoader::eval(float xval, float yval = 0., float zval = 0.){
    HistLoader::checkDim(xval,yval,zval);
    int binx = 0;
    int biny = 0;
    int binz = 0;
    if (dim >= 1) {binx = hist->GetXaxis()->FindBin(xval);}
    if (dim >= 2) {biny = hist->GetYaxis()->FindBin(yval);}
    if (dim == 3) {binz = hist->GetZaxis()->FindBin(zval);}

    return HistLoader::eval_bybin(binx,biny,binz);
}

