#ifndef _TIMBER_HISTLOADER
#define _TIMBER_HISTLOADER
#include <string>
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"

/**
 * @class HistLoader
 * @brief C++ class. Generic histogram loader with methods to return bin values.
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
#endif