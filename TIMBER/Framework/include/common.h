#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;
namespace analyzer {   
    std::vector<float> HistLookup(TH1D* hist, float xval, float yval=0.0, float zval=0.0){
        std::vector<float> out;

        int bin = hist->FindBin(xval,yval,zval); 
        float Weight = hist->GetBinContent(bin);
        float Weightup = Weight + hist->GetBinErrorUp(bin);
        float Weightdown = Weight - hist->GetBinErrorLow(bin);
        
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }

    float deltaPhi(float phi1,float phi2) {
        float result = phi1 - phi2;
        while (result > TMath::Pi()) result -= 2*TMath::Pi();
        while (result <= -TMath::Pi()) result += 2*TMath::Pi();
        return result;
    }

    ROOT::Math::PtEtaPhiMVector TLvector(float pt,float eta,float phi,float m) {
        ROOT::Math::PtEtaPhiMVector v(pt,eta,phi,m);
        return v;
    }

    double invariantMass(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2) {
        return (v1+v2).M();
    }
    double invariantMass(int idx1, int idx2, RVec<float> pts, RVec<float> etas, RVec<float> phis, RVec<float> masses) {
        ROOT::Math::PtEtaPhiMVector v1, v2;
        v1.SetCoordinates(pts[idx1],etas[idx1],phis[idx1],masses[idx1]);
        v2.SetCoordinates(pts[idx2],etas[idx2],phis[idx2],masses[idx2]);
        return invariantMass(v1,v2);
    }

    double invariantMassThree(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2, ROOT::Math::PtEtaPhiMVector v3) {
        return (v1+v2+v3).M();
    }

    float HT(std::vector<int> pts) {
        float ht = 0.0;
        for(int pt : pts) {
            ht = ht + pt;
        }
        return ht;
    }

}