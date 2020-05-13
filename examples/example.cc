ROOT::VecOps::RVec<float> tau32Maker (ROOT::VecOps::RVec<float> tau3, ROOT::VecOps::RVec<float> tau2) {
    auto lamb = [](float x1, float x2) { return x1/x2; };
    auto tau32_map = ROOT::VecOps::Map(tau3, tau2, lamb);
    return tau32_map;
}

ROOT::VecOps::RVec<float> sjbtagMaker (
    ROOT::VecOps::RVec<int> sj_idx1, 
    ROOT::VecOps::RVec<int> sj_idx2, 
    ROOT::VecOps::RVec<float> subjet_btag) {
    
    auto lamb = [&subjet_btag](int idx1, int idx2) { return std::max(subjet_btag[idx1],subjet_btag[idx2]); };
    auto sjbtag_map = ROOT::VecOps::Map(sj_idx1, sj_idx2, lamb);
    return sjbtag_map;
}

