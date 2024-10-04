import os
import sys        

def rename_files():
    # dir = input("Enter the path to the files to be renamed: ")
    dir = "test_images"
    if not (os.path.exists(dir) and os.path.isdir(dir)):
        # write error message to stderr
        print(f"Directory {dir} does not not exist or is not a directory.", file=sys.stderr)
        # exit program with exit code 1 indicating the script has failed
        sys.exit(1)
    # pull all files in the directory THAT ARE FITS and store for each file it's name and the full path to the file
    # This way we won't have to create the full path many times
    my_files = []
    for file in os.listdir(dir):
        if os.path.join(dir, file):
            if os.path.splitext(file)[1] == ".fits":
                my_files.append((file, os.path.join(dir, file)))
            else: pass
        else: pass
    if len(my_files) == 0: 
        raise Exception(f"No FITS files in Directory {dir}")
    # sort by "modified" timestamp in reverse order => file with most recent modified date first
    # we need to use the fullpath here which is the second element in the tuple
    sorted_by_creation_date = sorted(my_files, key=lambda file: os.path.getmtime(file[1]))
    # get number of digits required to assign a unique value
    number_of_digits = len(str(len(my_files)))
    # use at least 3 digits, even if that's not actually required to uniquely assign values
    number_of_digits = max(3, number_of_digits)

    #ask for user to input telescope name & planet name to be added to file name
    telescope_name = "Melba"  # input("Enter Telescope Name: ")
    planet_name = "TrES-3b"  #input("Enter Planet Name: ")

    # loop over all files and rename them
    print("Renaming files...")
    for index, (file, fullpath) in enumerate(sorted_by_creation_date):
        # parse filename - keep date and add planet name
        file_split = file.split("_")
        if len(file_split) == 4:
            date = file_split[1][:8]
        else:
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
        os.rename(fullpath, new_name)

    print("Done.")

if __name__ == '__main__':
    rename_files()
