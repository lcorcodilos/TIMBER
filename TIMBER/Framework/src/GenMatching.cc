#include "../include/GenMatching.h"

bool GenMatching::BitChecker(const int &bit, int &number){
    int result = number & (1 << bit);

    if (result > 0) {return true;}
    else {return false;}
}

std::map <int, std::string> GenMatching::PDGIds {
    {1,"d"}, {2,"u"}, {3,"s"}, {4,"c"}, {5,"b"}, {6,"t"},
    {11,"e"}, {12,"nu_e"}, {13,"mu"}, {14,"nu_mu"},{ 15,"tau"},
    {16,"nu_tau"}, {21,"g"}, {22,"photon"}, {23,"Z"}, {24,"W"}, {25,"h"}
};

std::map <std::string, int> GenMatching::GenParticleStatusFlags {
        {"isPrompt", 0},
        {"isDecayedLeptonHadron", 1},
        {"isTauDecayProduct", 2},
        {"isPromptTauDecayProduct", 3},
        {"isDirectTauDecayProduct", 4},
        {"isDirectPromptTauDecayProduct", 5},
        {"isDirectHadronDecayProduct", 6},
        {"isHardProcess", 7},
        {"fromHardProcess", 8},
        {"isHardProcessTauDecayProduct", 9},
        {"isDirectHardProcessTauDecayProduct", 10},
        {"fromHardProcessBeforeFSR", 11},
        {"isFirstCopy", 12},
        {"isLastCopy", 13},
        {"isLastCopyBeforeFSR", 14}
};

Particle::Particle(){};

void Particle::AddParent(int idx){
    parentIndex = idx;
}

void Particle::AddChild(int idx){
    childIndex.push_back(idx);
}

float Particle::DeltaR(LVector input_vector){
    return ROOT::Math::VectorUtil::DeltaR(vect,input_vector);
};

std::vector<int> GenParticleTree::StoredIndexes(){
    std::vector<int> current_idxs {};
    for (size_t i = 0; i < nodes.size(); i++) {
        current_idxs.push_back(nodes.at(i)->index);
    }
    return current_idxs;
}

void GenParticleTree::AddParticle(Particle* particle) {
    Particle* staged_node = particle;

    // First check if current heads don't have new parents and 
    // remove them from heads if they do
    std::vector<int> heads_to_delete {};
    for (size_t i = 0; i < heads.size(); i++) {
        if (heads.at(i)->parentIndex == staged_node->index) {
            heads_to_delete.push_back(i);
        }
    }
    // Need to delete indices in reverse order so as not to shift 
    // indices after a deletion
    for (int ih = heads_to_delete.size(); ih >= 0; ih--) {
        heads.erase(heads.begin()+ih);
    }
   
    // Next identify staged node has no parent (heads)
    // If no parent, no other infor we can get from this particle
    std::vector<int> indexes = StoredIndexes();
    if (Pythonic::InList(staged_node->parentIndex, indexes)) {
        heads.push_back(staged_node);
        nodes.push_back(staged_node);
    } else {
        for (size_t inode = 0; inode < nodes.size(); inode++) {
            if (staged_node->parentIndex == nodes[inode]->index){
                staged_node->AddParent(inode);
                nodes.at(inode)->AddChild(nodes.size());
                nodes.push_back(staged_node);
            }
        }        
    }
};

std::vector<Particle*> GenParticleTree::GetChildren(Particle* particle){
    std::vector<Particle*> children {};
    for (size_t i = 0; i < particle->childIndex.size(); i++) {
        children.push_back(nodes[particle->childIndex.at(i)]);
    }
    return children;
}

Particle* GenParticleTree::GetParent(Particle* particle) {
    if (nodes.size() > particle->parentIndex){
        return nodes.at(particle->parentIndex);
    } else {
        return &NoneParticle;
    }
    
}

bool GenParticleTree::MatchParticleToString(Particle* particle, std::string string){
    std::vector<int> pdgIds {}; 
    if (Pythonic::InString(":",string)) {
        int startId = std::stoi( string.substr(0,string.find(':')) );
        int stopId  = std::stoi( string.substr(1,string.find(':')) );
        pdgIds = Pythonic::Range(startId, stopId);
    } else if (Pythonic::InString(",",string)) {
        auto splits = Pythonic::Split(string,',');
        for (size_t istr = 0; istr < splits.size(); istr++) {
            pdgIds.push_back( std::stoi(splits.at(istr)) );
        }
    }

    bool out;
    if (pdgIds.size() == 0) {
        if (std::abs(*particle->pdgId) == std::stoi(string)) {
            out = true;
        } else {out = false;}
    } else {
        if (Pythonic::InList((int)std::abs(*particle->pdgId), pdgIds)) {
            out = true;
        } else {out = false;}
    }

    return out;
}

std::vector<Particle*> GenParticleTree::RunChain(Particle* node, std::vector<std::string> chain) {
    std::vector<Particle*> nodechain {node};
    Particle* parent = GetParent(node);
    std::vector<std::string> chain_minus_first = {chain.begin()+1,chain.end()};
    
    if (chain.size() == 0) {
        return nodechain;
    } else if (parent->flag == false) {
        nodechain.push_back(&NoneParticle);
    } else if (MatchParticleToString(parent, chain.at(0))) {
        Pythonic::Extend(nodechain, RunChain(parent,chain_minus_first));
    } else if (parent->pdgId == node->pdgId) {
        Pythonic::Extend(nodechain, RunChain(parent, chain));
    } else {
        nodechain.push_back(&NoneParticle);
    }

    return nodechain;
}

std::vector<std::vector<Particle*>> GenParticleTree::FindChain(std::string chainstring) {
    std::vector<std::string> reveresed_chain = Pythonic::Split(chainstring,'>');
    std::reverse(reveresed_chain.begin(), reveresed_chain.end());

    std::vector<std::string> reveresed_chain_minus_first = {reveresed_chain.begin()+1,reveresed_chain.end()};

    std::vector<Particle*> chain_result;
    std::vector<std::vector<Particle*>> out;

    for (size_t inode = 0; inode < nodes.size(); inode++) {
        Particle* n = nodes[inode];
        if (MatchParticleToString(n, reveresed_chain.at(0))) {
            chain_result = RunChain(n,reveresed_chain_minus_first);
            bool no_NoneParticle = true;
            for (size_t icr = 0; icr < chain_result.size(); icr++) {
                if (chain_result[icr]->flag == false) {
                    no_NoneParticle = false;
                    break;
                }
            }
            if (no_NoneParticle) {out.push_back(chain_result);}
        } 
    }
    return out;
}

GenParticleObjs::GenParticleObjs(RVec<float> in_pt, 
                RVec<float> in_eta, RVec<float> in_phi, 
                RVec<float> in_m, RVec<int> in_pdgId, 
                RVec<int> in_status, RVec<int> in_statusFlags, 
                RVec<int> in_genPartIdxMother) {

    GenPartCollection.RVecInt = { 
        {"pdgId",&in_pdgId},
        {"status",&in_status},
        {"statusFlags",&in_statusFlags},
        {"genPartIdxMother",&in_genPartIdxMother}
    };
    GenPartCollection.RVecFloat = { 
        {"pt",&in_pt},
        {"eta",&in_eta},
        {"phi",&in_phi},
        {"m",&in_m}
    };
    // Settings for the "set" particle
    particle.index = -1;
}

GenParticleObjs::GenParticleObjs(Collection genParts) {
    GenPartCollection = genParts;
};

void GenParticleObjs::SetStatusFlags(int particleIndex){
    for (auto it = GenMatching::GenParticleStatusFlags.begin(); it != GenMatching::GenParticleStatusFlags.end(); ++it) {
        particle.statusFlags[it->first] = GenMatching::BitChecker(it->second, GenPartCollection.RVecInt["statusFlags"]->at(particleIndex));
    }
}

std::map< std::string, bool> GenParticleObjs::CompareToVector(LVector vect) {
    std::map< std::string, bool> out;
    out["sameHemisphere"] = (ROOT::Math::VectorUtil::DeltaPhi(particle.vect,vect) < M_PI);
    out["deltaR"] = (particle.DeltaR(vect) < 0.8);
    out["deltaM"] = (std::abs(vect.M() - particle.vect.M())/particle.vect.M() < 0.05);
    return out;
};

Particle GenParticleObjs::SetIndex(int idx) {
    particle.index = idx;
    particle.pdgId = &GenPartCollection.RVecInt["pdgId"]->at(idx);
    SetStatusFlags(idx);
    particle.parentIndex = GenPartCollection.RVecInt["genPartIdxMother"]->at(idx);
    particle.vect.SetCoordinates(
        GenPartCollection.RVecFloat["pt"]->at(idx),
        GenPartCollection.RVecFloat["eta"]->at(idx),
        GenPartCollection.RVecFloat["phi"]->at(idx),
        GenPartCollection.RVecFloat["m"]->at(idx)
        );

    return particle;
};   

int GenParticleObjs::GetStatusFlag(std::string flagName){
    return particle.statusFlags[flagName];
};