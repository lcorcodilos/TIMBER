#ifndef _TIMBER_TOPTAG_SF
#define _TIMBER_TOPTAG_SF
#include <string>
#include <TFile.h>
#include <TH1.h>
#include <TString.h>
#include <Math/Vector4Dfwd.h>
#include <Math/GenVector/LorentzVector.h>
#include <Math/GenVector/PtEtaPhiM4D.h>
#include "GenMatching.h"
using LVector = ROOT::Math::PtEtaPhiMVector;

class TopTag_SF {
    private:
        std::string workpoint_name;
        int _year;
        std::map<int, std::map<std::string, TH1F*>> _hists;
        TFile *_file;

    public:
        TopTag_SF(int year, int workpoint, bool NoMassCut=false);
        ~TopTag_SF(){};
        int NMerged(LVector top_vect, RVec<Particle*> Ws,
                RVec<Particle*> quarks, GenParticleTree GPT);

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