#include "../include/common.h"
#include "libarchive/include/archive.h"
#include "libarchive/include/archive_entry.h"

TFile *hardware::Open(std::string file, bool inTIMBER, const char* option){
    if (inTIMBER) {
        return new TFile((std::string(std::getenv("TIMBERPATH"))+file).c_str(),option);
    } else {
        return new TFile((file).c_str(),option);
    }
}

TH1 *hardware::LoadHist(std::string filename, std::string histname, bool inTIMBER){
    TFile *file = hardware::Open(filename, inTIMBER);
    TH1 *hist = (TH1*)file->Get(histname.c_str());
    hist->SetDirectory(0);
    file->Close();
    return hist;
}

RVec<float> hardware::HadamardProduct(RVec<float> v1, RVec<float> v2) {
    RVec<float> out;
    out.reserve(v1.size());
    for (size_t i = 0; i<v1.size(); i++) {
        out.emplace_back(v1[i]*v2[i]);
    }
    return out;
}

RVec<float> hardware::HadamardProduct(RVec<float> v1, RVec<RVec<float>> v2, int v2subindex) {
    RVec<float> out;
    out.reserve(v1.size());
    for (size_t i = 0; i<v1.size(); i++) {
        out.emplace_back(v1[i]*v2[i][v2subindex]);
    }
    return out;
}

RVec<float> hardware::MultiHadamardProduct(RVec<float> v1, RVec<RVec<float>> Multiv2) {
    RVec<float> out;
    out.reserve(v1.size());
    for (size_t i = 0; i<v1.size(); i++) {
        float val = v1[i];
        for (RVec<float>& v2 : Multiv2) {
            val *= v2[i];
        }
        out.push_back(val);
    }
    return out;
}

RVec<float> hardware::MultiHadamardProduct(RVec<float> v1, RVec<RVec<RVec<float>>> Multiv2, int v2subindex) {
    RVec<float> out;
    out.reserve(v1.size());
    for (size_t i = 0; i<v1.size(); i++) {
        float val = v1[i];
        for (RVec<RVec<float>>& v2 : Multiv2) {
            val *= v2[i][v2subindex];
        }
        out.push_back(val);
    }
    return out;
}

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
float hardware::TransverseMass(float MET_pt, float obj_pt, float MET_phi, float obj_phi) {
    return sqrt(2.0*MET_pt*obj_pt-(1-cos(DeltaPhi(MET_phi,obj_phi))));
}

double hardware::InvariantMass(RVec<ROOT::Math::PtEtaPhiMVector> vects) {
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
    int64_t offset;
    size_t size;
    std::stringstream outstream;
    std::string out = "";
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
        if (std::string(archive_entry_pathname(_entry)).find(internalFile) !=  std::string::npos) {
            void *contents;
            int entry_size = archive_entry_size(_entry);
            contents = malloc(entry_size);
            archive_read_data(_arch, contents, entry_size);
            outstream.write((char*)contents, entry_size);
            out = outstream.str();
            out.erase(out.find_last_not_of('\n') + 1);
            free(contents);
            break;
        }
    }
    archive_read_free(_arch);
    return out;
}

TempDir::TempDir() :
    _path (boost::filesystem::temp_directory_path().string()+"/"+this->Hash()+"/") {
    boost::filesystem::create_directories(_path);
};
TempDir::~TempDir(){
    std::cout << "TempDir closing..." << std::endl;
    for (auto f : _filesSaved) {
        std::cout << "\tremoving " << f << " ..." << std::endl;
        boost::filesystem::remove(f);
    }
    std::cout << "\tremoving " << _path.string() << " ..." << std::endl;
    boost::filesystem::remove(_path.string());
};
// https://stackoverflow.com/questions/440133/how-do-i-create-a-random-alpha-numeric-string-in-c/12468109#12468109
std::string TempDir::Hash(){
    int length = 10;
    auto randchar = []() -> char
    {
        const char charset[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
        const size_t max_index = (sizeof(charset) - 1);
        return charset[ rand() % max_index ];
    };
    std::string str(length,0);
    std::generate_n( str.begin(), length, randchar );
    return str;
}
std::string TempDir::Write(std::string filename, std::string in) {
    std::string finalpath = _path.string()+filename; 
    std::ofstream out(finalpath);
    // std::string in_strip = in;
    // if (in.at(in.length()-1) == '\n') {
    //     in_strip.pop_back();
    // }
    out << in;
    out.close();
    _filesSaved.push_back(finalpath);
    return finalpath;
};