# How to use GenMatching.h

The NanoAOD format only stores the mother index of each generator particle.
This often makes it difficult to traverse the decay tree in search of particles
that are relevant to an analysis. `GenMatching.h` houses infrastructure to recreate
the relevant parts of the decay chain from the information available.

Note that the classes in `GenMatching.h` are only useful within the context of another
.cc script that is extracting information from the decay tree. There are no one-line
function calls that are useful within a TIMBER `Define` or `Cut`.

Below is an example of how to isolate the three quarks in an all-hadronic top quark decay
and return the number of quarks that are merged inside the reconstructed jet (this is something
one has to do for applying top tagging scale factors).

## Example: top to b+W(qq)

First, one should construct the skeleton of the function.

```.cc
#include "Math/Vector4Dfwd.h"
#include "TIMBER/Framework/include/GenMatching.h"

using LVector = ROOT::Math::PtEtaPhiMVector;

int NMerged(LVector top_vect, int nGenPart,
                RVec<float> GenPart_pt, RVec<float> GenPart_eta,
                RVec<float> GenPart_phi, RVec<float> GenPart_mass,
                RVec<int> GenPart_pdgId, RVec<int> GenPart_status,
                RVec<int> GenPart_statusFlags, RVec<int> GenPart_genPartIdxMother) {

    int nmerged = 0;
    /*
        rest of the code here
    */

    return nmerged;
}
```

Now create a GenParticleObjs instance. This is effectively reconfigures the
input information from vectors of properties to a vector of Particle objects,
each with its own properties. Adding to the `rest of the code here` area...

```.cc
GenParticleObjs GenParticles (GenPart_pt, GenPart_eta,
                                  GenPart_phi, GenPart_mass,
                                  GenPart_pdgId, GenPart_status,
                                  GenPart_statusFlags, GenPart_genPartIdxMother);
```

Now initialize the tree and some storage objects...

```.cc
GenParticleTree GPT;
// prongs are final particles we'll check
vector<Particle*> tops, Ws, quarks, prongs; 
```

Now we can start filling in the tree and tracking particle we care about (top, W, non-top quarks)...
```.cc
for (int i = 0; i < nGenPart; i++) {
    GenParticles.SetIndex(i); // access ith particle
    Particle* this_particle = &GenParticles.particle;
    GPT.AddParticle(this_particle); // add particle to tree
    
    int this_pdgId = *(this_particle->pdgId);

    if (abs(this_pdgId) == 6 && this_particle->DeltaR(top_vect) < 0.8) {
        tops.push_back(this_particle);
    } else if (abs(this_pdgId) == 24) {
        Ws.push_back(this_particle);
    } else if (abs(this_pdgId) >= 1 && abs(this_pdgId) <= 5) {
        quarks.push_back(this_particle);
    }
}
```

With the tree built and all of the tops, Ws, and non-top quarks tracked,
we'll look for the bottom quark (from the matching top).
```.cc
Particle *q, *bottom_parent;
for (int iq = 0; iq < quarks.size(); iq++) {
    q = quarks[iq];
    if (abs(*(q->pdgId)) == 5) { // if bottom
        bottom_parent = GPT.GetParent(q);
        if (bottom_parent->flag != false) { // if has parent
            // if parent is a matched top
            if (abs(*(bottom_parent->pdgId)) == 6 && bottom_parent->DeltaR(top_vect) < 0.8) { 
                prongs.push_back(q);
            }
        }
    }
}
```

Next, look for W (from the matching top) and then get the daughter quarks.
```.cc
Particle *W, *this_W, *wChild, *wParent;
vector<Particle*> this_W_children;
for (int iW = 0; iW < Ws.size(); iW++) {
    W = Ws[iW];
    wParent = GPT.GetParent(W);
    if (wParent->flag != false) {
        // Make sure parent is top that's in the jet
        if (abs(*(wParent->pdgId)) == 6 && wParent->DeltaR(top_vect) < 0.8) {
            this_W = W;
            this_W_children = GPT.GetChildren(this_W);
            // Make sure the child is not just another W
            if (this_W_children.size() == 1 && this_W_children[0]->pdgId == W->pdgId) {
                this_W = this_W_children[0];
                this_W_children = GPT.GetChildren(this_W);
            }
            // Add children as prongs
            for (int ichild = 0; ichild < this_W_children.size(); ichild++) {
                wChild = this_W_children[ichild];
                int child_pdgId = *(wChild->pdgId);
                if (abs(child_pdgId) >= 1 && abs(child_pdgId) <= 5) {
                    prongs.push_back(wChild);
                }
            } 
        }
    }
}
```

Finally, check how many of the prongs found are within the radius of the jet and return...
```.cc
for (int iprong = 0; iprong < prongs.size(); iprong++) {
    if (prongs[iprong]->DeltaR(top_vect) < 0.8) {
        nmerged++;
    }
}

return nmerged;
```