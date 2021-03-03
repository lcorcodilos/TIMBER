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
#include "Pythonic.h"
#include "JME_common.h"
#include "common.h"

using namespace ROOT::VecOps;
using LorentzV = ROOT::Math::PtEtaPhiMVector;

class GenJetMatcher {
    private:
        float _dRMax, _dPtMaxFactor;

    public: 
        GenJetMatcher() {};

        GenJetMatcher(float dRMax, float dPtMaxFactor = 3) : 
            _dRMax{dRMax}, _dPtMaxFactor(dPtMaxFactor) {};

        const LorentzV* match(LorentzV& jet, RVec<LorentzV> genJets, float resolution);
};

class JetSmearer {
    private:
        const std::string _jetType, _jerTag;
        const std::vector<float> _jmrVals;

        std::mt19937 _rnd;
        JME::JetParameters _paramsSF;
        JME::JetParameters _paramsRes;
        JME::JetResolution _jer;
        JME::JetResolutionScaleFactor _jerSF;

        std::vector<Variation> _variationIndex {
                Variation::NOMINAL,
                Variation::UP,
                Variation::DOWN
        };
        
        std::shared_ptr<GenJetMatcher> _genJetMatcher;
        static constexpr const double MIN_JET_ENERGY = 1e-2;

        TF1* _puppisd_res_central;
        TF1* _puppisd_res_forward;

    public:
        JetSmearer(){};
        // For JER smearing
        JetSmearer( std::string jetType, std::string jerTag);
        // For JMR smearing
        JetSmearer(std::vector<float> jmrVals);

        ~JetSmearer(){};
        /**
         * @brief Smear jet pT to account for measured difference in JER between data and simulation.
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
         * @param fixedGridRhoFastjetAll 
         * @return RVec<float> {nom,up,down}
         */
        RVec<float> GetSmearValsPt(LorentzV jet, RVec<LorentzV> genJets);
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
        RVec<float> GetSmearValsM(LorentzV jet, RVec<LorentzV> genJets);

        TFile* GetPuppiJMRFile() {
            return TFile::Open(TString(std::string(std::getenv("TIMBERPATH")) + "TIMBER/data/JME/puppiSoftdropResol.root"));;
        }

        TF1* GetPuppiSDResolutionCentral() {
            return (TF1*)this->GetPuppiJMRFile()->Get("massResolution_0eta1v3");
        } 

        TF1* GetPuppiSDResolutionForward() {
            return (TF1*)this->GetPuppiJMRFile()->Get("massResolution_1v3eta2v5");
        }
        
};
#endif