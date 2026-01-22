#/home/tim/Documents/Arbeit/PIScO_Control_Center/PISCO_Modules/FullSegmenter/Results/M202_046-01_PISCO2_20240727-0334_Images-PNG.h5
#/M202_046-01_PISCO2_0009.91dbar-38.69N-027.49W-22.32C_20240727-03372864
#
#
curl -X 'POST' \
  'http://127.0.0.1:8001/open-hdf-file/%2Fhome%2Ftim%2FDocuments%2FArbeit%2FPIScO_Control_Center%2FPISCO_Modules%2FFullSegmenter%2FResults%2FM202_046-01_PISCO2_20240727-0334_Images-PNG.h5' \
  -H 'accept: application/json' \
  -d ''

curl -X 'GET' \
  'http://127.0.0.1:8001/get-hdf-keys/M202_046-01_PISCO2_0009.91dbar-38.69N-027.49W-22.32C_20240727-03372864?file_path=%2Fhome%2Ftim%2FDocuments%2FArbeit%2FPIScO_Control_Center%2FPISCO_Modules%2FFullSegmenter%2FResults%2FM202_046-01_PISCO2_20240727-0334_Images-PNG.h5' \
  -H 'accept: application/json'

echo "-------------------------------"
curl -X 'GET' \
  'http://127.0.0.1:8001/get-hdf-dataset-info/M202_046-01_PISCO2_0009.91dbar-38.69N-027.49W-22.32C_20240727-03372864%2F1D_crop_data?file_path=%2Fhome%2Ftim%2FDocuments%2FArbeit%2FPIScO_Control_Center%2FPISCO_Modules%2FFullSegmenter%2FResults%2FM202_046-01_PISCO2_20240727-0334_Images-PNG.h5' \
  -H 'accept: application/json'

echo "-------------------------------"
curl -X 'GET' \
  'http://127.0.0.1:8001/read-hdf-dataset/M202_046-01_PISCO2_0009.91dbar-38.69N-027.49W-22.32C_20240727-03372864%2F1D_crop_data?file_path=%2Fhome%2Ftim%2FDocuments%2FArbeit%2FPIScO_Control_Center%2FPISCO_Modules%2FFullSegmenter%2FResults%2FM202_046-01_PISCO2_20240727-0334_Images-PNG.h5' \
  -H 'accept: application/json' \
