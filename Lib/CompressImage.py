import shutil
import tempfile
import os
import warnings
from PIL import Image, ImageSequence


class ImageCompressionBare:
    supported_formats = tuple(
        [f".{ext}" for ext in ("jpg", "jpeg", "png", "gif", "bmp")]
    )

    def __init__(self, image_file, output_file=None):
        if output_file is None:
            output_file = image_file
        else:
            if os.path.exists(output_file):
                warnings.warn(f"The specified output file {output_file} exists. It will be replaced!")

        if os.path.exists(image_file):
            self.path = image_file
            self.out_path = output_file
            self.original_out_path = output_file
        else:
            raise FileNotFoundError(f"The image {image_file}, does not exists or inaccessible!")

        _, ext = os.path.splitext(image_file)
        ext = ext.lower()

        if ext not in ImageCompressionBare.supported_formats:
            raise ValueError(f"The image {image_file} is of unsupported kind!")
        self.ext = ext
        self.image = Image.open(self.path)

    @staticmethod
    def rescale(img, res_scale=1.2):
        original_size = (img.width, img.height)
        if res_scale != 1:
            img = img.resize((round(img.width / res_scale),
                              round(img.height / res_scale)),
                             resample=Image.LANCZOS)
            img = img.resize(original_size,
                             resample=Image.LANCZOS)
        return img

    def set_out_path(self, output_file=None):
        if output_file is not None:
            self.out_path = output_file
        else:
            self.out_path = self.original_out_path

    def compress_png(self, res_scale=1.2, quality=65, ppi=72):
        if self.image.format in ['PNG', 'BMP']:
            img = ImageCompressionBare.rescale(self.image, res_scale)
            img = img.convert('P', palette=Image.ADAPTIVE)
            img.save(self.out_path,
                     format=self.image.format,
                     optimize=True, quality=quality, dpi=(ppi, ppi))

    def compress_jpg(self, res_scale=1.2, quality=65, ppi=72):
        if self.image.format in ['JPEG', 'JPG']:
            img = ImageCompressionBare.rescale(self.image, res_scale)
            img.save(self.out_path,
                     format=self.image.format,
                     optimize=True, quality=quality, dpi=(ppi, ppi))

    def compress_gif(self, res_scale=1.2, quality=65, ppi=72):
        if self.image.format == "GIF":
            frames = [ImageCompressionBare.rescale(
                frame.copy(),
                res_scale).convert('P', palette=Image.ADAPTIVE)
                      for frame in ImageSequence.Iterator(self.image)]
            frames[0].save(self.out_path,
                           save_all=True,
                           append_images=frames[1:],
                           optimize=True, quality=quality, dpi=(ppi, ppi),
                           loop=0)

    def compress(self, res_scale=1.2, quality=65, ppi=72):
        if self.image.format in ['PNG', 'BMP']:
            self.compress_png(res_scale, quality, ppi)
        elif self.image.format in ['JPEG', 'JPG']:
            self.compress_jpg(res_scale, quality, ppi)
        elif self.image.format == "GIF":
            self.compress_gif(res_scale, quality, ppi)
        else:
            raise ValueError(f"Unsupported image format: {self.image.format}")


class ImageCompression:
    def __init__(self, image_file, output_file=None):
        self.ICB = ImageCompressionBare(image_file, output_file)

    def __compress(self, res_scale=1.2, quality=65, ppi=72, compression_ratio_threshold=5):
        compression_ok = False
        with tempfile.TemporaryDirectory() as td:
            tfn = os.path.join(td, "test" + self.ICB.ext)
            self.ICB.set_out_path(tfn)
            self.ICB.compress(res_scale, quality, ppi)
            in_size = os.path.getsize(self.ICB.path)
            out_size = os.path.getsize(tfn)
            ratio = (1 - out_size / in_size) * 100
            if ratio > compression_ratio_threshold:
                compression_ok = True
                if os.path.exists(tfn):
                    shutil.copy2(tfn, self.ICB.original_out_path)
                else:
                    self.ICB.set_out_path()
                    self.ICB.compress(res_scale, quality, ppi)
        return compression_ok

    def compress(self, res_scale=1.2, quality=65, ppi=72, compression_ratio_threshold=5):
        try:
            self.__compress(res_scale, quality, ppi, compression_ratio_threshold)
        except Exception as e:
            print(f"While compressing image exception :{e} - occurred. File:- {os.path.split(self.ICB.path)[1]}")
