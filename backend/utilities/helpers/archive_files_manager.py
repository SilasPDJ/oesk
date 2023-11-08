import os
import os.path
from time import sleep

import aspose.zip as az
from io import BytesIO
import zipfile
from typing import Union


def _convert_rar_to_zip(rar_path, zip_name="rar_to_zip.zip", rarfile_shall_be_removed=True):
    """
    Convert a RAR file to a ZIP file.

    :param rar_path: The path to the RAR file.
    :param zip_name: The name for the resulting ZIP file.
    :param rarfile_shall_be_removed: defaults to True -> removes or not
    :return: The path to the converted ZIP file.
    """
    # Create ZIP archive
    with az.Archive() as zip:
        # Load RAR file
        with az.rar.RarArchive(rar_path) as rar:
            # Loop through entries
            for i in range(rar.entries.length):
                # Copy entries from RAR to ZIP
                if not rar.entries[i].is_directory:
                    ms = BytesIO()
                    rar.entries[i].extract(ms)
                    zip.create_entry(rar.entries[i].name, ms)
                else:
                    zip.create_entry(rar.entries[i].name + "/", None)
        # Save ZIP archive
        new_name = os.path.join(os.path.dirname(rar_path), zip_name)
        zip.save(new_name)
        sleep(3)
        if rarfile_shall_be_removed:
            os.remove(rar_path)
        return new_name


def extract_zip_folder(zip_path: Union[str, os.PathLike], destination: Union[str, os.PathLike] = '',
                       is_non_default_destination=False):
    """
    Extract the contents of a ZIP file to a specified destination.

    :param zip_path: The path to the ZIP file.
    :param destination: The destination folder for extraction.
    :param is_non_default_destination: Specify whether to use a non-default destination.
    :return: True if extraction was successful, False otherwise.
    """

    if zip_path.lower().endswith('.rar'):
        zip_path = _convert_rar_to_zip(zip_path)

    main_path = os.path.dirname(zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if destination:
                if is_non_default_destination:
                    zip_ref.extractall(destination)
                else:
                    zip_ref.extractall(os.path.join(main_path, destination))
            else:
                zip_ref.extractall(os.path.join(main_path, ""))
            return True
    except Exception as e:
        return False


if __name__ == '__main__':
    extract_zip_folder(r"O:\OneDrive\_FISCAL-2021\2023\10-2023\RICARDO SOUSA DE MACEDO\10-2023 Ricadrdo.rar", "NFS")
    extract_zip_folder(r"O:\OneDrive\_FISCAL-2021\2023\10-2023\RICARDO SOUSA DE MACEDO\10-2023 Ricadrdo.rar")
