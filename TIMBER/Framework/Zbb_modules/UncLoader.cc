#include <string>
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"

/**
 * @class UncLoader
 * @brief Load two histograms (up, down) and return their values. Hist up and down need to be of same shape
 */
class UncLoader {
    private:
        TFile *file;
        int dim;

        /**
         * @brief Sanity check that the dimensionality of the
         * arguements and the histogram make sense
         * 
         * @param x 
         * @param y 
         * @param z 
         */
        void checkDim(int x, int y, int z);
    public:
        TH1 *histUp; //!< Histogram object
        TH1 *histDown; //!< Histogram object
        /**
         * @brief Empty constructor
         */
        UncLoader(){};
        /**
         * @brief Construct a new UncLoader object
         * 
         * @param filename File to access.
         * @param histname Histogram names in the file.
         */
        UncLoader(std::string filename, std::string histUpName, std::string histDownName);
        /**
         * @brief Evaluate by bin numbers.
         * 
         * @param binx 
         * @param biny 
         * @param binz 
         * @return std::vector<float> {up unc, down unc}
         */
        std::vector<float> eval_bybin(int binx, int biny = 0, int binz = 0);
        /**
         * @brief Evaluate by axis value.
         * 
         * @param xval 
         * @param yval 
         * @param zval 
         * @return std::vector<float> {up unc, down unc}
         */
        std::vector<float> eval(float xval, float yval = 0., float zval = 0.);
            
};

UncLoader::UncLoader(std::string filename, std::string histUpName, std::string histDownName) {
    file = TFile::Open(filename.c_str());
    histUp = (TH1*)file->Get(histUpName.c_str());
    histDown = (TH1*)file->Get(histDownName.c_str());
    if (dynamic_cast<TH2*>(histUp) != nullptr) {
        dim = 2;
    } else if (dynamic_cast<TH3*>(histUp) != nullptr) {
        dim = 3;
    } else {
        dim = 1;
    }
}

void UncLoader::checkDim(int x, int y, int z){
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

std::vector<float> UncLoader::eval_bybin(int binx, int biny, int binz){
    UncLoader::checkDim(binx,biny,binz);
    float valUp;
    float valDown;
    if (dim == 1){
        valUp = histUp->GetBinContent(binx);
        valDown = histDown->GetBinContent(binx);
    } else if (dim == 2) {
        valUp = histUp->GetBinContent(binx,biny);
        valDown = histDown->GetBinContent(binx,biny);
    } else if (dim == 3) {
        valUp = histUp->GetBinContent(binx,biny,binz);
        valDown = histDown->GetBinContent(binx,biny,binz);
    } else {
        throw "Dimensionality not supported.";
    }

    return {valUp,valDown};
}

std::vector<float> UncLoader::eval(float xval, float yval, float zval){
    UncLoader::checkDim(xval,yval,zval);
    int binx = 0;
    int biny = 0;
    int binz = 0;
    if (dim >= 1) {binx = histUp->GetXaxis()->FindBin(xval);}
    if (dim >= 2) {biny = histUp->GetYaxis()->FindBin(yval);}
    if (dim == 3) {binz = histUp->GetZaxis()->FindBin(zval);}

    return UncLoader::eval_bybin(binx,biny,binz);
}

