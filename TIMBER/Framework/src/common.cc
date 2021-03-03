#include "../include/common.h"

float hardware::DeltaPhi(float phi1,float phi2) {
    float result = phi1 - phi2;
    while (result > TMath::Pi()) result -= 2*TMath::Pi();
    while (result <= -TMath::Pi()) result += 2*TMath::Pi();
    return result;
}

float hardware::DeltaR(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2) {
    float deta = v1.Eta()-v2.Eta();
    float dphi = DeltaPhi(v1.Phi(),v2.Phi());
    return sqrt(deta*deta+dphi*dphi);
}

ROOT::Math::PtEtaPhiMVector hardware::TLvector(float pt,float eta,float phi,float m) {
    ROOT::Math::PtEtaPhiMVector v(pt,eta,phi,m);
    return v;
}

RVec<ROOT::Math::PtEtaPhiMVector> hardware::TLvector(RVec<float> pt,RVec<float> eta,RVec<float> phi,RVec<float> m) {
    RVec<ROOT::Math::PtEtaPhiMVector> vs;
    vs.reserve(pt.size());
    for (size_t i = 0; i < pt.size(); i++) {
        vs.emplace_back(pt[i],eta[i],phi[i],m[i]);
    }
    return vs;
}
float hardware::transverseMass(float MET_pt, float obj_pt, float MET_phi, float obj_phi) {
    return sqrt(2.0*MET_pt*obj_pt-(1-cos(DeltaPhi(MET_phi,obj_phi))));
}

double hardware::invariantMass(RVec<ROOT::Math::PtEtaPhiMVector> vects) {
    ROOT::Math::PtEtaPhiMVector sum;
    sum.SetCoordinates(0,0,0,0);
    for (size_t i = 0; i < vects.size(); i++) {
        sum = sum + vects[i];
    }
    return sum.M();
}

std::vector<std::string> Pythonic::Split(const std::string& str, char delim) {
    std::vector<std::string> out {};
    std::stringstream ss(str);
    std::string token;
    while (std::getline(ss, token, delim)) {
        out.push_back(token);
    }
    return out;
}

bool Pythonic::InString(std::string sub, std::string main) {
    bool out;
    auto found = main.find(sub);
    if (found != std::string::npos){
        out = true;
    } else {out = false;}
    return out;
}

bool Pythonic::IsDir(char* dirname) {
    struct stat sb;
    bool exists;

    if (stat(dirname, &sb) == 0 && S_ISDIR(sb.st_mode)) {
        exists = true;
    } else {
        exists = false;
    }
    return exists;
}

void Pythonic::Execute(std::string cmd) {
    printf("Executing: %s",cmd.c_str());
    std::system(cmd.c_str());
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

TempDir::TempDir(){
    path = boost::filesystem::temp_directory_path();
    boost::filesystem::create_directories(path);
};
TempDir::~TempDir(){
    boost::filesystem::remove(path);
};
std::string TempDir::Write(std::string filename, std::string in) {
    std::ofstream out(filename);
    out << in;
    out.close();
    std::string finalpath (path.string()+filename); 
    return finalpath;
};