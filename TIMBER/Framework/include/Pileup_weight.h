#ifndef _TIMBER_PILEUP_WEIGHT
#define _TIMBER_PILEUP_WEIGHT
#include <iostream>
#include <TFile.h>
#include <TH1.h>
#include <TROOT.h>
#include <TTree.h>
#include "common.h"
#include "../ext/WeightCalculatorFromHistogram.h"

class Pileup_weight {
    private:
        TFile *_dataFile, *_mcFile;
        TH1 *_dataHist, *_dataHistUp, *_dataHistDown,
            *_mcHist, *_mcHistUp, *_mcHistDown;
        WeightCalculatorFromHistogram _worker, _worker_plus, _worker_minus;
        bool _autoPU;

        void init(std::string filename_mc, std::string filename_data,
                std::string histname_mc, std::string histname_data);

    public:
        /**
         * @brief Construct a new Pileup_weight object, providing custom MC and 
         * data histograms.
         * 
         * @param filename_mc Use "auto" to get the number of primary vertices directly from "autoPU" histogram in memory (gDirectory)
         * @param filename_data 
         * @param histname_mc 
         * @param histname_data 
         */
        Pileup_weight(std::string filename_mc, std::string filename_data,
                      std::string histname_mc, std::string histname_data);
        /**
         * @brief Construct a new Pileup_weight object. Assumes "auto" pileup calculation
         * for MC distribution.
         * 
         * @param era 2016(UL), 2017(UL), 2018(UL)
         */
        Pileup_weight(std::string era);
        /**
         * @brief Save the Pileup_nTrueInt MC distribution if using "auto" mode.
         * 
         * @param outfile Name of the output file (opened in UPDATE mode).
         */
        std::vector<float> eval(int Pileup_nTrueInt);
        ~Pileup_weight(){};
};
#endif