// subjet_btag
namespace analyzer {
    int subjet_btag(int subjet_idx1,int subjet_idx2, ROOT::VecOps::RVec<Float_t> subjets_csv) {
        float sj_csv1, sj_csv2;

        // std::cout << subjet_idx1 << ", " << subjet_idx2 << std::endl;

        if (subjet_idx1 > -1 || subjet_idx1 >= subjets_csv.size()) {sj_csv1 = subjets_csv[subjet_idx1];}
        else {sj_csv1 = 0;}

        if (subjet_idx2 > -1|| subjet_idx2 >= subjets_csv.size()) {sj_csv2 = subjets_csv[subjet_idx2];}
        else {sj_csv2 = 0;}

        if (sj_csv1 > 0.8484 || sj_csv2 > 0.8484) {
            // std::cout << "subjet_btag returning 1" << std::endl;
            return 1;
        } else {
            // std::cout << "subjet_btag returning 0" << std::endl;
            return 0;
        }
    }
}
