import os

import ujson


def replace_values_with_potato(json_data):
    if isinstance(json_data, dict):
        return {
            key: replace_values_with_potato(value) if "thoughts" in key else value
            for key, value in json_data.items()
        }
    elif isinstance(json_data, list):
        return [replace_values_with_potato(item) for item in json_data]
    else:
        return "potato"


def process_json_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as file:
        data = ujson.load(file)

    # Replace the top-level key "en" with "po"
    if "en" in data:
        data = {"po": replace_values_with_potato(data["en"])}
    else:
        data = [replace_values_with_potato(item) for item in data]

    with open(output_path, "w") as file:
        ujson.dump(data, file, indent=4)


# Folder setup
file_dir = os.path.dirname(os.path.realpath("__file__"))
print(file_dir)
folder = "thoughts/alive"
input_folder = os.path.join(file_dir, f"../en/{folder}")
output_folder = os.path.join(file_dir, f"./{folder}")

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        if ".en." in filename:
            # Rename the file by replacing "en" with "po"
            new_filename = filename.replace(".en", ".po")
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, new_filename)
        else:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

        process_json_file(input_path, output_path)

print("All JSON files processed!")
