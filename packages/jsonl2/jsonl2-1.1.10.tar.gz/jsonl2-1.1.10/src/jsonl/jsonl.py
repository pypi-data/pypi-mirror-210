"""Json Line class able to read and write
json line objects, both, locally and in the cloud;
compressed or in plain text thanks to smart-open library"""
import json
import logging
from itertools import count
from typing import IO

import smart_open
from tqdm import tqdm

logging.getLogger('smart_open').setLevel(
    logging.ERROR)  # set smart_open logging only for error messages


class Jsonl:
    """Jsonl | Json Line Stream class"""

    def __init__(self,
                 path: str,
                 mode: str = "r",
                 open_kwargs: dict or None = None,
                 offset: int = 0,
                 limit: int or None = None,
                 tqdm_kwargs: dict or None = None):
        """
        :param path: input file
        :param mode: open mode "r","w","a" (default: "r")
        :param open_kwargs: extra params for open method
        :param offset: skip offset lines
        :param limit: max number of lines to be read
        :param tqdm_kwargs: extra params for tqdm constructor
        """

        open_kwargs = open_kwargs if open_kwargs else {}

        self.path = path
        self.mode = mode
        self.open_kwargs = open_kwargs
        self.offset = offset
        self.limit = limit
        self.tqdm_kwargs = tqdm_kwargs

        self.pbar: tqdm or None = None
        self.file: IO = smart_open.open(path, mode=mode, **open_kwargs)
        self.line_counter = 0
        self.new_line_prefix: str = "\n" if "a" in mode else ""

    @classmethod
    def count_lines(cls,
                    file_path: str,
                    tqdm_kwargs: dict or None = None) -> int:
        """Efficiently count lines in a json line file

        :param file_path: the file path
        :param tqdm_kwargs: extra parameters for tqdm
        :return: number of lines in the file
        """
        tqdm_default_kwargs = {"desc": f"Jsonl.count_lines('{file_path}')..."}
        tqdm_final_kwargs = tqdm_default_kwargs if tqdm_kwargs is None else {
            **tqdm_default_kwargs,
            **tqdm_kwargs
        }

        with smart_open.open(file_path) as file:
            file_iterator = tqdm(
                file, **tqdm_final_kwargs) if tqdm_kwargs is not None else file

            n_lines = len([1 for _ in file_iterator])
            return n_lines

    def _skip_offset_lines(self):
        """Skip `self.offset` number of lines from the current position"""
        n = self.offset

        if n == 0:
            return False

        tqdm_kwargs = self.tqdm_kwargs if self.tqdm_kwargs else {}
        tqdm_default_kwargs = {
            "total": n,
            "desc": f"Jsonl.skip('{self.path}',{n})",
            "leave": True
        }
        tqdm_input_kwargs = {**tqdm_default_kwargs, **tqdm_kwargs}
        iterator = tqdm(
            zip(range(n), self.file), **
            tqdm_input_kwargs) if self.tqdm_kwargs is not None else zip(
                range(n), self.file)

        for _, _ in iterator:
            pass

        return True

    def write(self, data: dict or list[dict]) -> int:
        """writes all objects in data and return the number of lines"""
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ValueError("write expects dict or list object")

        n = 0
        for x in data:
            s = json.dumps(x)
            s = self.new_line_prefix + s
            self.new_line_prefix = "\n"
            self.file.write(s)
            n += 1
        return n

    def readline(self) -> dict or None:
        """Read one line and parse as an object
        :return: a dictionary object
        """
        line = self.file.readline()
        if not line:
            return None
        data = json.loads(line)
        return data

    def __iter__(self):
        """For using in a `for` loop"""
        self._skip_offset_lines()
        self.line_counter = 0

        n = self.limit
        extra = f",{n}" if n else ""

        tqdm_default_kwargs = {
            "desc": f"Json.read('{self.path}'{extra})",
            "leave": True,
            "total": n
        }

        kwargs = self.tqdm_kwargs if self.tqdm_kwargs else {}
        tqdm_input_kwargs = {**tqdm_default_kwargs, **kwargs}
        self.pbar = tqdm(
            count(), **
            tqdm_input_kwargs) if self.tqdm_kwargs is not None else None

        return self

    def __next__(self):
        """For getting the next element within the `for` loop
        :return: parsed json object
        """
        if self.limit and self.line_counter == self.limit:
            if self.pbar:
                self.pbar.close()
            raise StopIteration

        data = self.readline()
        if data:
            self.line_counter += 1
            if self.pbar:
                self.pbar.update()

            return data

        if self.pbar:
            self.pbar.close()
        raise StopIteration
