#include <ROOT/RVec.hxx>
/**
 * @class BranchCorrection
 * @brief Trivial class to load a branch as correction in TIMBER
 */
using namespace ROOT::VecOps;
class BranchCorrection {

    public:
        BranchCorrection(){};
        ~BranchCorrection(){};
        RVec<float> eval(float val);
            
};


RVec<float> BranchCorrection::eval(float val){
    RVec<float> correction(1);
    correction[0]=val;
    return correction;
};

