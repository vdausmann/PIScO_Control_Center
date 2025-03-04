import datetime

def write_new_inputfile(settings: dict, page_name: str) -> str:
    now = datetime.datetime.now()
    path = "tmp/" + page_name + "_" + f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}" + "_input.ini"
    with open(path, "w") as f:
        f.write("# Input file for " + page_name + "\n")
        for key in settings.keys():
            f.write(key + "=" + str(settings[key].get()) + "\n")
    return path

