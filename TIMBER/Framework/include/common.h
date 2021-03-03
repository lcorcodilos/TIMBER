#ifndef _TIMBER_COMMON
#define _TIMBER_COMMON
#ifndef _STRUCT_TIMESPEC
#define _STRUCT_TIMESPEC 1
#endif

#include "libarchive/include/archive.h"
#include "libarchive/include/archive_entry.h"
#include <fstream>
#include <string>
#include <iostream>
#include <sstream>
#include <boost/filesystem.hpp>

#include <cmath>
#include <cstdlib>
#include <ROOT/RVec.hxx>
#include <TMath.h>
#include <Math/GenVector/LorentzVector.h>
#include <Math/GenVector/PtEtaPhiM4D.h>
#include <Math/Vector4Dfwd.h>

using namespace ROOT::VecOps;
/**
 * @namespace hardware
 * @brief Namespace for common physics functions.
 */
namespace hardware {  
    /**
     * @brief Calculate the difference in \f$\phi\f$.
     * 
     * @param phi1 
     * @param phi2 
     * @return float Difference in \f$\phi\f$.
     */
    float DeltaPhi(float phi1,float phi2);
    /**
     * @brief Calculate \f$\Delta R\f$ between two vectors.
     * 
     * @param v1 
     * @param v2 
     * @return float 
     */
    float DeltaR(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2);
    /**
     * @brief Calculate \f$\Delta R\f$ between two objects.
     * 
     * @param in1 
     * @param in2 
     * @return float 
     */
    template<class T1, class T2>
    float DeltaR(T1 in1, T2 in2) {
        ROOT::Math::PtEtaPhiMVector v1(in1.pt, in1.eta, in1.phi, in1.mass);
        ROOT::Math::PtEtaPhiMVector v2(in2.pt, in2.eta, in2.phi, in2.mass);
        float deta = v1.Eta()-v2.Eta();
        float dphi = DeltaPhi(v1.Phi(),v2.Phi());
        return sqrt(deta*deta+dphi*dphi);
    }
    /**
     * @brief Create a ROOT::Math::PtEtaPhiMVector.
     * 
     * @param pt 
     * @param eta 
     * @param phi 
     * @param m 
     * @return ROOT::Math::PtEtaPhiMVector 
     */
    ROOT::Math::PtEtaPhiMVector TLvector(float pt,float eta,float phi,float m);
    /**
     * @brief Create a vector of ROOT::Math::PtEtaPhiMVectors.
     * 
     * @param pt 
     * @param eta 
     * @param phi 
     * @param m 
     * @return RVec<ROOT::Math::PtEtaPhiMVector> 
     */
    RVec<ROOT::Math::PtEtaPhiMVector> TLvector(RVec<float> pt,RVec<float> eta,RVec<float> phi,RVec<float> m);
    /**
     * @brief Create a ROOT::Math::PtEtaPhiMVectors.
     * 
     * @param obj
     * @return ROOT::Math::PtEtaPhiMVector
     */
    template<class T>
    ROOT::Math::PtEtaPhiMVector TLvector(T obj) {
        ROOT::Math::PtEtaPhiMVector v (obj.pt, obj.eta, obj.phi, obj.mass);
        return v;
    }
    /**
     * @brief Create a vector of ROOT::Math::PtEtaPhiMVectors.
     * 
     * @param objs 
     * @return RVec<ROOT::Math::PtEtaPhiMVector> 
     */
    template<class T>
    RVec<ROOT::Math::PtEtaPhiMVector> TLvector(RVec<T> objs) {
        RVec<ROOT::Math::PtEtaPhiMVector> vs;
        vs.reserve(objs.size());
        for (size_t i = 0; i < objs.size(); i++) {
            vs.emplace_back(objs[i].pt, objs[i].eta, objs[i].phi, objs[i].mass);
        }
        return vs;
    }

    /**
     * @brief Calculate the transverse mass from MET \f$p_T\f$ and \f$\eta\f$
     * and an object's \f$p_T\f$ and \f$\eta\f$.
     * 
     * @param MET_pt 
     * @param obj_pt 
     * @param MET_phi 
     * @param obj_phi 
     * @return float 
     */
    float transverseMass(float MET_pt, float obj_pt, float MET_phi, float obj_phi);

    /**
     * @brief Calculates the invariant mass of a vector of Lorentz vectors
     * (ROOT::Math::PtEtaPhiMVector). Note that this is an alternative
     * to [ROOT::VecOps::InvariantMasses()](https://root.cern/doc/master/namespaceROOT_1_1VecOps.html#a2c531eae910edad48bbf7319cc6d7e58)
     * which does not need the intermediate Lorentz vector.
     * 
     * @param vects 
     * @return double 
     */
    double invariantMass(RVec<ROOT::Math::PtEtaPhiMVector> vects);
}

/**
 * @brief Streams a tgz file (tarname) and searches for internalFile
 * within the tgz. Returns a string of the internalFile contents.
 * 
 * @param tarname 
 * @param internalFile 
 * @return std::string 
 */
std::string ReadTarFile(std::string tarname, std::string internalFile);

/**
 * @brief Creates a temporary directory that is destroyed on delete.
 */
class TempDir {
    private:
        boost::filesystem::path path;

    public:
        /**
         * @brief Construct a new Temp Dir object
         * 
         */
        TempDir();
        /**
         * @brief Destroy the Temp Dir object
         * 
         */
        ~TempDir();
        /**
         * @brief Write a string (in) to a file (filename) within the 
         * temporary directory.
         * 
         * @param filename 
         * @param in 
         * @return std::string 
         */
        std::string Write(std::string filename, std::string in);
};
#endif