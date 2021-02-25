#ifndef _TIMBER_COMMON
#define _TIMBER_COMMON

#include "TIMBER/bin/libarchive/include/archive.h"
#include "TIMBER/bin/libarchive/include/archive_entry.h"
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
    float DeltaPhi(float phi1,float phi2) {
        float result = phi1 - phi2;
        while (result > TMath::Pi()) result -= 2*TMath::Pi();
        while (result <= -TMath::Pi()) result += 2*TMath::Pi();
        return result;
    }
    /**
     * @brief Calculate \f$\Delta R\f$ between two vectors.
     * 
     * @param v1 
     * @param v2 
     * @return float 
     */
    float DeltaR(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2) {
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
    ROOT::Math::PtEtaPhiMVector TLvector(float pt,float eta,float phi,float m) {
        ROOT::Math::PtEtaPhiMVector v(pt,eta,phi,m);
        return v;
    }
    /**
     * @brief Create a vector of ROOT::Math::PtEtaPhiMVectors.
     * 
     * @param pt 
     * @param eta 
     * @param phi 
     * @param m 
     * @return RVec<ROOT::Math::PtEtaPhiMVector> 
     */
    RVec<ROOT::Math::PtEtaPhiMVector> TLvector(RVec<float> pt,RVec<float> eta,RVec<float> phi,RVec<float> m) {
        RVec<ROOT::Math::PtEtaPhiMVector> vs;
        for (size_t i = 0; i < pt.size(); i++) {
            ROOT::Math::PtEtaPhiMVector v(pt[i],eta[i],phi[i],m[i]);
            vs.push_back(v);
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
    float transverseMass(float MET_pt, float obj_pt, float MET_phi, float obj_phi) {
        return sqrt(2.0*MET_pt*obj_pt-(1-cos(DeltaPhi(MET_phi,obj_phi))));
    }

    /**
     * @brief Calculates the invariant mass of a vector of Lorentz vectors
     * (ROOT::Math::PtEtaPhiMVector). Note that this is an alternative
     * to [ROOT::VecOps::InvariantMasses()](https://root.cern/doc/master/namespaceROOT_1_1VecOps.html#a2c531eae910edad48bbf7319cc6d7e58)
     * which does not need the intermediate Lorentz vector.
     * 
     * @param vects 
     * @return double 
     */
    double invariantMass(RVec<ROOT::Math::PtEtaPhiMVector> vects) {
        ROOT::Math::PtEtaPhiMVector sum;
        sum.SetCoordinates(0,0,0,0);
        for (size_t i = 0; i < vects.size(); i++) {
            sum = sum + vects[i];
        }
        return sum.M();
    }

    // std::pair<int,float> closest(obj, collection, presel=lambda x, y: True):
    //     ret = None
    //     drMin = 999
    //     for x in collection:
    //         if not presel(obj, x):
    //             continue
    //         dr = deltaR(obj, x)
    //         if dr < drMin:
    //             ret = x
    //             drMin = dr
    //     return (ret, drMin)


    // def matchObjectCollection(objs,
    //                         collection,
    //                         dRmax=0.4,
    //                         presel=lambda x, y: True):
    //     pairs = {}
    //     if len(objs) == 0:
    //         return pairs
    //     if len(collection) == 0:
    //         return dict(list(zip(objs, [None] * len(objs))))
    //     for obj in objs:
    //         (bm, dR) = closest(obj,
    //                         [mobj for mobj in collection if presel(obj, mobj)])
    //         if dR < dRmax:
    //             pairs[obj] = bm
    //         else:
    //             pairs[obj] = None
    //     return pairs


    // def matchObjectCollectionMultiple(
    //         objs,
    //         collection,
    //         dRmax=0.4,
    //         presel=lambda x, y: True
    // ):
    //     pairs = {}
    //     if len(objs) == 0:
    //         return pairs
    //     if len(collection) == 0:
    //         return dict(list(zip(objs, [None] * len(objs))))
    //     for obj in objs:
    //         matched = []
    //         for c in collection:
    //             if presel(obj, c) and deltaR(obj, c) < dRmax:
    //                 matched.append(c)
    //         pairs[obj] = matched
    //     return pairs
}

std::string ReadTarFile(std::string tarname, std::string internalFile) {
    struct archive *_arch;
    struct archive_entry *_entry;
    const void *buff;
    int64_t offset;
    size_t size;
    std::stringstream outstream;
    std::string out;
    int code;
    // Open archive
    _arch = archive_read_new();
    archive_read_support_filter_all(_arch);
    archive_read_support_format_all(_arch);
    code = archive_read_open_filename(_arch, tarname.c_str(), 10240); // Note 1
    if (code != ARCHIVE_OK)
        throw "Not able to open archive `"+tarname+"`.";
    // Search for file in archive and return
    while (archive_read_next_header(_arch, &_entry) == ARCHIVE_OK) {
        if (std::string(archive_entry_pathname(_entry)) == internalFile) {
            archive_read_data_block(_arch, &buff, &size, &offset);
            outstream.write((char*)buff, size);
            out = outstream.str();
            break;
        }
    }

    archive_read_free(_arch);
    return out;
}

class TempDir {
    private:
        boost::filesystem::path path;

    public:
        TempDir(){
            path = boost::filesystem::temp_directory_path();
            boost::filesystem::create_directories(path);
        };
        ~TempDir(){
            boost::filesystem::remove(path);
        };

        std::string Write(std::string filename, std::string in) {
            std::ofstream out(filename);
            out << in;
            out.close();
            std::string finalpath (path.string()+filename); 
            return finalpath;
        };

};

#endif