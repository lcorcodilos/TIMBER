CC=gcc
INCLUDE=-I/usr/include/ -I bin/ -I./ `root-config --cflags --ldflags --glibs` -I/usr/include/
LIBS=-lstdc++ -l boost_wserialization -l boost_filesystem -L bin/libarchive/lib/ -Wl,-rpath=bin/libarchive/lib/ -l archive
CFLAGS=-g -Wno-attributes -fPIC -c
CVMFS=/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/cms/cmssw/$(CMSSW_VERSION)
CMSSW=-I$(CVMFS)/src -I/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/boost/1.72.0-bcolbf/include -L/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/boost/1.72.0-bcolbf/lib -L$(CVMFS)/lib/$(SCRAM_ARCH)

SOURCE_DIR=TIMBER/Framework/src/
HEADER_DIR=TIMBER/Framework/include/
BIN_DIR=bin/libtimber/

CPP_FILES=$(wildcard $(SOURCE_DIR)*.cc TIMBER/Framework/src/ext/*.cpp)
HEADERS=$(CPP_FILES:$(SOURCE_DIR)%.cc=$(HEADER_DIR)%.h)

JME_FILES=JetSmearer.cc JetRecalibrator.cc JMR_weight.cc JER_weight.cc JES_weight.cc JMS_weight.cc JME_common.cc
JME_FILES:=$(JME_FILES:%.cc=$(SOURCE_DIR)%.cc)
ifndef CMSSW_VERSION
	CPP_FILES:=$(filter-out $(JME_FILES), $(CPP_FILES))
else
	CMSSW:=$(CMSSW) -l CondFormatsJetMETObjects -l JetMETCorrectionsModules
endif

O_FILES=$(CPP_FILES:$(SOURCE_DIR)%.cc=$(BIN_DIR)%.o)

.PHONY: all clean
.DEFAULT: all

all: libtimber

libtimber: $(O_FILES)
	$(CC) -shared $(CMSSW) $(INCLUDE) $(LIBS) -o $(BIN_DIR)libtimber.so $(O_FILES)
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)%.o: $(SOURCE_DIR)%.cc | $(BIN_DIR)
	$(CC) $(CFLAGS) $(CMSSW) $(INCLUDE) $(LIBS) $< -o $@

clean:
	- rm -rf bin/libtimber
