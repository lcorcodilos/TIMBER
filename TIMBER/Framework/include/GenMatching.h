#include <map>
#include <algorithm>
#include <numeric>
#include <math.h>
#include <cstdlib>
#include "Collection.h"
#include "Pythonic.h"
#include "Math/Vector4Dfwd.h"
#include "Math/VectorUtil.h"

using namespace ROOT::VecOps;
using LVector = ROOT::Math::PtEtaPhiMVector;

/**Unwraps an integer to check for bitwise flags.
 * Checks if the bit of a number is true or false.
 * @param bit Bit to check.
 * @param number Number to check.
 * 
 * @return Bool of whether the bit in the number is 0 or 1 */
bool BitChecker(const int &bit, int &number){
    int result = number & (1 << bit);

    if (result > 0) {return true;}
    else {return false;}
}

/**Map of the PDG ID values to the particle names.
 * used for plotting decay structure. */
static const std::map <int, std::string> PDGIds {
    {1,"d"}, {2,"u"}, {3,"s"}, {4,"c"}, {5,"b"}, {6,"t"},
    {11,"e"}, {12,"nu_e"}, {13,"mu"}, {14,"nu_mu"},{ 15,"tau"},
    {16,"nu_tau"}, {21,"g"}, {22,"photon"}, {23,"Z"}, {24,"W"}, {25,"h"}
};

/**Converts flag name to the corresponding bit in the
 * value for statusFlags branch. */
static const std::map <std::string, int> GenParticleStatusFlags {
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

/** @class Particle
 * @brief Stores identifying features of a particle
 * in the GenPart collection.
 */
class Particle {
    public:
        bool flag = true; /**< Should always be true unless we need to return a None-like particle */
        int index; /**< Index in collection */
        int* pdgId; /**< PDG ID of particle */
        int* status; /**< Pythia status of particle */
        std::map <std::string, int> statusFlags; /**< Map of status flags for set gen particle  */
        int parentIndex; /**< Parent index  */
        std::vector<int> childIndex; /**< Children indices */
        LVector vect; /**< Lorentz vector */
        Particle(){};
        /**
         * @brief Add parent index to track.
         * 
         * @param idx Parent index
         */
        void AddParent(int idx){
            parentIndex = idx;
        }
        /**
         * @brief Add child index to track.
         * 
         * @param idx Child index
         */
        void AddChild(int idx){
            childIndex.push_back(idx);
        }
        /**
         * @brief Calculate DeltaR between this and input vector
         * 
         * @param input_vector 
         * @return float 
         */
        float DeltaR(LVector input_vector);
};

/**Calculates \f$\Delta R\f$ between current particle and input vector.
 * @param input_vector The vector to compare against the current particle. 
 * @return \f$\Delta R\f$ value. */
float Particle::DeltaR(LVector input_vector) {
    return ROOT::Math::VectorUtil::DeltaR(vect,input_vector);
};

/**@class GenParticleTree
 * @brief Constructs tree by adding particles.
 * Establish relationships between particles (parent, child)
 * and allows you to search for a chain of decays. */
class GenParticleTree
{
    private:
        Collection GenParts;
        std::vector<Particle*> nodes;
        std::vector<Particle*> heads;

        bool MatchParticleToString(Particle* particle, std::string string);
        std::vector<Particle*> RunChain(Particle* node, std::vector<std::string> chain);

        std::vector<int> StoredIndexes();
        Particle NoneParticle;

    public:
        GenParticleTree(){
            NoneParticle.flag = false;
        };
        /**
         * @brief Add particle to tree.
         * 
         * @param particle 
         */
        void AddParticle(Particle* particle);
        /**
         * @brief Get the list of particle objects.
         * 
         * @return std::vector<Particle*> 
         */
        std::vector<Particle*> GetParticles() {return nodes;}
        /**
         * @brief Get the list of child particles for a given particle in the tree.
         * 
         * @param particle 
         * @return std::vector<Particle*> 
         */
        std::vector<Particle*> GetChildren(Particle* particle);
        /**
         * @brief Get the parent of the given particle in the tree.
         * 
         * @param particle 
         * @return Particle* 
         */
        Particle* GetParent(Particle* particle);
        /**
         * @brief Find a chain of decays in the tree.
         * 
         * @param chainstring 
         * @return std::vector<std::vector<Particle*>> 
         */
        std::vector<std::vector<Particle*>> FindChain(std::string chainstring);
};

std::vector<int> GenParticleTree::StoredIndexes(){
    std::vector<int> current_idxs {};
    for (int i = 0; i < nodes.size(); i++) {
        current_idxs.push_back(nodes.at(i)->index);
    }
    return current_idxs;
}

void GenParticleTree::AddParticle(Particle* particle) {
    Particle* staged_node = particle;

    // First check if current heads don't have new parents and 
    // remove them from heads if they do
    std::vector<int> heads_to_delete {};
    for (int i = 0; i < heads.size(); i++) {
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
    if (InList(staged_node->parentIndex, indexes)) {
        heads.push_back(staged_node);
        nodes.push_back(staged_node);
    } else {
        for (int inode = 0; inode < nodes.size(); inode++) {
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
    for (int i = 0; i < particle->childIndex.size(); i++) {
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
    if (InString(":",string)) {
        int startId = std::stoi( string.substr(0,string.find(':')) );
        int stopId  = std::stoi( string.substr(1,string.find(':')) );
        pdgIds = range(startId, stopId);
    } else if (InString(",",string)) {
        auto splits = split(string,',');
        for (int istr = 0; istr < splits.size(); istr++) {
            pdgIds.push_back( std::stoi(splits.at(istr)) );
        }
    }

    bool out;
    if (pdgIds.size() == 0) {
        if (std::abs(*particle->pdgId) == std::stoi(string)) {
            out = true;
        } else {out = false;}
    } else {
        if (InList(std::abs(*particle->pdgId), pdgIds)) {
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
        Extend(nodechain, RunChain(parent,chain_minus_first));
    } else if (parent->pdgId == node->pdgId) {
        Extend(nodechain, RunChain(parent, chain));
    } else {
        nodechain.push_back(&NoneParticle);
    }

    return nodechain;
}

std::vector<std::vector<Particle*>> GenParticleTree::FindChain(std::string chainstring) {
    std::vector<std::string> reveresed_chain = split(chainstring,'>');
    std::reverse(reveresed_chain.begin(), reveresed_chain.end());

    std::vector<std::string> reveresed_chain_minus_first = {reveresed_chain.begin()+1,reveresed_chain.end()};

    std::vector<Particle*> chain_result;
    std::vector<std::vector<Particle*>> out;

    for (int inode = 0; inode < nodes.size(); inode++) {
        Particle* n = nodes[inode];
        if (MatchParticleToString(n, reveresed_chain.at(0))) {
            chain_result = RunChain(n,reveresed_chain_minus_first);
            bool no_NoneParticle = true;
            for (int icr = 0; icr < chain_result.size(); icr++) {
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

/**@class GenParticleObjs
 * @brief Object that stores and manipulates the information for gen particles.
 * Stores all gen particles in the event and member functions can be used to
 * access the gen particles by index. */
class GenParticleObjs {
    private:
        Collection GenPartCollection; /** Struct holding maps of values */

        /**
         * @brief Sets the status flags for the current particle.
         * Called by \ref SetIndex. */
        void SetStatusFlags(int particleIndex);

    public:
        /**
         * @brief Construct a new Gen Particle object
         * 
         * @param in_pt Input \f$p_T\f$
         * @param in_eta Input \f$eta\f$
         * @param in_phi Input \f$phi\f$
         * @param in_m Input mass
         * @param in_pdgId Input PDG ID
         * @param in_status Input status
         * @param in_statusFlags Input status flags
         * @param in_genPartIdxMother Input mother index
         */
        GenParticleObjs(RVec<float> in_pt, 
                        RVec<float> in_eta, RVec<float> in_phi, 
                        RVec<float> in_m, RVec<int> in_pdgId, 
                        RVec<int> in_status, RVec<int> in_statusFlags, 
                        RVec<int> in_genPartIdxMother);
        /**
         * @brief Construct a new Gen Particle object
         * 
         * @param genParts @ref Collection object filled with GenPart branches from NanoAOD.
         */
        GenParticleObjs(Collection genParts);   

        Particle particle; /**< the current particle object queued for access*/
        /**
         * @brief Compares GenPart object to a provided vector.
         * 
         * @param vect The vector to compare against the current particle. 
         * @return std::map< std::string, bool> Map with keys "sameHemisphere" (phi<pi), "deltaR" 
         * (deltaR < 0.8), "deltaM" (|delta m|/m_gen < 0.05) which  all return bools.
         */
        std::map< std::string, bool> CompareToVector(LVector vect);
        /**
         * @brief Sets the index of the lookup particle 
         * 
         * @param idx The index in the collection 
         * @return Particle 
         */
        Particle SetIndex(int idx);   
        /**Returns the bool for the flag name provided
         * @param  flagName
         * @return int Status flag.
         */
        int GetStatusFlag(std::string flagName);
};

/**Constructor which takes in all info from the GenPart collection in NanoAOD 
 * Just assigns the inputs to internal variables.
 * @param in_pt \f$ p_{T} \f$
 * @param in_eta \f$ \eta \f$
 * @param in_phi \f$ \phi \f$
 * @param in_m \f$ m \f$
 * @param in_pdgId PDG ID
 * @param in_status Pythia status
 * @param in_statusFlags Status flags
 * @param in_genPartIdxMother Mother indices
 * */
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
    for (auto it = GenParticleStatusFlags.begin(); it != GenParticleStatusFlags.end(); ++it) {
        particle.statusFlags[it->first] = BitChecker(it->second, GenPartCollection.RVecInt["statusFlags"]->at(particleIndex));
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