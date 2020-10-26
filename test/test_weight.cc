#include <vector>
#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;

class testWeight
{
private:
    std::vector<float> boundaries, weights, up_err, down_err;
public:
    testWeight();
    RVec<float> eval(float pt);
};

testWeight::testWeight() {
    boundaries = {0.,100.,120.,150.,200.,10000.};
    weights = {0.95, 0.98, 1.05, 1.01, 1.10, 1};
    up_err = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02};
    down_err = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02};
}

RVec<float> testWeight::eval(float pt) {
    RVec<float> out;
    for (size_t i = 0; i < weights.size(); i++) {
        if ((pt > boundaries[i]) && (pt < boundaries[i+1])) {
            out.push_back(weights[i]);
            out.push_back(weights[i]+up_err[i]);
            out.push_back(weights[i]-down_err[i]);
            return out;
        }
    }
    out = {1.,1.,1.};
    return out;
}

