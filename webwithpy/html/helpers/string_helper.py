def remove_quotes(quoted_string: str) -> str:
    """
    removes all quotes in any given string
    :param quoted_string: a string that contains quotes
    """
    return quoted_string.replace("'", "").replace('"', "")


def filter_pyht_line(line: str) -> str:
    """
    filters a line of an pyht(html + python) file
    aka this will remove all brackets and spacing from the line and will return the filtered version.
    """
    filtered_line = line[line.find("{{") + 2 : line.find("}}")]
    return filtered_line.lstrip(" ")
