#include "../include/Wtag_SF.h"

Wtag_SF::Wtag_SF(int year){
    if (year > 2000) {
        _year = year - 2000;
    } else {
        _year = year;
    }

    if (year == 16) {
        _HP = 1.00; _HPunc = 0.06;
        _LP = 0.96; _LPunc = 0.11;
    } else if (year == 17) {
        _HP = 0.97; _HPunc = 0.06;
        _LP = 1.14; _LPunc = 0.29;
    } else if (year == 18) {
        _HP = 0.98; _HPunc = 0.027;
        _LP = 1.12; _LPunc = 0.275;
    } else {
        throw "Wtag_SF: Year not supported";
    }
}

ROOT::VecOps::RVec<float> Wtag_SF::eval(float tau21) {
    ROOT::VecOps::RVec<float> out;

    if (_year == 16) {
        if (tau21 < 0.4) {
            out = {_HP, _HP+_HPunc, _HP-_HPunc};
        } else {
            out = {_LP, _LP+_LPunc, _LP-_LPunc};
        }

    } else if (_year == 17) {
        if (tau21 < 0.45) {
            out = {_HP, _HP+_HPunc, _HP-_HPunc};
        } else if (tau21 < 0.75) {
            out = {_LP, _LP+_LPunc, _LP-_LPunc};
        } else {
            out = {1., 1., 1.};
        }

    } else if (_year == 18) {
        if (tau21 < 0.4) {
            out = {_HP, _HP+_HPunc, _HP-_HPunc};
        } else if (tau21 < 0.75) {
            out = {_LP, _LP+_LPunc, _LP-_LPunc};
        } else {
            out = {1., 1., 1.};
        }
    } 

    return out;
}