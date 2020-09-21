#include <stdio.h>
#include <string.h>
#include "../PhysicsObjects/GenParticleTree.h"
#include "TLorentzVector.h"
#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

namespace analyzer {
    int TopMergeChecker() {

    }
    bool WMatchChecker() {

    }

    float TopTaggingSF(char taggername[], int year, char mergecategory[], TLorentzVector jet) {
        // If tau32 only (yes, == 0 is correct because of how strcmp returns)
        if (strcmp(taggername,"tau32") == 0){
            if 
        } else if (strcmp(taggername,"tau32+sjbtag")){

        }
    }
    float WTaggingSF(char taggername[], int year, char purity[], float pt, float eta) {
        
    }
    float bTaggingSF(char taggername[], int year, char category[], float pt) {
        if (strcmp(taggername,"DeepCSV") == 0){
            std::string csv_name = ;
        }
        

        BTagCalibration calib("csvv1", "CSVV1.csv");
        BTagCalibrationReader reader(BTagEntry::OP_LOOSE,  // operating point
                                     "central",             // central sys type
                                     {"up", "down"});      // other sys types

        reader.load(calib,                // calibration instance
                    BTagEntry::FLAV_B,    // btag flavour
                    "incl")               // measurement type

        double jet_scalefactor    = reader.eval_auto_bounds(
            "central", 
            BTagEntry::FLAV_B, 
            b_jet.eta(), // absolute value of eta
            b_jet.pt()
        ); 
        double jet_scalefactor_up = reader.eval_auto_bounds(
            "up", BTagEntry::FLAV_B, b_jet.eta(), b_jet.pt());
        double jet_scalefactor_do = reader.eval_auto_bounds(
            "down", BTagEntry::FLAV_B, b_jet.eta(), b_jet.pt()); 
    }
}

int main(char particle[], char tagger[], char wp[] int year, TLorentzVector jet){
    if (strcmp(particle,"top") == 0) {
        if (strcmp(tagger,"tau32") == 0) {

        } else if (strcmp(tagger,"tau32+sjbtag") == 0) {

        } else {
            printf ("Top tagger not supported. Quitting...");
            exit(EXIT_FAILURE);
        }
    } else if (strcmp(particle,"W") == 0) {
        if strcmp(tagger,"tau21") {

        } else {
            printf ("W tagger not supported. Quitting...");
            exit(EXIT_FAILURE);
        }

    } else if (strcmp(particle,"bottom") == 0) {
        if strcmp(tagger,"DeepCSV") {

        } else {
            printf ("Bottom tagger not supported. Quitting...");
            exit(EXIT_FAILURE);
        }

    }

    return 0;
}