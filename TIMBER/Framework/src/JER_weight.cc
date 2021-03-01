#include "../include/JER_weight.h"

JER_weight::JER_weight(std::string jetType, std::string jerTag) :
    _smearer(JetSmearer(jetType, jerTag)) {};

