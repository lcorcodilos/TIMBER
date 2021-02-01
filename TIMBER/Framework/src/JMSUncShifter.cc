// Requires CMSSW
#include "TIMBER/Framework/include/JMSUncShifter.h"

JMSUncShifter::JMSUncShifter(){
	this->jmsTable["2016"]={1.00, 0.9906, 1.0094};//nominal, down, up
	this->jmsTable["2017"]={0.982, 0.978, 0.986};
	this->jmsTable["2018"]={0.982, 0.978, 0.986};
}

float JMSUncShifter::shiftMsd(float mSD,std::string year,int shift){
	float jmsVal = jmsTable[year][shift];
	return mSD*jmsVal;
}