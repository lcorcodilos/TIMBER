// Requires CMSSW
#include <string>
#include <vector>
#include <cstdlib>
#include <unistd.h>
#include <math.h>
// #include "CondFormats/JetMETObjects/interface/JetResolutionObject.h"
// #include "JetMETCorrections/Modules/interface/JetResolution.h"
#include <TRandom3.h>
#include <TFile.h>
#include <TF1.h>
#include <TString.h>
#include <TSystem.h>
#include <ROOT/RVec.hxx>
#include <Math/GenVector/LorentzVector.h>
#include <Math/GenVector/PtEtaPhiM4D.h>
#include <Math/Vector4Dfwd.h>
#include "../include/Pythonic.h"

using namespace ROOT::VecOps;
using LorentzV = ROOT::Math::PtEtaPhiMVector;

class JetSmearer {
    private:
        const std::string jetType_;
        const std::string jerTag_;
        const std::vector<float> jmrVals_;
        const std::string timberPath_ = std::string(std::getenv("TIMBERPATH"));
        const std::string jerInputArchivePath_ = timberPath_ + "TIMBER/data/jme/";
        TFile *puppiJMRFile_ = new TFile(TString(timberPath_ + "TIMBER/data/jme/puppiSoftdropResol.root"));
        TF1 *puppisd_resolution_cen = (TF1*)puppiJMRFile_->Get("massResolution_0eta1v3");
        TF1 *puppisd_resolution_for = (TF1*)puppiJMRFile_->Get("massResolution_1v3eta2v5");
        
        TRandom3 rnd;
        std::string jerInputFileName_;
        std::string jerUncertaintyInputFileName_;
        char *tempDir = mkdtemp("/tmp/jmeuntar/");
        JME::JetParameters params_sf_and_uncertainty();
        JME::JetParameters params_resolution();
        
        JME::JetResolution jer;
        JME::JetResolution jerSF;

    public:
        JetSmearer(
            std::string jetType,
            std::string jetTag,
            std::vector<float> jmrVals);
        ~JetSmearer(){
            rmdir(tempDir);
        };
        RVec<float> GetSmearValsPt(LorentzV jet, LorentzV genJet, float rho);
        RVec<float> GetSmearValsM(LorentzV jet, LorentzV genJet);
};

JetSmearer::JetSmearer(std::string jetType,
            std::string jerTag,
            std::vector<float> jmrVals) : 
            jetType_(jetType), jerTag_(jerTag),
            jmrVals_(jmrVals),
            jerInputFileName_(jerTag + "_PtResolution_" + jetType + ".txt"),
            jerUncertaintyInputFileName_(jerTag + "_SF_" + jetType + ".txt") {

    Pythonic::Execute(std::string("tar -xzvf "+jerInputArchivePath_+"/"+jerInputFileName_+" -C "+tempDir));
    Pythonic::Execute(std::string("tar -xzvf "+jerInputArchivePath_+"/"+jerUncertaintyInputFileName_+" -C "+tempDir));

    rnd = TRandom3(12345); // initialize random number generator
                                 // (needed for jet pT smearing)
    
    // load libraries for accessing JER scale factors and uncertainties from txt files
    // NOTE: Not sure if this is still necessary but will try it
    std::vector<std::string> libraries = {"libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools"};
    for (size_t ilib = 0; ilib < libraries.size(); ilib++) {
       if (Pythonic::InList(libraries[ilib],Pythonic::Split(gSystem->GetLibraries()))) {
            printf("Load Library '%s'", libraries[ilib].c_str());
            gSystem->Load(TString(libraries[ilib]));
       }
    }         

    printf("Loading jet energy resolutions (JER) from file '%s/%s'",tempDir.c_str(),jerInputFileName_.c_str());
    jer = JetResolution(TString(tempDir+jerInputFileName_));
    
    printf("Loading JER scale factors and uncertainties from file '%s'",tempDir.c_str(),jerUncertaintyInputFileName_.c_str());
    jerSF = JetResolutionScaleFactor(TString(tempDir+jerUncertaintyInputFileName_));

}

/**
 * @brief CV: Smear jet pT to account for measured difference in JER between data and simulation.
 *  The function computes the nominal smeared jet pT simultaneously with the JER up and down shifts,
 *  in order to use the same random number to smear all three (for consistency reasons).
 *  
 *  The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
 * 
 *  Consider three cases:
 *      Case 1: we have a "good" generator level jet matched to the reconstructed jet
 *      Case 2: we don't have a generator level jet. Smear jet pT using a random Gaussian variation
 *      Case 3: we cannot smear this jet, as we don't have a generator level jet and the resolution
 *          in data is better than the resolution in the simulation, so we would need to randomly
 *          "unsmear" the jet, which is impossible
 * 
 * @param jet Jet Lorentz vector
 * @param genJet GenJet Lorentz vector
 * @param rho 
 * @return RVec<float> {nom,up,down}
 */
RVec<float> JetSmearer::GetSmearValsPt(LorentzV jet, LorentzV genJet, float rho) {
    RVec<float> out = {};
    if (jet.Pt() <= 0.){
        printf("WARNING: jet pT = %f !!", jet.Pt());
        out = {1.,1.,1.};
    }

    int central_or_shift;
    std::vector<int> variation_index = {0,2,1}; // nom,up,down

    std::map<int, float> jet_pt_sf_and_uncertainty = {};
    for (size_t i = 0; i < 3; i++) {
        central_or_shift = variation_index[i];
        params_sf_and_uncertainty.setJetEta(jet.Eta());
        params_sf_and_uncertainty.setJetPt(jet.Pt());

        jet_pt_sf_and_uncertainty[central_or_shift] = 
            jerSF.getScaleFactor(params_sf_and_uncertainty, central_or_shift);
    }
    
    std::map<int, float> smear_vals = {};
    float jet_pt_resolution, smear_factor;
    if (genJet) { // Case 1
        for (size_t i = 0; i < 3; i++) {
            central_or_shift = variation_index[i];
            float dPt = jet.Pt() - genJet.Pt();
            smear_factor = 1. + (jet_pt_sf_and_uncertainty[central_or_shift] - 1.) * dPt /  jet.Pt();
            smear_vals[central_or_shift] = smear_factor;
        }
    } else {
        params_resolution.setJetPt(jet.Pt());
        params_resolution.setJetEta(jet.Eta());
        params_resolution.setRho(rho);
        jet_pt_resolution = jer.getResolution(params_resolution);

        float rand = rnd.Gaus(0, jet_pt_resolution);

        for (size_t i = 0; i < 3; i++) {
            central_or_shift = variation_index[i];

            if (jet_pt_sf_and_uncertainty[central_or_shift] > 1.){ // Case 2
                smear_factor =
                    1. + rand * sqrt( pow(jet_pt_sf_and_uncertainty[central_or_shift],2) - 1.);
            } else { // Case 3
                smear_factor = 1.;
            }
            smear_vals[central_or_shift] = smear_factor;
        }
    }

    // check that smeared jet energy remains positive, as the direction of
    // the jet would change ("flip") otherwise - and this is not what we want
    for (size_t i = 0; i < 3; i++) {
        central_or_shift = variation_index[i];
        if (smear_vals[central_or_shift] * jet.E() < 1.e-2){
            smear_vals[central_or_shift] = 1.e-2 / jet.E();
        }
        out.push_back(smear_vals[central_or_shift]);
    }
    return out;
}

/**
 * @brief Smear jet m to account for measured difference in JMR between 
 * data and simulation. The function computes the nominal smeared jet m
 * simultaneously with the JMR up and down shifts, in order to use the
 * same random number to smear all three (for consistency reasons).
 * 
 * Consider three cases:
 *  Case 1: we have a "good" generator level jet matched to the reconstructed jet
 *  Case 2: we don't have a generator level jet. Smear jet m using a random Gaussian variation
 *  Case 3: we cannot smear this jet, as we don't have a generator level jet and the
 *      resolution in data is better than the resolution in the simulation, so we would need
 *      to randomly "unsmear" the jet, which is impossible.
 * 
 * The implementation of this function follows:
 * PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
 * Procedure outline in: https://twiki.cern.ch/twiki/bin/view/Sandbox/PUPPIJetMassScaleAndResolution
 * 
 * @return def 
 */
RVec<float> JetSmearer::GetSmearValsM(LorentzV jet, LorentzV genJet){
    RVec<float> out = {};
    if (jet.M() <= 0.){
        printf("WARNING: jet m = %f !!", jet.M());
        out = {1.,1.,1.};
    }

    int central_or_shift;
    std::vector<int> variation_index = {0,2,1}; // nom,up,down

    std::map<int, float> jet_m_sf_and_uncertainty = {
        {0, jmrVals_[0]},
        {1, jmrVals_[1]},
        {2, jmrVals_[2]}
    };
    
    std::map<int, float> smear_vals = {};
    float jet_pt_resolution, smear_factor;

    if (genJet) { // Case 1
        for (size_t i = 0; i < 3; i++) {
            central_or_shift = variation_index[i];
            float dM = jet.M() - genJet.M();
            smear_factor =
                1. + jet_m_sf_and_uncertainty[central_or_shift] - 1. * dM / jet.M();
        }
    } else {
        float jet_m_resolution;
        if (abs(jet.Eta()) <= 1.3) {
            jet_m_resolution = puppisd_resolution_cen->Eval(jet.Pt());
        } else {
            jet_m_resolution = puppisd_resolution_for->Eval(jet.Pt());
        }

        float rand = rnd.Gaus(0, jet_m_resolution);
        for (size_t i = 0; i < 3; i++) {
            central_or_shift = variation_index[i];
            if (jet_m_sf_and_uncertainty[central_or_shift] > 1.){ // Case 2
                smear_factor =
                    rand * sqrt(pow(jet_m_sf_and_uncertainty[central_or_shift],2) - 1.);
            } else { // Case 3
                smear_factor = 1.;
            }
        }
    }

    // check that smeared jet energy remains positive, as the direction of
    // the jet would change ("flip") otherwise - and this is not what we want
    for (size_t i = 0; i < 3; i++) {
        central_or_shift = variation_index[i];
        if (smear_vals[central_or_shift] * jet.M() < 1.e-2){
            smear_vals[central_or_shift] = 1.e-2;
        }
        out.push_back(smear_vals[central_or_shift]);
    }
    return out;
}