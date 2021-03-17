#ifndef _TIMBER_JETSMEARER
#define _TIMBER_JETSMEARER
// Requires CMSSW
#include <string>
#include <vector>
#include <cstdlib>
#include <unistd.h>
#include <math.h>
#include <limits>
#include <random>

#include <TRandom3.h>
#include <TFile.h>
#include <TF1.h>
#include <TString.h>
#include <TSystem.h>
#include <ROOT/RVec.hxx>
#include <Math/GenVector/LorentzVector.h>
#include <Math/GenVector/PtEtaPhiM4D.h>
#include <Math/Vector4Dfwd.h>
#include "JME_common.h"
#include "common.h"

using namespace ROOT::VecOps;
using LorentzV = ROOT::Math::PtEtaPhiMVector;

/**
 * @brief C++ class to match single reconstructed jet (represented as a Lorentz vector)
 * to the closest generator jet in a vector of generator jets (represented as Lorentz vectors).
 * 
 */
class GenJetMatcher {
    private:
        float _dRMax, _dPtMaxFactor;

    public: 
        /**
         * @brief Construct a new GenJetMatcher object
         * 
         * @param dRMax The maximum \f$\Delta R\f$ to consider. For an AK8 jet, use 0.4.
         * @param dPtMaxFactor The maximum \f$p_{T}\f$ factor to consider where the difference
         *  \f$p_{T}\f$ between the reco and gen jets must be less than dPtMaxFactor times the resolution
         * (provided as an argument to GenJetMatcher::match). Default is 3.
         */
        GenJetMatcher(float dRMax, float dPtMaxFactor = 3);
        /**
         * @brief Perform the actual matching
         * 
         * @param jet Lorentz vector for the reco jet.
         * @param genJets Vector of Lorentz vectors of the gen jets.
         * @param resolution \f$p_{T}\f$ resolution to consider.
         * @return LorentzV The gen jet that matches.
         */
        LorentzV match(LorentzV& jet, RVec<LorentzV> genJets, float resolution);
};

/**
 * @brief C++ class to handle the smearing of jet pt and mass using
 * the JER and JMR inputs, respectively.
 * 
 */
class JetSmearer {
    private:
        const std::string _jetType, _jerTag;
        const std::vector<float> _jmrVals;

        std::mt19937 _rnd;
        JERpaths _path;
        JME::JetParameters _paramsSF;
        JME::JetParameters _paramsRes;
        JME::JetResolution _jer;
        JME::JetResolutionScaleFactor _jerSF;

        std::vector<Variation> _variationIndex;
        
        std::shared_ptr<GenJetMatcher> _genJetMatcher;
        static constexpr const double MIN_JET_ENERGY = 1e-2;

        TF1* _puppisd_res_central;
        TF1* _puppisd_res_forward;

    public:
        /**
         * @brief Construct a new Jet Smearer object for jet
         * energy smearing.
         * 
         * @param jerTag The JER tag to identify the JER files to load.
         * @param jetType The type of jet - ex. AK8PFPuppi
         */
        JetSmearer( std::string jerTag, std::string jetType);
        /**
         * @brief Construct a new Jet Smearer object for jet 
         * mass smearing.
         * 
         * @param jmrVals The JMR values stored as a vector ordered as
         * nominal, up, down. 
         */
        JetSmearer(std::vector<float> jmrVals);

        ~JetSmearer();
        /**
         * @brief Smear jet pT to account for measured difference in JER between data and simulation.
         *  The function computes the nominal smeared jet pT simultaneously with the JER up and down shifts,
         *  in order to use the same random number to smear all three (for consistency reasons).
         *  
         *  The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
         * 
         *  The function considers three cases:
         *      Case 1: we have a "good" generator level jet matched to the reconstructed jet,
         *      Case 2: we don't have a generator level jet so we smear jet pT using a random Gaussian variation,
         *      Case 3: we cannot smear this jet, as we don't have a generator level jet and the resolution
         *          in data is better than the resolution in the simulation, so we would need to randomly
         *          "unsmear" the jet, which is impossible.
         * 
         * @param jet Jet Lorentz vector
         * @param genJets Vector of possible matching GenJet Lorentz vectors
         * @param fixedGridRhoFastjetAll Stored in the NanoAOD with this name as the branch name.
         * @return std::vector<float> {nominal,up,down}
         */
        std::vector<float> GetSmearValsPt(LorentzV jet, RVec<LorentzV> genJets, float fixedGridRhoFastjetAll);
        /**
         * @brief Smear jet mass to account for measured difference in JMR between 
         * data and simulation. The function computes the nominal smeared jet mass
         * simultaneously with the JMR up and down shifts, in order to use the
         * same random number to smear all three (for consistency reasons).
         * 
         * Consider three cases:
         *  Case 1: we have a "good" generator level jet matched to the reconstructed jet,
         *  Case 2: we don't have a generator level jet so we smear jet mass using a random Gaussian variation,
         *  Case 3: we cannot smear this jet, as we don't have a generator level jet and the
         *      resolution in data is better than the resolution in the simulation, so we would need
         *      to randomly "unsmear" the jet, which is impossible.
         * 
         * The implementation of this function follows:
         * PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
         * Procedure outline in: https://twiki.cern.ch/twiki/bin/view/Sandbox/PUPPIJetMassScaleAndResolution
         * @param jet Jet Lorentz vector
         * @param genJets Vector of possible matching GenJet Lorentz vectors
         * @return std::vector<float> {nominal,up,down}
         */
        std::vector<float> GetSmearValsM(LorentzV jet, RVec<LorentzV> genJets);
        /**
         * @brief Get the file for mass resolution smearing.
         * 
         * @return TFile* 
         */
        TFile* GetPuppiJMRFile();
        /**
         * @brief Get the function for the mass resolution for the central portion of the detector.
         * 
         * @return TF1* 
         */
        TF1* GetPuppiSDResolutionCentral();
        /**
         * @brief Get the function for the mass resolution for the forward portion of the detector.
         * 
         * @return TF1* 
         */
        TF1* GetPuppiSDResolutionForward();
};
#endif