import uuid
from exif import Image as exIm

print('Hello')
uuid4=str(uuid.uuid4())#write UUID to image meta data
#with open("/home/pisco-controller/SO298-Test2/20230503/20230503-1016/JPG/20230503-10402549_003.198bar_27.24C.jpg", 'wb') as img_file:
with open('franz.jpg', 'rb') as img_file:
    img = exIm(img_file)
    img.image_unique_id=uuid4
with open('franz.jpg', 'wb') as imga_file:
    imga_file.write(img.get_file())
      
                                           
#with open("/home/pisco-controller/SO298-Test2/20230503/20230503-1016/JPG/20230503-10402549_003.198bar_27.24C.jpg", 'rb') as img_file2:
with open('franz.jpg', 'rb') as img_file2:
    img2 = exIm(img_file2)
    if img2.get("image_unique_id")==uuid4:
    #update yaml file
        print('UUID JPG Metadatawrite Success!')
    else:
        print('UUID JPG Metadatawrite Error!')            
