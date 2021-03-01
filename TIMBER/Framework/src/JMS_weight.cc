#include "../include/JMS_weight.h"

JMS_weight::JMS_weight(int year) : _jmsVals(_jmsTable[year]) {};

std::vector<float> JMS_weight::eval(){
	return this->_jmsVals;
} 