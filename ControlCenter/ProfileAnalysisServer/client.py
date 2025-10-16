# benchmark_client_indexed.py
import requests
import time
import statistics
import cv2 as cv
import numpy as np

SERVER = "http://127.0.0.1:8000"   # Use localhost; SSH tunnel can forward to remote
NUM_IMAGES = 10                    # Number of images to download (indices 0..9)

def benchmark_download():
    times = []
    image_sizes = []
    cv_images = []

    print(f"Starting benchmark: downloading {NUM_IMAGES} indexed images...")

    for idx in range(NUM_IMAGES):
        url = f"{SERVER}/image/{idx}"
        start_time = time.perf_counter()
        response = requests.get(url)

        if response.status_code != 200:
            print(f"[{idx}] Error {response.status_code}: {response.text}")
            continue

        data = response.content  # bytes stored in RAM
        size_kb = len(data) / 1024

        # --- Convert bytes to OpenCV image ---
        np_arr = np.frombuffer(data, np.uint8)
        img = cv.imdecode(np_arr, cv.IMREAD_GRAYSCALE)  # decode as color image
        if img is None:
            print(f"[{idx}] Failed to decode image")
            continue
        cv_images.append(img)

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        times.append(elapsed)
        image_sizes.append(size_kb)

        print(f"[{idx}] {size_kb:.1f} KB in {elapsed:.4f} s "
              f"({size_kb / elapsed:.1f} KB/s)")

    if times:
        print("\n=== Benchmark Summary ===")
        print(f"Total images: {len(times)}")
        print(f"Total time: {sum(times)}")
        print(f"Average time: {statistics.mean(times):.4f} s")
        print(f"Median time: {statistics.median(times):.4f} s")
        print(f"Average speed: {statistics.mean(image_sizes) / statistics.mean(times):.1f} KB/s")
    else:
        print("No successful downloads.")

    for i in range(NUM_IMAGES):
        img = cv.resize(cv_images[i], None, fx=0.5, fy=0.5)
        cv.imshow("Img", img)
        cv.waitKey(50)

if __name__ == "__main__":
    benchmark_download()

