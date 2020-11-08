#include <map>
#include <string>
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;
using namespace std;

/** Structure to store maps of the various types of objects
 * in a collection. UChar not considered.
 * Use by building each map as <branchName, branchValue> and
 * then assigning to the correct struct member. */
struct Collection {
    map<string,int*> Int;
    map<string,bool*> Bool;
    map<string,RVec<float>*> RVecFloat;
    map<string,RVec<int>*> RVecInt;
};

