#include "types.hpp"

template <typename T>
void reorder(std::vector<T>& v, const std::vector<size_t>& idx)
{
    std::vector<T> tmp(v.size());
    for (size_t i = 0; i < idx.size(); ++i)
        tmp[i] = std::move(v[idx[i]]);
    v = std::move(tmp);
}

