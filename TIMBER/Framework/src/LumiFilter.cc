#include "../include/LumiFilter.h"

LumiFilter::LumiFilter(std::string filename) {
    boost::property_tree::read_json(filename, ptree);
}

LumiFilter::LumiFilter(int year){
    if (year == 17 or year == 2017) {
        boost::property_tree::read_json(std::getenv("TIMBERPATH")+std::string("TIMBER/data/LumiJSON/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt"), ptree);
    } else if (year == 18 or year == 2018) {
        boost::property_tree::read_json(std::getenv("TIMBERPATH")+std::string("TIMBER/data/LumiJSON/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt"), ptree);
    } else {
        std::cout << "Year " << year << " not supported by LumiFilter" << std::endl;
        throw;
    }
}

LumiFilter::~LumiFilter() {
}

bool LumiFilter::eval(unsigned int run, unsigned int lumi) {
    bool out = false;
    for ( const auto& runEntry : ptree ) {
        if (std::stoul(runEntry.first) == run) {
            for ( const auto& lrEntry : runEntry.second ) {
                const auto lrNd = lrEntry.second;
                lumStart = std::stoul(lrNd.begin()->second.data());
                lumEnd = std::stoul((++lrNd.begin())->second.data());
                if ((lumi < lumEnd) && (lumi > lumStart)) {
                    out = true;
                }
            }
        }
    }
    return out;
}