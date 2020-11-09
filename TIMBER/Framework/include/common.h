#include <ROOT/RVec.hxx>

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
        for (int i = 0; i < pt.size(); i++) {
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
        for (int i = 0; i < vects.size(); i++) {
            sum = sum + vects[i];
        }
        return sum.M();
    }
}