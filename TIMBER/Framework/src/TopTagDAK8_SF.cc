#include "../include/TopTagDAK8_SF.h"

TopTagDAK8_SF::TopTagDAK8_SF(int year, std::string workingpoint, bool massDecorr) :
    helper("Top",year, workingpoint, massDecorr) {};

std::vector<float> TopTagDAK8_SF::eval(float pt) {
    return helper.eval(pt);
}
