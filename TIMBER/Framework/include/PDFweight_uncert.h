#ifndef _TIMBER_PDFWEIGHT_UNCERT
#define _TIMBER_PDFWEIGHT_UNCERT
#include <cmath>
#include <vector>
#include <numeric>
#include <fstream>
#include "ROOT/RVec.hxx"
#include "common.h"

using namespace ROOT::VecOps;

/**
 * @class PDFweight_uncert
 * @brief C++ class. PDF weight uncertainty lookup class.
 * 
 * Accounts for hessians vs replicas by using LHA ID.
 */
class PDFweight_uncert {
    private:
        bool hessian;
        bool ignoreEmpty;
        int lhaid;
    public:
        /**
         * @brief Construct a new PDF weight uncertainty lookup object
         * 
         * @param lhaID LHA ID for the PDF set used to determine whether
         *  set is Hessian eigenvectors or MC replicas.
         * @param ignoreEmptyBranch Ignores error that LHEPdfWeight branch is empty.
         *  Defaults to false.
         */
        PDFweight_uncert(int lhaID, bool ignoreEmptyBranch = false);
        ~PDFweight_uncert();
        /**
         * @brief Per-event evaluation function.
         * 
         * @param LHEPdfWeight The LHEPdfWeight branch/column.
         * @return std::vector<float> {up, down} uncertainties in PDF weight.
         */
        std::vector<float> eval(RVec<float> LHEPdfWeight);
};
#endif