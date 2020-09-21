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
}