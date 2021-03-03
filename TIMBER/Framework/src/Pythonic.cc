#include "../include/Pythonic.h"

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