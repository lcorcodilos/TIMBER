#include <ROOT/RVec.hxx>

class Wtag_SF {
    /**
     * @brief C++ class to access scale factors associated with tau21+mass
     * based W tagging. More details provided at [https://twiki.cern.ch/twiki/bin/view/CMS/JetWtagging](https://twiki.cern.ch/twiki/bin/view/CMS/JetWtagging)
     * 
     */
    private:
        int _year;
        float _HP, _HPunc, _LP, _LPunc;
    public:
        /**
         * @brief Construct a new Wtag_SF object
         * 
         * @param year 2016, 2017, 2018
         */
        Wtag_SF(int year);
        ~Wtag_SF(){};
        /**
         * @brief Get the scale factor for a given tau21 value.
         * 
         * @param tau21 
         * @return std::vector<float> Absolute (not relative) {nominal, up, down}
         */
        ROOT::VecOps::RVec<float> eval(float tau21);
};