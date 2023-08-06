"""This tutorial will showcase the capability of this library.
"""
sample_location = "repo/images sample"
f"""
We are going to extract information from images of a person id card,
to be more specific we are going to extract name, sex, marital status and job.
The sample images located in {sample_location}. All are already censored and
preprocessed to yield better result.
A quick note, the process of censoring the image utilize this library 
to find the pixel coordinate of an anchor string to automate the censorship,
but we won't discuss it here, maybe some other time.
"""
# First let's import the necessary module
from pathlib import Path  # for file manipulation
from string import ascii_uppercase as upper  # we will use this for string cleanup
import pandas as pd  # to process data
from PIL.Image import open as open_image  # image loader
import pytesseract  # OCR tools used in this tutorial

from src.slimpy import Fragment, REM  # main player of this tutorial
"""For this tutorial, I already created custom class that specialized in this task
that we will perform, named ExtractFieldWithRegex. To know more about the class
see the API documentation"""
from doc.extra import ExtractFieldWithRegex

# If your tesseract executable not in path, first specify the path to it
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Since the string that we want to extract is all uppercase alphabet, define function
# to clean the extracted string
def clean_non_uppercase(string):
    """Stripe non alphabetic uppercase character that trailing the string"""
    str_length = len(string)
    start_idx = find_trailing_Uppercase_index(string, str_length)
    end_idx = find_trailing_Uppercase_index(string, str_length, -1) + 1
    end_idx = str_length if end_idx == 0 else end_idx
    return string[start_idx:end_idx]


def find_trailing_Uppercase_index(string, str_len=None, increment=1):
    """child of clean_non_uppercase function. It iterate the index until it find
     an uppercase letter. The index used to slice the string."""
    str_len = len(string) if str_len is None else str_len
    start = 0 if increment == 1 else -1
    for r in range(start, str_len * increment, increment):
        if string[r] in upper:
            return r
    return 0 if increment == 1 else -1


# We start defining an anchor
# The word used here is Indonesian, from left to right the field we trying
# to extract using anchor is name, sex, marital status and job.
fields_name = ["Nama", "Jenis Kelamin", "Status Perkawinan", "Pekerjaan"]
start_anchor = ["Nama :", "Jenis Kelamin :", "Status Perkawinan:", "Pekerjaan :"]
end_anchor = [None, "Gol Darah", None, None]

# Create ExtractFieldWithRegex object and start adding anchor Fragment as rule
extract = ExtractFieldWithRegex()
for i in range(len(fields_name)):
    fragments_start = Fragment(start_anchor[i])
    fragments_end = Fragment(end_anchor[i]) if end_anchor[i] is not None else None
    extract.add_rule(fields_name[i], fragments_start, fragments_end)

# Now prepare the image
images_source_path = r"../../test_sub/extract data kusuka/source prepared"
# Convert path string to Path
images_source_path = Path(images_source_path)
# Search all image path in that directory
images_path = images_source_path.glob("*.png")

# Create panda dataframe to process the extracted data
extract_accumulator = pd.DataFrame(columns=fields_name)
# Below code can be omitted.
# Setting displayed tabular data, to show our whole DataFrame
# without truncating the display.
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

count = 0
for i_path in images_path:
    count += 1
    image = open_image(str(i_path))
    # extract the image text
    reference = pytesseract.image_to_string(image, config="--oem 1 --psm 6")
    # set the reference for the extract object to match against
    extract.set_reference(reference)

    # now we perform extraction using perform_extraction() methode, it return dictionary
    # of extracted string that we wanted
    extracted = extract.perform_extraction()
    # create DataFrame object from the extracted result
    extracted = pd.DataFrame(extracted, index=[count])
    # merge the result with the previous one
    extract_accumulator = pd.concat([extract_accumulator, extracted])

# see the raw result
print(extract_accumulator)

"""
Since sex, marital status and job has a determined value, mean the result can be controlled
in other word the value just a matter of multiple choice, we can do some matching again:"""

choice_value = [None,
                ("LAKI-LAKI", "PEREMPUAN"),
                ("KAWIN", "BELUM KAWIN", "CERAI HIDUP"),
                ("PETANI/PEKEBUN", "BELUM/TIDAK BEKERJA", "MENGURUS RUMAH TANGGA", "WIRASWASTA",)]

# create a list to store REM object to easily iterate it when matching
match_choice = []
for ref in choice_value:
    rematch = None
    if ref is not None:
        rematch = REM()
        rematch.set_reference(ref)
    match_choice.append(rematch)

# Now we iterate it using index
for i in range(len(fields_name)):
    if match_choice[i] is not None:
        # create new list to update the value of the current result DataFrame
        new_series = []
        # now we iterate the value of a column of the DataFrame
        for value in extract_accumulator[fields_name[i]]:
            # clean non uppercase letter
            value = clean_non_uppercase(value)
            # create Fragment for the value to match it against earlier defined multiple choice
            value_frag = Fragment(value, 0.5)
            # now we perform matching for the value
            match = match_choice[i].perform_matching(value_frag)
            new_value = match.match
            # append the new value if match or the old value if not
            new_series.append(new_value) if new_value is not None else new_series.append(value)
        # here we replace the old column with new one
        extract_accumulator[fields_name[i]] = new_series

# See the end result
print('\n', extract_accumulator)

"""
As you can see, some field are missing and some aren't what like it intended, 
there is many situation that could lead to this and from developer perspective 
there should be some unoptimized and miss written code somewhere.
Maybe it will be found in the future by someone and there would be and update
to this library.
"""
