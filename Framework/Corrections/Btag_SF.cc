// with CMSSW:
#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
  std::vector<float> BtagSF(BTagCalibrationReader reader,ROOT::Math::PtEtaPhiMVector b_jet0,ROOT::Math::PtEtaPhiMVector b_jet1) {
    std::vector<float> v;

    // Note: this is for b jets, for c jets (light jets) use FLAV_C (FLAV_UDSG)
    double jet_scalefactor = reader.eval_auto_bounds("central", BTagEntry::FLAV_B, b_jet0.Eta(),b_jet0.Pt()); 
    double jet_scalefactor_up = reader.eval_auto_bounds("up", BTagEntry::FLAV_B, b_jet0.Eta(), b_jet0.Pt());
    double jet_scalefactor_do = reader.eval_auto_bounds("down", BTagEntry::FLAV_B, b_jet0.Eta(), b_jet0.Pt());

    jet_scalefactor *= reader.eval_auto_bounds("central", BTagEntry::FLAV_B, b_jet1.Eta(),b_jet1.Pt()); 
    jet_scalefactor_up *= reader.eval_auto_bounds("up", BTagEntry::FLAV_B, b_jet1.Eta(), b_jet1.Pt());
    jet_scalefactor_do *= reader.eval_auto_bounds("down", BTagEntry::FLAV_B, b_jet1.Eta(), b_jet1.Pt());


    v.push_back(jet_scalefactor);
    v.push_back(jet_scalefactor_up);
    v.push_back(jet_scalefactor_do);

    return v;
  }
}

