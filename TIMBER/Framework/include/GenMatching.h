#ifndef _TIMBER_GENMATCHING
#define _TIMBER_GENMATCHING
#include <map>
#include <algorithm>
#include <numeric>
#include <math.h>
#include <cstdlib>
#include "Collection.h"
#include "common.h"
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

using namespace ROOT::VecOps;
using LVector = ROOT::Math::PtEtaPhiMVector;

namespace GenMatching {
    /** @brief Unwraps an integer to check for bitwise flags.
     * Checks if the bit of a number is true or false.
     * 
     * @param bit Bit to check.
     * @param number Number to check.
     * 
     * @return Bool of whether the bit in the number is 0 or 1 */
    bool BitChecker(const int &bit, int &number);

    /** @brief Map of the PDG ID values to the particle names.
     * used for plotting decay structure. */
    extern std::map <int, std::string> PDGIds;

    /** @brief Converts flag name to the corresponding bit in the
     * value for statusFlags branch. */
    extern std::map <std::string, int> GenParticleStatusFlags;
}

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
        Particle();
        /**
         * @brief Add parent index to track.
         * 
         * @param idx Parent index
         */
        void AddParent(int idx);
        /**
         * @brief Add child index to track.
         * 
         * @param idx Child index
         */
        void AddChild(int idx);
        /**
         * @brief Calculate \f$\Delta R\f$ between current particle and input vector.
         * 
         * @param input_vector The vector to compare against the current particle. 
         * @return float \f$\Delta R\f$ value
         */
        float DeltaR(LVector input_vector);
};


/** @class GenParticleTree
 *  @brief Constructs tree by adding particles.
 *  Establish relationships between particles (parent, child)
 *  and allows you to search for a chain of decays.
 */
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

/** @class GenParticleObjs
 *  @brief Object that stores and manipulates the information for gen particles.
 *  Stores all gen particles in the event and member functions can be used to
 *  access the gen particles by index.
*/
class GenParticleObjs {
    private:
        Collection GenPartCollection; /** Struct holding maps of values */

        /**
         * @brief Sets the status flags for the current particle.
         * Called by \ref SetIndex. */
        void SetStatusFlags(int particleIndex);

    public:
        /**
         * @brief Constructor which takes in all info from the GenPart collection in NanoAOD 
         * Just assigns the inputs to internal variables.
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
        /** @brief Returns the bool for the flag name provided
         * @param flagName
         * @return int Status flag.
         */
        int GetStatusFlag(std::string flagName);
};
#endif