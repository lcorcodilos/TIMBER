#include <string>
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"

/**
 * @class HistLoader
 * @brief Generic histogram loader with methods to return bin values.
 */
class HistLoader {
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
        TH1 *hist; //!< Histogram object
        /**
         * @brief Empty constructor
         */
        HistLoader(){};
        /**
         * @brief Construct a new HistLoader object
         * 
         * @param filename File to access.
         * @param histname Histogram name in the file.
         */
        HistLoader(std::string filename, std::string histname);
        /**
         * @brief Evaluate by bin numbers.
         * 
         * @param binx 
         * @param biny 
         * @param binz 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval_bybin(int binx, int biny = 0, int binz = 0);
        /**
         * @brief Evaluate by axis value.
         * 
         * @param xval 
         * @param yval 
         * @param zval 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
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

std::vector<float> HistLoader::eval_bybin(int binx, int biny, int binz){
    HistLoader::checkDim(binx,biny,binz);
    float binval;
    float binup;
    float bindown;
    if (dim == 1){
        binval = hist->GetBinContent(binx);
        binup = hist->GetBinContent(binx) + hist->GetBinErrorUp(binx);
        bindown = hist->GetBinContent(binx) - hist->GetBinErrorLow(binx);
    } else if (dim == 2) {
        binval = hist->GetBinContent(binx,biny);
        binup = hist->GetBinContent(binx,biny) + hist->GetBinErrorUp(hist->GetBin(binx,biny));
        bindown = hist->GetBinContent(binx,biny) - hist->GetBinErrorLow(hist->GetBin(binx,biny));
    } else if (dim == 3) {
        binval = hist->GetBinContent(binx,biny,binz);
        binup = hist->GetBinContent(binx,biny,binz) + hist->GetBinErrorUp(hist->GetBin(binx,biny,binz));
        bindown = hist->GetBinContent(binx,biny,binz) - hist->GetBinErrorLow(hist->GetBin(binx,biny,binz));
    } else {
        throw "Dimensionality not supported.";
    }

    return {binval,binup,bindown};
}

std::vector<float> HistLoader::eval(float xval, float yval, float zval){
    HistLoader::checkDim(xval,yval,zval);
    int binx = 0;
    int biny = 0;
    int binz = 0;
    if (dim >= 1) {binx = hist->GetXaxis()->FindBin(xval);}
    if (dim >= 2) {biny = hist->GetYaxis()->FindBin(yval);}
    if (dim == 3) {binz = hist->GetZaxis()->FindBin(zval);}

    return HistLoader::eval_bybin(binx,biny,binz);
}

