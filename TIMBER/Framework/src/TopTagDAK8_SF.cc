#include "../include/TopTagDAK8_SF.h"

TopTagDAK8_SF::TopTagDAK8_SF(int year, std::string workingpoint, bool massDecorr) {
    std::string massDecorrStr = massDecorr ? "MassDecorr" : "Nominal";
    std::string yearStr;
    if (year > 2000) {
        yearStr = std::to_string(year - 2000);
    } else {
        yearStr = std::to_string(year);
    }

    std::fstream csv_file;
    csv_file.open(_p, std::ios::in);
    if (!csv_file.is_open()) {
        std::cout << "Cannot open file " << _p << std::endl;
        throw;
    }
        
    std::string line;
    std::stringstream end_of_line;
    std::string entry_to_find ("Top, 20"+yearStr+", "+massDecorrStr+", "+workingpoint+", ");
    std::vector<float> bins_and_vals;
    while (std::getline(csv_file, line))  {
        if (line.find(entry_to_find)!=std::string::npos) {
            end_of_line << line.substr(entry_to_find.size());
            bins_and_vals = {};
            std::string entry;
            while(end_of_line.good()) {
                std::getline(end_of_line, entry, ','); //get first string delimited by comma
                bins_and_vals.push_back(std::stof(entry));
            }
            _values[{bins_and_vals[0],bins_and_vals[1]}] = {bins_and_vals[2],
                                                bins_and_vals[2]+bins_and_vals[3],
                                                bins_and_vals[2]-bins_and_vals[4] };
        }
    }
}

std::vector<float> TopTagDAK8_SF::eval(float pt) {
    std::vector<float> out = {1.0, 1.0, 1.0};
    for (auto const& entry : _values) {
        std::pair<int,int> pt_range = entry.first;
        if (pt > pt_range.first && pt < pt_range.second) {
            out = entry.second;
            break;
        }
    }
    return out;
}
