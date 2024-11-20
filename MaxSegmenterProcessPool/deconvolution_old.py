import cv2 as cv
import torch
import numpy as np
from pathlib import Path
import os


from multiprocessing import Queue

from MaxSegmenterProcessPool.lucyd import LUCYD, device

## Load Deconv Model globally for faster inference on CPU
MODEL_NAME='lucyd-edof-plankton_231204.pth'
model = LUCYD(num_res=1).to(device)

root_dir = Path(__file__).resolve().parent
model_path=root_dir / "models"
model.load_state_dict(torch.load(os.path.join(model_path,MODEL_NAME)))
model.eval()

def run_deconvolution(input: Queue, output: Queue, n_imgs: int, batch_size: int = 1):
    batch = []
    filenames = []

    while n_imgs > 0:
        corrected, cleaned, mean, fn = input.get()
        n_imgs -= 1

        # Prepare the image for deconvolution
        # ... [your existing image preprocessing code] ...
        x = cleaned / 255
        x_t = torch.from_numpy(x).to(device)
        x_t = x_t.unsqueeze(0).unsqueeze(0)

        # Accumulate batch
        batch.append(x_t)
        filenames.append(fn)

        # Check if batch is ready to process
        if len(batch) == batch_size or n_imgs == 0:
            batch_tensor = torch.cat(batch, dim=0)  # Combine images into a single tensor

            # Deconvolution on the batch
            with torch.no_grad():
                y_hat_batch, _, _ = model(batch_tensor.float())

            # Process each image in the batch
            for i in range(y_hat_batch.shape[0]):
                deconv = y_hat_batch.detach().cpu().numpy()[i, 0]
                deconv = deconv * 255
                cleaned = deconv.astype(np.uint8)
                corrected = cv.bitwise_not(cleaned)

                # Put the result in the output queue
                output.put((corrected, cleaned, mean, filenames[i]))

            # Clear the batch for next round
            batch.clear()
            filenames.clear()

    print('deconvolution finished')


# def run_deconvolution(input: Queue, output: Queue, n_imgs: int):
    
#     for _ in range(n_imgs):
#         corrected, cleaned, mean, fn = input.get()

#         #deconvolution on cleaned img
#         with torch.no_grad():
#             #x = cv.resize(cleaned,(2560,2560))
#             x = cleaned
#             if x.shape[0] % 2 != 0: x = x[1:]
#             if x.shape[1] % 2 != 0: x = x[:,1:]
#             # x = (x - np.min(x))/(np.max(x) - np.min(x))
#             x = x/255

#             x_t = torch.from_numpy(x).to(device)
#             x_t = x_t.unsqueeze(0).unsqueeze(0)
#             y_hat, y_k, update = model(x_t.float())
#             y = x_t.detach().cpu().numpy()[0,0]
#             deconv = y_hat.detach().cpu().numpy()[0,0]
#             deconv = deconv*255

#         cleaned = deconv
#         cleaned = cleaned.astype(np.uint8)
#         corrected = cv.bitwise_not(cleaned)
#         output.put((corrected, cleaned, mean, fn))
#     print('deconvolution finished')
