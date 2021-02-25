// Requires CMSSW
#include "../include/JES_weight.h"

JES_weight::JES_weight(str globalTag, str jetFlavour, bool redoJECs):
            _globalTag(globalTag), _jetFlavour(jetFlavour), _redoJECs(redoJECs) {
    JetRecalibrator _jetRecalib (_globalTag, _jetFlavour, true);
};
