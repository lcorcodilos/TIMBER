#include "../include/JMS_weight.h"

JMS_weight::JMS_weight(int year) : _jmsVals(_jmsTable[year]) {};

RVec<RVec<float>> JMS_weight::eval(size_t nFatJet){
	RVec<RVec<float>> out;
	out.reserve(nFatJet);
	for (size_t i=0; i<nFatJet; i++){
		out.push_back(this->_jmsVals);
	}
	return out;
} 