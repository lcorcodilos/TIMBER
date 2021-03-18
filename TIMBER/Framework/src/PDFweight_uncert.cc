#include "../include/PDFweight_uncert.h"

PDFweight_uncert::PDFweight_uncert(int lhaID, bool ignoreEmptyBranch){
    ignoreEmpty = ignoreEmptyBranch;
    lhaid = lhaID;
    // auto determine whether these are replicas or hessian eigenvectors
    // Search pdfsets.index, find matching lhaid, check if "hessian" is in the pdf set name
    std::fstream lhaid_file;
    lhaid_file.open(std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/pdfsets.index",std::fstream::in);
    std::string line;
    std::vector<std::string> line_parts;
    while (getline(lhaid_file, line)) {
        line_parts = Pythonic::Split(line,' ');
        if (lhaid == (int)std::stoi(line_parts[0])) {
            std::cout << "Found matching PDF set: " << line_parts[1] << " (" << lhaid << ")" << std::endl;
            if (Pythonic::InString("hessian",line_parts[1])) {
                hessian = true;
            } else { hessian = false; }
        };
    }
};

PDFweight_uncert::~PDFweight_uncert(){};

std::vector<float> PDFweight_uncert::eval(RVec<float> LHEPdfWeight) {
    // [up,down]
    std::vector<float> v;
    float stddev;
    float sumsquares = 0.0;
    int size = LHEPdfWeight.size();
    // check weights aren't empty (known bug that they all could)
    if (size == 0 && !ignoreEmpty) {
        throw "LHEPdfWeight vector empty. May be known bug in NanoAOD - see https://github.com/cms-nanoAOD/cmssw/issues/520. To ignore, set ignoreEmpty argument to true.";
    }
    
    if (hessian) { // Computes sqrt of sum of differences squared
        float base_eigenv = LHEPdfWeight[0];
        for (int ipdf = 1; ipdf < size; ipdf++) {
            sumsquares = sumsquares + std::pow(LHEPdfWeight[ipdf] - base_eigenv,2);
        }
        stddev = sqrt(sumsquares);
        
    } else { // Computes the std dev of the pdf MC replicas
        float pdfavg = std::accumulate(LHEPdfWeight.begin(), LHEPdfWeight.end(), 0.0) / size;
        for (int ipdf = 0; ipdf < size; ipdf++) {
            sumsquares = sumsquares + std::pow(LHEPdfWeight[ipdf] - pdfavg,2);
        }
        stddev = sqrt(sumsquares/(size-1));
    }

    v = {
        std::min((float)13.0,(float)1.0+stddev),
        std::max((float)-13.0,(float)1.0-stddev)
    };

    return v;
}
