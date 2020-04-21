#define _USE_MATH_DEFINES

#include <cmath>
#include "ROOT/RVec.hxx"
using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;
//return two ak4 cnadidates that are properly selected by hemispherize funtion for 2+1
//Compares ak4 jets against leading ak8 and looks for any in opposite hemisphere
//First find the highest pt ak8 jet with mass > 40 geV
namespace analyzer {
     RVec<int> Hemispherize(rvec_f FJpt, rvec_f FJeta, rvec_f FJphi, rvec_f FJmass, unsigned int FJnjets, rvec_f Jpt, rvec_f Jeta, rvec_f Jphi, rvec_f Jmass, unsigned int Jnjets, rvec_f btagDeepB){
        //First find the highest pt ak8 jet with mass > 40 geV
        RVec<int> fail = {0,0}; //this is used for if the hemispherize fails so we can filter the event

        auto candidateFatJetIndex = -1;
        for (unsigned int i =0; i<FJnjets; i++){

            if (FJmass[i] > 40) {
                candidateFatJetIndex = i;
                break;
            }
        }
        if (candidateFatJetIndex == -1){
            return fail;
        }
        //cout << "fat jet found " << candidateFatJetIndex << endl;
        RVec<int> candidateJetIndices;
        //Check the AK4s against the AK8

        if (Jnjets < 1){
            //cout << "No jets available" << endl;
            return fail;
        }//else{
            //cout << Jnjets << " jets are available" << endl;
        //}

        for (unsigned int ijet = 0; ijet<Jnjets; ijet++){
            //cout << "ijet = " << ijet+1 << " Jnjets = " << Jnjets << endl;
            if (abs(FJphi[candidateFatJetIndex]-Jphi[ijet]) > M_PI_2 ){
                candidateJetIndices.emplace_back(ijet);
                //cout << "Jet " << ijet << " passed." << endl;
            }
        }
        //cout << "number of candidate jets = " << candidateJetIndices.size() << endl;
        //If not enough jets, end it
        if (candidateJetIndices.size() < 2){
            //cout << "not enough jets" << endl;
            return fail;
        }else{//Else compare jets and find those within R of 1.5 (make pairs)
            //Compare all pairs
            RVec<RVec<size_t>> pairs_cmb = Combinations(Jpt,2);
            //cout << "Combinations made" << endl; 
            RVec<RVec<int>> passing_pair_indices;
            RVec<int> temp_pair(2);
	        int pairsSize = pairs_cmb[0].size();
            //cout << "check combinations size " << pairsSize << endl;
            if (pairsSize < 1){
                //cout << "Combinations size less than 1" << endl;
                return fail;
            }
            //cout << "start for loop" << endl;
            for (unsigned int j = 0; j < pairsSize; j++){   // this is providing pairs of indices of the candidateJetIndices list! (not the indices of the jetCollection!)
                const auto i1 = pairs_cmb[0][j];
                const auto i2 = pairs_cmb[1][j];
                //cout << "make lorentz vectors " << j << endl;
                ROOT::Math::PtEtaPhiMVector v1(Jpt[i1],Jeta[i1],Jphi[i1],Jmass[i1]);
                ROOT::Math::PtEtaPhiMVector v2(Jpt[i2],Jeta[i2],Jphi[i2],Jmass[i2]);
                if (sqrt((v1.Eta()-v2.Eta())*(v1.Eta()-v2.Eta()) + (deltaPhi(v1.Phi(),v2.Phi()))*(deltaPhi(v1.Phi(),v2.Phi()))) < 1.5){
                    // Save out collection index of those that pass
                    //cout << "pair " << j << " passes DeltaR" << endl;
                    temp_pair.emplace_back(i1);
                    temp_pair.emplace_back(i2);
                    passing_pair_indices.emplace_back(temp_pair);
                    temp_pair.clear();
                }

            }
            //cout << "end for loop" << endl;
            if (passing_pair_indices.empty()){
                //cout << "no passing pairs found" << endl;
                return fail;
            }

            //cout << "passing pairs made " << passing_pair_indices.size() << endl;
            // Check if the ak4 jets are in a larger ak8
            // If they are, pop them out of our two lists for consideration
            for (unsigned int i =0; i<FJnjets; i++){
                ROOT::Math::PtEtaPhiMVector fjetLV(FJpt[i],FJeta[i],FJphi[i],FJmass[i]);
                //cout << i << " fat jet lorentz vector made" << endl;
                for (unsigned int j =0; j < passing_pair_indices.size(); j++){
                    //cout << "begin making indices with index " << j << endl;
                    if (passing_pair_indices[j].empty()){
                        //cout << "empty vector pair values found " << endl;
                        break;
                    }
                    //cout << "checking pair indices " << passing_pair_indices[j][0] << " " << passing_pair_indices[j][1] << endl; 
                    if (passing_pair_indices[j][0] > 1000 || passing_pair_indices[j][1] > 1000){
                        //cout << "uncaught high memory usage" << endl;
                        break;
                    }
                    const auto i1 = passing_pair_indices[j][0];
                    const auto i2 = passing_pair_indices[j][1];
                    //cout << "indices booked " << i1 << " " << i2 << endl;
                    if(i2 < 0 || i1 < 0){
                        //cout << "bad index found" << endl;
                        break; 
                    }
                    ROOT::Math::PtEtaPhiMVector v1(Jpt[i1],Jeta[i1],Jphi[i1],Jmass[i1]);
                    ROOT::Math::PtEtaPhiMVector v2(Jpt[i2],Jeta[i2],Jphi[i2],Jmass[i2]);
                    //cout << j << " jet lorentz vectors made" << endl;

                    if (sqrt((fjetLV.Eta()-v1.Eta())*(fjetLV.Eta()-v1.Eta()) + (deltaPhi(fjetLV.Phi(),v1.Phi()))*(deltaPhi(fjetLV.Phi(),v1.Phi()))) < 0.8){
                        //cout << "Pair " << j << " found inside AK8 jet" << endl;
                        passing_pair_indices.erase(passing_pair_indices.begin()+i);
                        break;
                    }
                    if (sqrt((fjetLV.Eta()-v2.Eta())*(fjetLV.Eta()-v2.Eta()) + (deltaPhi(fjetLV.Phi(),v2.Phi()))*(deltaPhi(fjetLV.Phi(),v2.Phi()))) < 0.8){
                        //cout << "Pair " << j << " found inside AK8 jet" << endl;
                        passing_pair_indices.erase(passing_pair_indices.begin()+i);
                    }
                }
            }
            //cout << "candidate pairs made" << endl;
            RVec<RVec<int>> candidatePairIdx;
            RVec<int> PairIdx;
            //if STILL greater than 1 pair...
            if (passing_pair_indices.size() > 1){
                // Now pick based on summed btag values
                float btagsum = 0;
                for (int i =0; i < passing_pair_indices.size(); i++) {
		            const auto i1 = passing_pair_indices[i][0];
                    const auto i2 = passing_pair_indices[i][1];
                    float thisbtagsum = btagDeepB[i1] + btagDeepB[i2];
                    if (thisbtagsum > btagsum){
                        btagsum = thisbtagsum;
                        candidatePairIdx.emplace_back(passing_pair_indices[i]);
                    }
                }
            } else if (passing_pair_indices.size() == 1){
                candidatePairIdx.emplace_back(passing_pair_indices[0]);
            } else{
                candidatePairIdx.emplace_back(fail); 
            }
            
            if (candidatePairIdx.size() == 1){
                //cout << "final pair indices found" << endl;
                PairIdx.emplace_back(candidatePairIdx[0][0]);
                PairIdx.emplace_back(candidatePairIdx[0][1]);
                return PairIdx;
            } else{
                //cout << "no indices found" << endl;
                return fail;
            }

        }
    }
}
