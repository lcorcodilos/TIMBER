#include "../include/TopTag_SF.h"

TopTag_SF::TopTag_SF(int year, int workpoint, bool NoMassCut) :
        _year(year > 2000 ? year - 2000 : year) {

    workpoint_name = "wp"+std::to_string(workpoint);
    std::string filename = "TIMBER/data/OfficialSFs/20"+std::to_string(_year)+"TopTaggingScaleFactors";
    if (NoMassCut){filename += "_NoMassCut.root";}
    else {filename += ".root";}
    _file = hardware::Open(filename);

    _hists[3]["nom"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_mergedTop_nominal"));
    _hists[3]["up"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_mergedTop_up"));
    _hists[3]["down"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_mergedTop_down"));

    _hists[2]["nom"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_semimerged_nominal"));
    _hists[2]["up"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_semimerged_up"));
    _hists[2]["down"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_semimerged_down"));

    _hists[1]["nom"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_notmerged_nominal"));
    _hists[1]["up"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_notmerged_up"));
    _hists[1]["down"] = (TH1F*)_file->Get(TString("PUPPI_"+workpoint_name+"_btag/sf_notmerged_down"));
};

int TopTag_SF::NMerged(LVector top_vect, RVec<Particle*> Ws, RVec<Particle*> quarks, GenParticleTree GPT) {
    int nmerged = 0;
    // prongs are final particles we'll check
    RVec<Particle*> prongs; 

    Particle *q, *bottom_parent;
    for (size_t iq = 0; iq < quarks.size(); iq++) {
        q = quarks[iq];
        if (abs(q->pdgId) == 5) { // if bottom
            bottom_parent = GPT.GetParent(q);
            if (bottom_parent->flag != false) { // if has parent
                // if parent is a matched top
                if (abs(bottom_parent->pdgId) == 6 && bottom_parent->DeltaR(top_vect) < 0.8) { 
                    prongs.push_back(q);
                }
            }
        }
    }

    Particle *W, *this_W, *wChild, *wParent;
    std::vector<Particle*> this_W_children;
    for (size_t iW = 0; iW < Ws.size(); iW++) {
        W = Ws[iW];
        wParent = GPT.GetParent(W);
        if (wParent->flag != false) {
            // Make sure parent is top that's in the jet
            if (abs(wParent->pdgId) == 6 && wParent->DeltaR(top_vect) < 0.8) {
                this_W = W;
                this_W_children = GPT.GetChildren(this_W);
                // Make sure the child is not just another W
                if ((this_W_children.size() == 1) && (this_W_children[0]->pdgId == W->pdgId)) {
                    this_W = this_W_children[0];
                    this_W_children = GPT.GetChildren(this_W);
                }
                // Add children as prongs
                for (size_t ichild = 0; ichild < this_W_children.size(); ichild++) {
                    wChild = this_W_children[ichild];
                    int child_pdgId = wChild->pdgId;
                    if (abs(child_pdgId) >= 1 && abs(child_pdgId) <= 5) {
                        prongs.push_back(wChild);
                    }
                } 
            }
        }
    }
    for (size_t iprong = 0; iprong < prongs.size(); iprong++) {
        if (prongs[iprong]->DeltaR(top_vect) < 0.8) {
            nmerged++;
        }
    }
    return std::min(nmerged,3);
}

