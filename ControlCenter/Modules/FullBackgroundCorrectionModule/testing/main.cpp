#include "threads.hpp"
#include "utils.hpp"
#include <iostream>
#include <opencv2/highgui.hpp>

int main()
{
    Settings settings = readConfig("testing/input.ini");

    ThreadManager tm(settings);

    return 0;
}
