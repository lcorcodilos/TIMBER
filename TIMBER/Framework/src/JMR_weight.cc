#include "../include/JMR_weight.h"

JMR_weight::JMR_weight(int year):
    _smearer (_getJMRvals(year)) {};

std::vector<float> JMR_weight::_getJMRvals(int year) {
    std::vector<float> out;
    if (year == 2016) {
        out = {1.00, 1.2,  0.8 };
    } else if (year == 2017) {
        out = {1.09, 1.14, 1.04};
    } else if (year == 2018) {
        out = {1.09, 1.14, 1.04};
    } else {
        throw "JMR_weight: Provided year not supported.";
    }
    return out;
}