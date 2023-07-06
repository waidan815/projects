import os


def is_over_10000(text_file):
    with open(text_file, "r") as f:
        data = f.readlines()
        print(data)
        print(len(data))

        assert len(data) < 10000, print("Error")


def clean_up(
    path: str,
):
    """Given a path to a folder, this will remove all the files within the SUBDIRECTORIES of that folder. Use carefully.
    Note that this won't delete the sub-directories themselves"""

    base_path = path
    for subdir, dirs, files in os.walk(base_path):
        for file in files:
            os.remove(os.path.join(subdir, file))


def get_inputs(directory: str):
    all_frames = []

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        with open(file_path, "r") as f:
            frames = []
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                number = int(line)
                frames.append(number)

            all_frames.append(frames)

    return all_frames
