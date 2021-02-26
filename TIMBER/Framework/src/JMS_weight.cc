#include "../include/JMS_weight.h"

std::vector<float> JMS_weight::eval(int year){
	return this->jmsTable[year];
} 