#include "../include/JER_weight.h"

JER_weight::JER_weight(std::string jerTag, std::string jetType) :
    _smearer(jerTag, jetType) {};

