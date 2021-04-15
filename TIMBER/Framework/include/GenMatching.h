#ifndef _TIMBER_GENMATCHING
#define _TIMBER_GENMATCHING
#include <map>
#include <algorithm>
#include <numeric>
#include <math.h>
#include <cstdlib>
#include "common.h"
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

using namespace ROOT::VecOps;
using LVector = ROOT::Math::PtEtaPhiMVector;

namespace GenMatching {
    /** @brief C++ function. Unwraps an integer to check for bitwise flags.
     * Checks if the bit of a number is true or false.
     * 
     * @param bit Bit to check.
     * @param number Number to check.
     * 
     * @return Bool of whether the bit in the number is 0 or 1 */
    bool BitChecker(const int &bit, int &number);

    /** @brief C++ map of the PDG ID values to the particle names.
     * used for plotting decay structure. */
    extern std::map <int, std::string> PDGIds;

    /** @brief C++ map. Converts flag name to the corresponding bit in the
     * value for statusFlags branch. */
    extern std::map <std::string, int> GenParticleStatusFlags;
}

/** @class Particle
 * @brief C++ class. Stores identifying features of a particle
 * in the GenPart collection.
 */
class Particle {
    public:
        bool flag = true; /**< Should always be true unless we need to return a None-like particle */
        int index; /**< Index in collection */
        std::map <std::string, int> statusFlags; /**< Map of status flags for set gen particle  */
        int parentIndex; /**< Parent index in GenParticleTree */
        std::vector<int> childIndex; /**< Children indices in GenParticleTree */
        LVector vect; /**< Lorentz vector */
        int genPartIdxMother; /**< Index of the mother particle in NanoAOD*/
        int pdgId; /**< PDG id*/
        int status; /**< Particle status*/
        /**
         * @brief Construct a new Particle object
         */
        Particle();
        /**
         * @brief Construct a new Particle object with TIMBER collection struct as input
         * 
         * @tparam T 
         * @param i index
         * @param p struct
         */
        template <class T>
        Particle(int i, T p) : 
            vect(LVector(p.pt, p.eta, p.phi, p.mass)), index(i), genPartIdxMother(p.genPartIdxMother),
            pdgId(p.pdgId), status(p.status) {
                SetStatusFlags(p.statusFlags);
        };
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
         * @brief Return the index of the parent.
         * 
         * @return int 
         */
        int GetParent();
        /**
         * @brief Get vector of indices of the children.
         * 
         * @return std::vector<int> 
         */
        std::vector<int> GetChild();
        /**
         * @brief Calculate \f$\Delta R\f$ between current particle and input vector.
         * 
         * @param input_vector The vector to compare against the current particle. 
         * @return float \f$\Delta R\f$ value
         */
        float DeltaR(LVector input_vector);
        /**
         * @brief Set the internal status flags map
         * @param flags Integer from NanoAOD
         */
        void SetStatusFlags(int flags);
        /** @brief Returns the bool for the flag name provided
         * @param flagName
         * @return int Status flag.
         */
        int GetStatusFlag(std::string flagName);
        /**
         * @brief Compares particle to a provided vector.
         * 
         * @param vect The vector to compare against the current particle. 
         * @return std::map< std::string, bool> Map with keys "sameHemisphere" (phi<pi/2), "deltaR" 
         * (deltaR < 0.8), "deltaM" (|delta m|/m_gen < 0.05) which all return bools.
         */
        std::map< std::string, bool> CompareToVector(LVector vect);
};


/** @class GenParticleTree
 *  @brief C++ class. Constructs tree by adding particles.
 *  Establish relationships between particles (parent, child)
 *  and allows you to search for a chain of decays.
 */
class GenParticleTree
{
    private:
        std::vector<Particle> _nodes;
        std::vector<Particle*> _heads;
        // std::vector<int> _storedIndexes;

        bool _matchParticleToString(Particle* particle, std::string string);
        std::vector<Particle*> _runChain(Particle* node, std::vector<std::string> chain);

        Particle _noneParticle;

    public:
        /**
         * @brief Construct a new GenParticleTree object
         * 
         * @param nParticles 
         */
        GenParticleTree(int nParticles);
        /**
         * @brief Add particle to tree.
         * 
         * @param particle 
         */
        Particle* AddParticle(Particle particle);
        /**
         * @brief Add particle to tree.
         * 
         * @tparam T GenPartStruct
         * @param index Index of the particle in the GenPart collection
         * @param p A GenPartStruct from TIMBER
         * @return Particle* 
         */
        template <class T>
        Particle* AddParticle(int index, T p) {
            Particle particle(index, p);
            return AddParticle(particle);
        }
        /**
         * @brief Get the list of particle objects.
         * 
         * @return std::vector<Particle*> 
         */
        std::vector<Particle*> GetParticles() {
            std::vector<Particle*> out;
            for (int inode = 0; inode<_nodes.size(); inode++) {
                out.push_back(&_nodes[inode]);
            }
            return out;
        }
        /**
         * @brief Get the list of child particles for a given particle in the tree.
         * 
         * @param particle 
         * @return std::vector<Particle>* 
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
#endif