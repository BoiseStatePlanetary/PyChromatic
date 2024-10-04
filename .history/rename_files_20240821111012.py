import os
import sys

def user_input(prompt, type_, values=None, max_tries=1000):
    """
    Captures user_input and casts it to the expected type


    Parameters
    ----------
    prompt : str
        A message shown to the user to get a desired answer in the right type
    type_ : type
        The type expected to be captured from the user. The user's response is
        attempted to be cast to this type.
    values : list[type_]
        Acceptable values to receive from the user. If the response from the user
        is valid after the type check BUT the response is not in this list then
        the user will be prompted to try again.
    max_tries : int
        The maximum number of times the user should be prompted to provide valid
        input. Defaults to 1000. Inserted to the function's signature to aid in
        simplicity of tests.

    Returns
    -------
    any
        The user's response cast to the type provided by the `type_` argument to
        the function.
    """

    tries_count = 0

    while True:
        if tries_count >= max_tries:
            print("You have exceeded the maximum number of retries")
            return None

        try:
            result = type_(input(prompt))

        except ValueError:
            tries_count = tries_count + 1
            print("Sorry, not a valid datatype.")
            continue

        if type_ == str and values is not None:
            result = result.lower().strip()
            if result not in values:
                tries_count = tries_count + 1
                print("Sorry, your response was not valid.")
            else:
                return result
        elif type_ == int and values is not None:
            if result not in values:
                tries_count = tries_count + 1
                print("Sorry, your response was not valid.")
            else:
                return result
        else:
            return result

def rename_files():
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
    telescope_name = user_input("Enter Telescope Name: ", type_=str)
    planet_name = user_input("Enter Planet Name: ", type_=str)

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
