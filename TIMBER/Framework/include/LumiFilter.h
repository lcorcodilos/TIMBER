#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>
#include "TIMBER/Framework/include/Pythonic.h"

/** @class LumiFilter
 * @brief Tool to filter luminosity block/run based on golden JSONs.
 * Golden JSONs are provided in TIMBER but a custom one can be 
 * provided. 
 */
class LumiFilter {
    private:
        boost::property_tree::ptree ptree;
        unsigned int lumStart;
        unsigned int lumEnd;

    public:
        /**
         * @brief Construct a new Lumi Filter object with a custom json file name
         * 
         * @param filename 
         */
        LumiFilter(std::string filename);
        /**
         * @brief Construct a new Lumi Filter object for a given year.
         * Supports formatting as `2017` or `17`. 2016 not needed currently.
         * 
         * @param year 
         */
        LumiFilter(int year);
        ~LumiFilter();
        /**
         * @brief Evaluate whether the given run and lumi pass the 
         * luminosity JSON filter.
         * 
         * @param run 
         * @param lumi 
         * @return bool 
         */
        bool eval(unsigned int run, unsigned int lumi);
};

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