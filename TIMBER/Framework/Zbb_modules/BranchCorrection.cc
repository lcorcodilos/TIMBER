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
        RVec<float> evalCorrection(float val);
        RVec<float> evalWeight(float val,float valUp,float valDown);
        RVec<float> evalUncert(float valUp,float valDown);
            
};


RVec<float> BranchCorrection::evalCorrection(float val){
    RVec<float> correction(1);
    correction[0]=val;
    return correction;
};

RVec<float> BranchCorrection::evalWeight(float val,float valUp,float valDown){
    RVec<float> weight(3);
    weight[0]=val;
    weight[1]=valUp;
    weight[2]=valDown;
    return weight;
};

RVec<float> BranchCorrection::evalUncert(float valUp,float valDown){
    RVec<float> uncert(2);
    uncert[0]=valUp;
    uncert[1]=valDown;
    return uncert;
};

