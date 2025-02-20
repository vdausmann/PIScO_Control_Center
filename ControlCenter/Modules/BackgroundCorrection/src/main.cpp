#include "threads.hpp"
#include "utils.hpp"
#include <iostream>
#include <opencv2/highgui.hpp>

int main()
{
    Settings settings = readConfig("input.ini");

    ThreadManager tm(settings);
    tm.start();

    return 0;
}
