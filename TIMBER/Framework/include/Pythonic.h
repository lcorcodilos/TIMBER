#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <stdexcept>

//https://stackoverflow.com/questions/13152252/is-there-a-compact-equivalent-to-python-range-in-c-stl
template <typename IntType>
std::vector<IntType> range(IntType start, IntType stop, IntType step)
{
  if (step == IntType(0))
  {
    throw std::invalid_argument("step for range must be non-zero");
  }

  std::vector<IntType> result;
  IntType i = start;
  while ((step > 0) ? (i < stop) : (i > stop))
  {
    result.push_back(i);
    i += step;
  }

  return result;
}

template <typename IntType>
std::vector<IntType> range(IntType start, IntType stop)
{
  return range(start, stop, IntType(1));
}

template <typename IntType>
std::vector<IntType> range(IntType stop)
{
  return range(IntType(0), stop, IntType(1));
}

// Adapted from http://www.martinbroadhurst.com/how-to-split-a-string-in-c.html
std::vector<std::string> split(const std::string& str, char delim = ' ') {
    std::vector<std::string> out {};
    std::stringstream ss(str);
    std::string token;
    while (std::getline(ss, token, delim)) {
        out.push_back(token);
    }

    return out;
}

// Personal
template<typename T>
bool InList(T obj, std::vector<T> list) {
    auto pos = std::find(std::begin(list), std::end(list), obj);
    if (pos != std::end(list)){
        return true;
    } else {return false;}
}

bool InString(std::string sub, std::string main) {
    auto found = main.find(sub);
    if (found != std::string::npos){
        return true;
    } else {return false;}
}

template<typename T>
void Extend(std::vector<T> base, std::vector<T> extension) {
    for (int i = 0; i < extension.size(); i++) {
        base.push_back(extension.at(i));
    }
}