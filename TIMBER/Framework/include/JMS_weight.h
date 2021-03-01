#include <string>
#include <cstdlib>
#include <map>
#include <vector>

// CURRENTLY ONLY SUPPORTS TAU21
class JMS_weight {
    private:
        std::map< int, std::vector<float> > _jmsTable {
            {2016, {1.000, 1.0094, 0.9906} },
            {2017, {0.982, 0.986 , 0.978 } },
            {2018, {0.982, 0.986 , 0.978 } }
        };
    public:
        JMS_weight();
        ~JMS_weight(){};
        std::vector<float> eval(int year);
};