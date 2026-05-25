
"""

Returns values after '=' in config file.

eg. in config file

PARAMETER1="nice/path/to/parameter1"
PARAMETER2="not/nice/path/to/parameter2"

for inputs as below returns:

    get_from_config()             -> parameter not found in config
    get_from_config("")           -> no parameter specified to search in config
    get_from_config("hybdz")      -> parameter not found in config
    get_from_config("PARAMETER1") -> "nice/path/to/parameter1"
    get_from_config("PARAMETER2") -> "not/nice/path/to/parameter2"
    
"""
def get_from_config(parameter=""):

    config_path = "config.txt"
    
    if parameter == "":
        return f"no parameter specified to search in {config_path}"

    with open(config_path, "r") as config_file:
        for line in config_file:
            if parameter in line:

                parts = line.split("=")
                path = parts[1].strip(" \r\n\"")

                return path
    
    return f"parameter not found in {config_path}"

if __name__ == "__main__":
    print(get_from_config(parameter="ALEXA_VOICE"))
