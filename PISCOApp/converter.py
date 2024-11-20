import os
import pickle

with open(os.path.join("yaml_json_converter", "test.yaml"), "w") as f:
    f.write("image-set-header:\n")
    f.write("    image-set-name: SO268-1_21-1_GMR_CAM-23 (wird befüllt)\n")
    f.write("    image-set-context: Cruise SO298 Equatorial Pacific GEOTRACES GP11")


def get_field(s: str):
    field_substr = s.split(" ")
    field = field_substr[-1]
    index = s.find(field)
    return index


def init_yaml_file(path, info: dict):
    with open(path, "w") as f:
        f.write("image-set-header:\n")
        info = info["header"]
        for key in info.keys():
            f.write(" " * 4 + f"{key}: ")
            if type(info[key]) == dict:
                f.write("\n")
                key2 = list(info[key].keys())[0]
                offset = get_field(key2)
                f.write(" " * 8 + f"{key2}: {info[key][key2]}\n")
                for key2 in list(info[key].keys())[1:]:
                    f.write(" " * 8 + " " * offset + f"{key2}: {info[key][key2]}\n")
            else:
                for i, row in enumerate(info[key]):
                    if i > 0:
                        f.write(" " * 8 + f"{row}\n")
                    else:
                        f.write(f"{row}\n")
        f.write("image-set-items:\n")


def append_entry(path, info: dict):
    with open(path, "a") as f:
        key = list(info.keys())[-1]
        # for key in info.keys():
        f.write(" " * 4 + f"{key}:\n")
        for key2 in info[key].keys():
            f.write(" " * 8 + f"{key2}: {info[key][key2]}\n")


if __name__ == "__main__":
    import time

    info = {
        "header": {
            "image-set-name": ["SO298_298-33-1_PISCO2"],
            "image-set-context": ["Cruise SO298 Equatorial Pacific GEOTRACES GP11"],
            "image-set-project": ["SO298"],
            "image-set-abstract": [
                "The research cruise SO298 is part of the International GEOTRACES",
                "Programme as a section cruse. The cruise will cross the equatorial Pacific Ocean",
                "(EPO) along 0°S from Guayaquil (Ecuador) to Townsville (Australia), with a focus",
                "on trace element biogeochemistry and chemical oceanography but also including",
                "physical and biological oceanographic components. The research topic of the cruise",
                "is to determine in detail the distributions, sources and sinks of trace elements",
                "and their isotopes (TEIs) in the water column along a zonal section in one of",
                "the least studied ocean regions on earth.",
            ],
            "image-set-event": ["SO298_298-33-1"],
            "image-set-platform": ["ROS4"],
            "image-set-sensor": ["PISCO2"],
            "image-set-uuid": ["3cbe2348-e139-4c9a-84c8-0c957220da22"],
            "image-set-data-handle": [""],
            "image-set-metadata-handle": [""],
            "image-set-crs": ["EPSG:4326"],
            "image-set-type": ["photo"],
            "image-set-creators": {
                "- name": "A. Theileis",
                "affiliation": "GEOMAR Helmholtz-Zentrum für Ozeanforschung Kiel",
                "email": "atheileis@geomar.de",
                "orcid": "0",
            },
            "image-set-pi": {
                "name": "J. Taucher",
                "affiliation": "GEOMAR Helmholtz-Zentrum für Ozeanforschung Kiel",
                "email": "Jtaucher@geomar.de",
                "orcid": "0000-0001-9944-0775",
            },
            "image-set-license": ["CC-BY"],
            "image-set-coordinate-uncertainty": ["3"],
            "image-set-event-information": ["Bio-Profile -nach einbau"],
            "image-set-item-identification-scheme": [
                "PROJECT_EVENT_SENSOR_FREETEXT_DATE_TIME.png"
            ],
            "image-set-resolution": ["10 lpmm"],
            "image-set-quality": ["raw"],
            "image-set-illumination": ["artificial"],
            "image-set-spectral-resolution": ["grayscale"],
            "image-set-capture-mode": ["timer"],
            "image-set-marine-zone": ["water column"],
            "image-set-pixel-per-millimeter": ["23"],
            "image-set-acquisition-settings": {
                "Flashduration": "30",
                "Flashpower": "237",
                "Tagamplitude": "60",
                "Binning": "2x2",
                "Gain": "1",
                "Mirrow adjusted": "yes",
                "Lenssystem": "500-400-160",
            },
        }
    }

    info["SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg"] = {
        "image-uuid": "9999ba88-1a20-4efe-a0ac-6b4233490ad6",
        "image-hash": "83f30eb35d1325c44c85fba0cf478825c0a629d20177a945069934f6cd07e087",
        "image-datetime": "2019-05-13 13:14:15.0000",
        "image-longitude": "-123.854637",
        "image-latitude": "42.133426",
        "image-depth": "4230.3",
    }

    start = time.perf_counter()
    init_yaml_file(os.path.join("yaml_json_converter", "test.yaml"), info)
    for i in range(500):
        info[f"{i}_" + "SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg"] = info[
            "SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg"
        ]
        append_entry(os.path.join("yaml_json_converter", "test.yaml"), info)
    with open("test.pickle", "bw") as f:
        pickle.dump(info, f)
    end = time.perf_counter()
    print(end - start, (end - start) / 500)

    with open("test.pickle", "br") as f:
        d = pickle.load(f)

    print(d["header"])
