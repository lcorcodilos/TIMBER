#include "../include/GenMatching.h"

bool GenMatching::BitChecker(const int &bit, int &number){
    int result = number & (1 << bit);

    if (result > 0) {return true;}
    else {return false;}
}
namespace GenMatching {
    std::map <int, std::string> PDGIds {
        {1,"d"}, {2,"u"}, {3,"s"}, {4,"c"}, {5,"b"}, {6,"t"},
        {11,"e"}, {12,"nu_e"}, {13,"mu"}, {14,"nu_mu"},{ 15,"tau"},
        {16,"nu_tau"}, {21,"g"}, {22,"photon"}, {23,"Z"}, {24,"W"}, {25,"h"}
    };
    std::map <std::string, int> GenParticleStatusFlags {
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
}

Particle::Particle(): parentIndex(-1){
    childIndex.reserve(5);
};
void Particle::AddParent(int idx){
    parentIndex = idx;
}
void Particle::AddChild(int idx){
    childIndex.push_back(idx);
}
int Particle::GetParent(){
    return parentIndex;
}
std::vector<int> Particle::GetChild(){
    return childIndex;
}
float Particle::DeltaR(LVector input_vector){
    return ROOT::Math::VectorUtil::DeltaR(vect,input_vector);
}
void Particle::SetStatusFlags(int flags){
    for (auto it = GenMatching::GenParticleStatusFlags.begin(); it != GenMatching::GenParticleStatusFlags.end(); ++it) {
        statusFlags[it->first] = GenMatching::BitChecker(it->second, flags);
    }
}
int Particle::GetStatusFlag(std::string flagName){
    return statusFlags[flagName];
}
std::map< std::string, bool> Particle::CompareToVector(LVector vect) {
    std::map< std::string, bool> out;
    out["sameHemisphere"] = (ROOT::Math::VectorUtil::DeltaPhi(this->vect,vect) < M_PI/2.0);
    out["deltaR"] = (this->DeltaR(vect) < 0.8);
    out["deltaM"] = (std::abs(vect.M() - this->vect.M())/this->vect.M() < 0.05);
    return out;
}

GenParticleTree::GenParticleTree(int nParticles){
    _noneParticle.flag = false;
    _nodes.reserve(nParticles);
};

Particle* GenParticleTree::AddParticle(Particle particle) {
    int new_particle_index = _nodes.size();
    // First check if current heads don't have new parents and 
    // remove them from heads if they do
    std::vector<int> heads_to_delete {};
    for (size_t i = 0; i < _heads.size(); i++) {
        if (_heads[i]->genPartIdxMother == particle.index) {
            heads_to_delete.push_back(i);
        }
    }
    // Need to delete indices in reverse order so as not to shift 
    // indices after a deletion
    for (int ih = heads_to_delete.size()-1; ih >= 0; ih--) {
        _heads.erase(_heads.begin()+heads_to_delete[ih]);
    }
    // Set relationship to all current nodes
    for (int inode = 0; inode < _nodes.size(); inode++) {
        if (_nodes[inode].genPartIdxMother == particle.index) {
            _nodes[inode].AddParent(new_particle_index);
            particle.AddChild(inode);
        } else if (particle.genPartIdxMother == _nodes[inode].index) {
            _nodes[inode].AddChild(new_particle_index);
            particle.AddParent(inode);
        }
    }

    _nodes.push_back(particle);
    if (particle.GetParent() == -1) {
        _heads.push_back(&_nodes.back());
    }
    return &_nodes.back();
}

std::vector<Particle*> GenParticleTree::GetChildren(Particle* particle){
    std::vector<Particle*> out;
    int childIdx;
    for (int i = 0; i < particle->childIndex.size(); i++) {
        childIdx = particle->childIndex[i];
        out.push_back(&_nodes[childIdx]);
    }
    return out;
}
Particle* GenParticleTree::GetParent(Particle* particle) {
    if (_nodes.size() > particle->GetParent()){
        return &_nodes[particle->GetParent()];
    } else {
        return &_noneParticle;
    }   
}
bool GenParticleTree::_matchParticleToString(Particle* particle, std::string string){
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
        if (std::abs(particle->pdgId) == std::stoi(string)) {
            out = true;
        } else {out = false;}
    } else {
        if (Pythonic::InList((int)std::abs(particle->pdgId), pdgIds)) {
            out = true;
        } else {out = false;}
    }

    return out;
}
std::vector<Particle*> GenParticleTree::_runChain(Particle* node, std::vector<std::string> chain) {
    std::vector<Particle*> nodechain {node};
    Particle* parent = GetParent(node);
    std::vector<std::string> chain_minus_first = {chain.begin()+1,chain.end()};
    
    if (chain.size() == 0) {
        return nodechain;
    } else if (parent->flag == false) {
        nodechain.push_back(&_noneParticle);
    } else if (_matchParticleToString(parent, chain.at(0))) {
        Pythonic::Extend(nodechain, _runChain(parent,chain_minus_first));
    } else if (parent->pdgId == node->pdgId) {
        Pythonic::Extend(nodechain, _runChain(parent, chain));
    } else {
        nodechain.push_back(&_noneParticle);
    }

    return nodechain;
}
std::vector<std::vector<Particle*>> GenParticleTree::FindChain(std::string chainstring) {
    std::vector<std::string> reveresed_chain = Pythonic::Split(chainstring,'>');
    std::reverse(reveresed_chain.begin(), reveresed_chain.end());

    std::vector<std::string> reveresed_chain_minus_first = {reveresed_chain.begin()+1,reveresed_chain.end()};

    std::vector<Particle*> chain_result;
    std::vector<std::vector<Particle*>> out;

    for (size_t inode = 0; inode < _nodes.size(); inode++) {
        Particle* n = &_nodes[inode];
        if (_matchParticleToString(n, reveresed_chain.at(0))) {
            chain_result = _runChain(n,reveresed_chain_minus_first);
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