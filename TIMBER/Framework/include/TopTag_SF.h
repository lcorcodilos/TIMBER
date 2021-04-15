#ifndef _TIMBER_TOPTAG_SF
#define _TIMBER_TOPTAG_SF
#include <string>
#include <TFile.h>
#include <TH1F.h>
#include <TString.h>
#include <Math/Vector4Dfwd.h>
#include <Math/GenVector/LorentzVector.h>
#include <Math/GenVector/PtEtaPhiM4D.h>
#include "GenMatching.h"
using LVector = ROOT::Math::PtEtaPhiMVector;

/**
 * @brief C++ class to access scale factors associated with tau32+subjet btag(+mass)
 * based top tagging. More details provided at https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetTopTagging](https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetTopTagging)
 */
class TopTag_SF {
    private:
        std::string workpoint_name;
        int _year;
        std::map<int, std::map<std::string, TH1F*>> _hists;
        TFile *_file;

    public:
        /**
         * @brief Construct a new TopTag_SF object
         * 
         * @param year 2016, 2017, 2018
         * @param workpoint 1 through 5. See Twiki above for details.
         * @param NoMassCut Bool based on whether a jet mass cut is applied for the tag.
         */
        TopTag_SF(int year, int workpoint, bool NoMassCut=false);
        ~TopTag_SF(){};
        /**
         * @brief Finds the number of merged generator particles
         * in the reconstructed jet.
         * 
         * @param top_vect LorentzVector of the reconstructed top jet
         * @param Ws Vector of (pointers to) the W particles
         * @param quarks Vector of (pointers to) the non-top quark particles
         * @param GPT GenParticleTree object with particles already added to tree.
         * @return int Number of merged particles. Maximum of 3 (ie. if more than 
         *      three are found, three is returned).
         */
        int NMerged(LVector top_vect, RVec<Particle*> Ws,
                RVec<Particle*> quarks, GenParticleTree GPT);
        /**
         * @brief Evaluation function based on the reconstructed top jet pt
         *  and the matched generator particles (GenParts).
         *  
         * @tparam T Array of structs constructed dynamically by TIMBER
         * @param top_vect Reconstructed top jet LorentzVector
         * @param GenParts Generator particles array of structs created dynamically by TIMBER (named `GenParts`).
         * @return RVec<double> Scale factor values, {nominal, up, down} (absolute)
         */
        template <class T>
        RVec<double> eval(LVector top_vect, std::vector<T> GenParts){
            GenParticleTree GPT(GenParts.size());
            // prongs are final particles we'll check
            RVec<Particle*> Ws, quarks; 
            int this_pdgId;

            for (size_t i = 0; i < GenParts.size(); i++) {
                Particle* this_particle = GPT.AddParticle(Particle(i,GenParts[i])); // add particle to tree
                this_pdgId = this_particle->pdgId;
                if (abs(this_pdgId) == 24) {
                    Ws.push_back(this_particle);
                } else if (abs(this_pdgId) >= 1 && abs(this_pdgId) <= 5) {
                    quarks.push_back(this_particle);
                }
            }
            int nMergedProngs = NMerged(top_vect, Ws, quarks, GPT);
            std::vector<double> sfs(3);
            if (nMergedProngs > 0){
                if (top_vect.Pt() > 5000) {
                    sfs = {_hists[nMergedProngs]["nom"]->GetBinContent(_hists[nMergedProngs]["nom"]->GetNbinsX()),
                           _hists[nMergedProngs]["up"]->GetBinContent(_hists[nMergedProngs]["up"]->GetNbinsX()),
                           _hists[nMergedProngs]["down"]->GetBinContent(_hists[nMergedProngs]["down"]->GetNbinsX())
                            };
                } else {                    
                    sfs = {_hists[nMergedProngs]["nom"]->GetBinContent(_hists[nMergedProngs]["nom"]->FindFixBin(top_vect.Pt())),
                           _hists[nMergedProngs]["up"]->GetBinContent(_hists[nMergedProngs]["up"]->FindFixBin(top_vect.Pt())),
                           _hists[nMergedProngs]["down"]->GetBinContent(_hists[nMergedProngs]["down"]->FindFixBin(top_vect.Pt()))
                            };
                }        
            } else {
                sfs = {1, 1, 1};
            }
            return sfs;
        }
};
#endif