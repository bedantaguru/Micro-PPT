import tempfile
import zipfile
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from Lib import FileOperation
from Lib.CompressImage import ImageCompression


def compress_image(file_path,
                   res_scale=1.2, quality=60, ppi=72):
    """
    Compress an image file with a given quality parameters.

    :param file_path: Image to be compressed (only supported formats are allowed)
    :param res_scale: A number ideally should be more than 1
    :param quality: Quality for compression (lesser means more lossy) 1-100
    :param ppi: DPI for compressed images
    :return: Compressed image is saved directly without returning anything
    """
    ic = ImageCompression(file_path)
    ic.compress(res_scale=res_scale, quality=quality, ppi=ppi)


def rename_pptx_file(file_path):
    """
    Rename a PPTX file by adding '-opt' before the '.pptx' extension.

    :param file_path: Original path to the PPTX file
    :return: New path with '-opt' added before the '.pptx' extension
    """
    dir_name, base_name = os.path.split(file_path)
    name, ext = os.path.splitext(base_name)
    new_base_name = f"{name} - opt{ext}"
    new_file_path = os.path.join(dir_name, new_base_name)
    return new_file_path


def compress_media_in_pptx(pptx_path=None,
                           output_path=None,
                           size_threshold_kb=1,
                           res_scale=1.5, quality=50, ppi=40):
    """
    Compress the media inside a PPTX file to facilitate easier sharing.
    :param pptx_path: The input PPTX file path. If left blank, the user will be
        prompted to select a file.
    :param output_path: The output file path for the compressed PPTX. If left
        blank, a renamed version of the input PPTX will be created in the same
        folder.
    :param size_threshold_kb: Images below this size (in kilobytes) will not be
        compressed.
    :param res_scale: A scaling factor for image resolution. A value greater
        than 1 will increase compression but may reduce image quality.
    :param quality: Quality parameter for JPEG compression. Higher values
        indicate better quality.
    :param ppi: DPI (dots per inch) parameter used to reduce the PPI of images.
    :return: None. The compressed PPTX is saved directly to the specified output
        path.
    """

    if pptx_path is None:
        pptx_path = FileOperation.FileHandling.file_choose()
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(pptx_path, 'r') as pptx:
            pptx.extractall(temp_dir)
            media_dir = os.path.join(temp_dir, 'ppt', 'media')

            if os.path.exists(media_dir):
                ftr_s = []
                with ThreadPoolExecutor() as exe:
                    for filename in os.listdir(media_dir):
                        media_path = os.path.join(media_dir, filename)
                        if os.path.isfile(media_path) and filename.lower().endswith(
                                ('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                            file_size_kb = os.path.getsize(media_path) / 1024
                            if file_size_kb >= size_threshold_kb:
                                ftr_s.append(exe.submit(compress_image, media_path, res_scale, quality, ppi))
                    for _ in tqdm(
                            as_completed(ftr_s),
                            desc="Processing File:",
                            unit="files",
                            total=len(ftr_s)):
                        pass

        if output_path is None:
            output_path = rename_pptx_file(pptx_path)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as pptx:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    pptx.write(file_path, arc_name)
