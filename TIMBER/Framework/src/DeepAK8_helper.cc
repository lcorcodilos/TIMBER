#include "../include/DeepAK8_helper.h"

DeepAK8_helper::DeepAK8_helper(std::string particle, int year, std::string workingpoint, bool massDecorr) {
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
    
    entry_to_find = particle+", 20"+yearStr+", "+massDecorrStr+", "+workingpoint+", ";
    std::vector<float> bins_and_vals(5);
    while (std::getline(csv_file, line))  {
        if (line.find(entry_to_find)!=std::string::npos) {
            bins_and_vals.clear();
            std::stringstream end_of_line;
            end_of_line << line.substr(entry_to_find.size());
            std::string entry;
            int ipiece = 0;
            while(end_of_line.good()) {
                std::getline(end_of_line, entry, ','); //get first string delimited by comma
                bins_and_vals[ipiece] = std::stof(entry);
                ipiece++;
            }
            _values.push_back({bins_and_vals[0],bins_and_vals[1],bins_and_vals[2],
                               bins_and_vals[2]+bins_and_vals[3],
                               bins_and_vals[2]-bins_and_vals[4]});
            end_of_line.str(std::string());
        }
    }
}

std::vector<float> DeepAK8_helper::eval(float pt) {
    std::vector<float> out = {};
    for (int irange = 0; irange < _values.size(); irange++) {
        std::vector<float> data = _values[irange];
        if (irange == 0 && pt < data[0]) {
            out = {1.0, 1.0, 1.0};
        } else if (irange == (_values.size()-1) && data[1] < pt) {
            out = {data[2], data[3], data[4]};
        } else if ((data[0] <= pt) && (pt < data[1])) {
            out = {data[2], data[3], data[4]};
        }
    }
    return out;
}
