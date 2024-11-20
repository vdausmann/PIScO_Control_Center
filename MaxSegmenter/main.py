from MaxSegmenterModule import run_segmenter


if __name__ == "__main__":
    run_segmenter(
        # source_folder="/home/tim/Documents/Arbeit/PeruTest",
        source_folder="/home/pisco-controller/SO298-Test/",
        save_crops=True,
        save_marked_imgs=False,
        min_area_to_segment=400,
        min_area_to_save=400,
        save_path="/home/pisco-controller/SO298-Segmentation/",
        equalize_hist=False,
        resize=True,
        clear_save_path=True,
        bg_size=5,
        max_threads=10,
        n_sigma=2,
        n_cores=10,
        mask_imgs=True,
        mask_radius_offset=100,
    )
