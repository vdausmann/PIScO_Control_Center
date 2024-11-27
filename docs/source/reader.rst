Reader Component Overview
=========================

Purpose
-------

The Reader is designed to read a batch of images from the filesystem, resize them, and store them in a shared data structure for further processing.

Concurrency
-----------

It uses a custom `ThreadPool` class to manage multiple threads for reading images concurrently, which speeds up the processing of large batches.

Error Handling
--------------

The code includes checks for file validity, such as ensuring the file is not empty and that the image can be successfully read.

Detailed Explanation of the Code
--------------------------------

Classes and Functions
~~~~~~~~~~~~~~~~~~~~~

ReaderOutput Class
------------------

**Purpose:** Manages a thread-safe list of images. It uses a `Manager` from Python's `multiprocessing` module to create a shared list that can be accessed by multiple threads.

**Methods:**

- `__init__`: Initializes the list to store images with placeholders (None) for each expected image.
- `add_output`: Safely adds an image and its filename to the list at the specified index using a lock to prevent race conditions.

read_img Function
-----------------

**Purpose:** Reads an image from the filesystem and adds it to the `ReaderOutput`.

**Parameters:**

- `output`: An instance of `ReaderOutput` where the read image is stored.
- `input`: A tuple containing the file path and image index.
- `thread_index`: Index of the thread executing this function, used for logging.

**Process:**

1. Checks if the file size is zero (indicating an empty file) and skips it if so.
2. Attempts to read the file as a grayscale image using OpenCV.
3. Resizes the image to (2560, 2560) pixels.
4. Adds the image and its filename to `ReaderOutput`.

run_reader Function
-------------------

**Purpose:** Initializes the thread pool and manages the distribution of image files to threads for reading.

**Parameters:**

- `files`: List of file paths and indices to be processed.
- `output`: `ReaderOutput` instance to store results.
- `n_threads`: Number of threads to use for reading images.
- `resize`: Boolean flag indicating if resizing is required (though resizing is always done in the current implementation).

**Process:**

1. Initializes a `ThreadPool` with the `read_img` function.
2. Starts the specified number of threads.
3. Adds each file to the thread pool as a task.
4. Stops the thread pool after all tasks are added.

Key Considerations
------------------

- **Error Handling:** The implementation includes basic error handling for file reading and validity checks, which helps in debugging and ensures robustness.
- **Thread Safety:** The use of locks and a shared list via `Manager` ensures that image data is safely handled across threads.
- **Performance:** By using threading, the reader can handle large batches more efficiently, reducing the time spent waiting for I/O operations.
