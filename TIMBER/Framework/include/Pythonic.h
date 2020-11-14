#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <stdexcept>

/**
 * @brief Python-like range function.
 * https://stackoverflow.com/questions/13152252/is-there-a-compact-equivalent-to-python-range-in-c-stl
 * 
 * @tparam IntType 
 * @param start Starting point, inclusive.
 * @param stop Stopping point, exclusive.
 * @param step Defaults to 1.
 * @return std::vector<IntType> Vector of range with provided step.
 */
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

/**
 * @brief Python-like range function with step 1.
 * https://stackoverflow.com/questions/13152252/is-there-a-compact-equivalent-to-python-range-in-c-stl
 * 
 * @tparam IntType 
 * @param start Starting point, inclusive.
 * @param stop Stopping point, exclusive.
 * @return std::vector<IntType> Vector of range with step of 1.
 */
template <typename IntType>
std::vector<IntType> range(IntType start, IntType stop)
{
  return range(start, stop, IntType(1));
}

/**
 * @brief Python-like range function with step 1 and start assumed to be 0.
 * https://stackoverflow.com/questions/13152252/is-there-a-compact-equivalent-to-python-range-in-c-stl
 * 
 * @tparam IntType 
 * @param start Starting point, inclusive.
 * @return std::vector<IntType> Vector of range with step of 1 and start of 0.
 */
template <typename IntType>
std::vector<IntType> range(IntType stop)
{
  return range(IntType(0), stop, IntType(1));
}

/**
 * @brief Python-like string splitter based on a delimiter.
 * 
 * Adapted from http://www.martinbroadhurst.com/how-to-split-a-string-in-c.html
 * 
 * @param str String to split.
 * @param delim Char to split around.
 * @return std::vector<std::string> Vector of pieces split around delimiter.
 */
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
/**
 * @brief Checks for object in a list.
 * 
 * @tparam T 
 * @param obj Object to look for.
 * @param list List to look in.
 * @return bool True or false based on whether object is found in list.
 */
template<typename T>
bool InList(T obj, std::vector<T> list) {
    bool out;
    auto pos = std::find(std::begin(list), std::end(list), obj);
    if (pos != std::end(list)){
        out = true;
    } else {out = false;}
    return out;
}

/**
 * @brief Check for string in another string.
 * 
 * @param sub Substring to look for.
 * @param main String to look in.
 * @return out  True or false based on whether sub is found in main.
 * @return false 
 */
bool InString(std::string sub, std::string main) {
    bool out;
    auto found = main.find(sub);
    if (found != std::string::npos){
        out = true;
    } else {out = false;}
    return out;
}

/**
 * @brief Extend vector with another vector (modifies base in-place).
 * 
 * @tparam T 
 * @param base Modif
 * @param extension 
 */
template<typename T>
void Extend(std::vector<T> base, std::vector<T> extension) {
    for (int i = 0; i < extension.size(); i++) {
        base.push_back(extension.at(i));
    }
}