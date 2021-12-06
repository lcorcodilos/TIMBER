#ifndef _TIMBER_PILEUP_WEIGHT
#define _TIMBER_PILEUP_WEIGHT
#include <iostream>
#include <TFile.h>
#include <TH1.h>
#include <TROOT.h>
#include <TTree.h>
#include "common.h"
#include "../ext/WeightCalculatorFromHistogram.h"

/**
 * @brief C++ class to handle pileup reweighting. Used in AutoPU.py.
 */
class Pileup_weight {
    private:
        TFile *_dataFile, *_mcFile;
        TH1 *_dataHist, *_dataHistUp, *_dataHistDown,
            *_mcHist, *_mcHistUp, *_mcHistDown;
        WeightCalculatorFromHistogram _worker, _worker_plus, _worker_minus;
        bool _autoPU;

        void init(std::string filename_mc, std::vector<std::string> filenames_data,
                std::string histname_mc, std::string histname_data);

    public:
        /**
         * @brief Construct a new Pileup_weight object, providing custom MC histograms 
         * to take the ratio of the true number of primary vertices.
         * 
         * @param filename_mc Use "auto" to get the number of primary vertices directly from "autoPU" histogram in memory (gDirectory).
         * @param filenames_data Vector of file names holding pileup distributions, ordered as nominal, up, down variations.
         * @param histname_mc Defaults to "autoPU".
         * @param histname_data Defaults to "pileup".
         */
        Pileup_weight(std::string filename_mc, std::vector<std::string> filenames_data,
                      std::string histname_mc="autoPU", std::string histname_data="pileup");
        /**
         * @brief Construct a new Pileup_weight object. Assumes "auto" pileup calculation
         * for MC distribution. Calculates the ratio of the true number of primary vertices
         * between data and simulation.
         * 
         * @param filenames_data Vector of file names holding pileup distributions, ordered as nominal, up, down variations
         */
        Pileup_weight(std::vector<std::string> filenames_data);
        /**
         * @brief Evaluate the pileup weight (value of ratio of data to simulation).
         * 
         * @param Pileup_nTrueInt 
         * @return std::vector<float> 
         */
        std::vector<float> eval(int Pileup_nTrueInt);
        ~Pileup_weight(){};
};
#endif