#include <cmath>
#include <vector>
#include <numeric>
#include "ROOT/RVec.hxx"
using namespace ROOT::VecOps;

class PDFweight_uncert
{
public:
    PDFweight_uncert();
    ~PDFweight_uncert();
    std::vector<float> PDFweight_uncert::eval(RVec<float> pdfweights, bool hessian = false, bool ignoreEmpty = false);
};

PDFweight_uncert::PDFweight_uncert(){};

PDFweight_uncert::~PDFweight_uncert(){};

std::vector<float> PDFweight_uncert::eval(RVec<float> pdfweights, bool hessian = false, bool ignoreEmpty = false) {
    // [up,down]
    std::vector<float> v;
    float stddev;
    float sumsquares = 0.0;
    int size = pdfweights.size();
    // check weights aren't empty (known bug that they all could)
    if (size == 0 && !ignoreEmpty) {
        throw "LHEPdfWeight vector empty. May be known bug in NanoAOD - see https://github.com/cms-nanoAOD/cmssw/issues/520. To ignore, set ignoreEmpty argument to true.";
    }
    
    if (hessian) { // Computes sqrt of sum of differences squared
        float base_eigenv = pdfweights[0];
        for (int ipdf = 1; ipdf < size; ipdf++) {
            sumsquares = sumsquares + std::pow(pdfweights[ipdf] - base_eigenv,2);
        }
        stddev = sqrt(sumsquares);
        
    } else { // Computes the std dev of the pdf MC replicas
        float pdfavg = std::accumulate(pdfweights.begin(), pdfweights.end(), 0.0) / size;
        for (int ipdf = 0; ipdf < size; ipdf++) {
            sumsquares = sumsquares + std::pow(pdfweights[ipdf] - pdfavg,2);
        }
        stddev = sqrt(sumsquares/(size-1));
    }

    v = {
        std::min((float)13.0,(float)1.0+stddev),
        std::max((float)-13.0,(float)1.0-stddev)
    };

    return v;
}
