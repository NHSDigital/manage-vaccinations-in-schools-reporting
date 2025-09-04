import os
from flask import url_for, current_app


def get_file_mtime(file_path):
    """
    Get the modification time of a file as a string for use in a cache busting URL.
    """
    try:
        return str(int(os.path.getmtime(file_path)))
    except (IOError, OSError):
        return None


def static(path):
    """
    Get the URL for a static file with cache busting.
    """
    static_folder = current_app.static_folder or "static"
    file_path = os.path.join(static_folder, path)

    mtime = get_file_mtime(file_path)

    if mtime:
        return url_for("static", filename=path, v=mtime)
    else:
        return url_for("static", filename=path)
