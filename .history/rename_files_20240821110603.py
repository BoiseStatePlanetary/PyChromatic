import os
import sys
from .utils import user_input

def rename_files(telescope_name, planet_name):
    dir = os.path.join(os.getcwd(), "test_images")
    if not (os.path.exists(dir) and os.path.isdir(dir)):
        # write error message to stderr
        print(f"Directory {dir} does not not exist or is not a directory.", file=sys.stderr)
        # exit program with exit code 1 indicating the script has failed
        sys.exit(1)
    # get all files in the directory and store for each file it's name and the full path to the file
    # This way we won't have to create the full path many times
    my_files = [(file, os.path.join(dir, file)) for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file))]
    # sort by "modified" timestamp in reverse order => file with most recent modified date first
    # we need to use the fullpath here which is the second element in the tuple
    sorted_by_creation_date = sorted(my_files, key=lambda file: os.path.getmtime(file[1]))
    # get number of digits required to assign a unique value
    number_of_digits = len(str(len(my_files)))

    #ask for user to input telescope name & planet name to be added to file name
    telescope_name = user_input("Enter Telescope Name: ", type=str)
    planet_name = user_input()


    # loop over all files and rename them
    print("Renaming files...")
    for index, (file, fullpath) in enumerate(sorted_by_creation_date):
        # parse filename - keep date and add planet name
        file_split = file.split("_")
        date = file_split[0].split("T")[0]
        # rename files with leading zeros and start with index 1 instead of 0
        new_filename = f"{index + 1:0{number_of_digits}d}_{date}{telescope_name}_{planet_name}_{file_split[-1]}" 
        if new_filename == file:
            # move on to next file if the file already has the desired filename
            print(f"File already has the desired filename {file}. Skipping file.")
            continue
        # concatenate new filename with path to directory
        new_name = os.path.join(dir, new_filename)
        # rename the file
        print(f"{file} => {new_filename}")
        # os.rename(fullpath, new_name)

    print("Done.")

if __name__ == '__main__':
    rename_files()
