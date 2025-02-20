#include "test_include.hpp"

void test_include()
{
    // generate random matrix:
    cv::Mat image(1000, 1000, CV_8U);
    cv::randu(image, cv::Scalar(0), cv::Scalar(255));

    cv::imshow("image", image);
    cv::waitKey(0);
}
