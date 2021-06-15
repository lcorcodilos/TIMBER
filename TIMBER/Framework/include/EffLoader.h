#ifndef _TIMBER_EFFLOADER
#define _TIMBER_EFFLOADER
#include <string>
#include "TFile.h"
#include "TEfficiency.h"

/**
 * @class EffLoader
 * @brief C++ class. Generic histogram loader with methods to return bin values.
 */
class EffLoader {
    private:
        TFile *file;
        TEfficiency *efficiency; //!< Histogram object
        int binx;
        int globalbin;
        float effval;
        float effup;
        float effdown;

    public:
        /**
         * @brief Empty constructor
         */
        EffLoader();
        /**
         * @brief Construct a new EffLoader object
         * 
         * @param filename File to access.
         * @param histname Histogram name in the file.
         */
        EffLoader(std::string filename, std::string histname);
        /**
         * @brief Evaluate by global bin number.
         * 
         * @param globalbin 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval_byglobal(int globalbin);
        /**
         * @brief Evaluate by per-axis bin numbers.
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
        std::vector<float> eval(float xval, float yval = 0, float zval = 0);
};
#endif