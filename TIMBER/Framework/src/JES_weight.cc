// Requires CMSSW
#include "../include/JES_weight.h"

JES_weight::JES_weight(str jecTag, str jetType, str uncertType, bool redoJECs):
            _jecTag(jecTag), _jetType(jetType), _uncertType(uncertType), _redoJECs(redoJECs),
            _jetRecalib(_jecTag, _jetType, true, _uncertType){
    if (!this->check_type_exists()) {
        throw "Type '"+_uncertType+"' does not exist in list of sources.";
    }
};

bool JES_weight::check_type_exists() {
    bool out;
    if (_uncertType == "") {
        out = true;
    } else {
        if (Pythonic::InList(_uncertType,this->get_sources())>-1) {
            out = true;
        } else {
            out = false;
        }
    }
    return out;
}

std::vector<std::string> JES_weight::get_sources() {
    JESpaths paths(_jecTag, _jetType);
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