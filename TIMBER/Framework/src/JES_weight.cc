// Requires CMSSW
#include "../include/JES_weight.h"

JES_weight::JES_weight(str globalTag, str jetFlavour, str uncertType, bool redoJECs):
            _globalTag(globalTag), _jetFlavour(jetFlavour), _uncertType(uncertType), _redoJECs(redoJECs) {
    JetRecalibrator _jetRecalib (_globalTag, _jetFlavour, true, _uncertType);
    if (!this->check_type_exists()) {
        throw "Type '"+_uncertType+"' does not exist in list of sources.";
    }
};

bool JES_weight::check_type_exists() {
    bool out;
    if (_uncertType == "") {
        out = true;
    } else {
        if (Pythonic::InList(_uncertType,this->get_sources())) {
            out = true;
        } else {
            out = false;
        }
    }
    return out;
}

std::vector<std::string> JES_weight::get_sources() {
    JESpaths paths(_globalTag, _jetFlavour);
    std::istringstream f(paths.GetTxtFileStr("Uncert"));
    std::string line;
    std::vector<std::string> sources;
    while (std::getline(f, line)) {
        if (line.find("[") == 0 && line.find("]") == line.length()) {
            sources.push_back(line.substr(1, line.length()-1));
        }
    }
    return sources;
}