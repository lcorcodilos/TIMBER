#ifndef _TIMBER_LUMIFILTER
#define _TIMBER_LUMIFILTER
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

/** @class LumiFilter
 * @brief C++ class. Tool to filter luminosity block/run based on golden JSONs.
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
         * Supports formatting as (for example) `2017` or `17`.
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


#endif 