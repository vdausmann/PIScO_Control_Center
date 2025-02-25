#pragma once
#include <string>

struct circularIndex {
    int idx;
    int maxIdx;

    circularIndex(int maxIdx)
        : idx(0)
        , maxIdx(maxIdx)
    {
    }

    circularIndex operator++(int)
    {
        circularIndex old = *this;
        idx = (idx + 1) % maxIdx;
        return old;
    }
};

void runSegmenter();
