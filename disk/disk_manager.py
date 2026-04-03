#! /usr/bin/env python3
import os

PAGE_SIZE = 4096

class DiskManager:

    def __init__(self, filename: str):
        self.filename = filename

        # create file if not exists
        if not os.path.exists(self.filename):
            open(self.filename, "wb").close()

        # open for read/write binary
        self.file = open(self.filename, "r+b")

        # calculate number of existing pages
        self.file.seek(0, 2)  # go to end
        self.file_size = self.file.tell()
        # this is from the end of the file and further
        self.next_page_id = self.file_size // PAGE_SIZE

    # -------------------------
    # Write Page
    # -------------------------
    def write_page(self, page_id: int, data: bytes) -> None:
        if len(data) != PAGE_SIZE:
            raise ValueError("Data must be exactly PAGE_SIZE bytes")

        offset = page_id * PAGE_SIZE
        self.file.seek(offset)
        self.file.write(data)

        # ensure persistence
        self.file.flush()
        os.fsync(self.file.fileno())

    # -------------------------
    # Read Page
    # -------------------------
    def read_page(self, page_id: int) -> bytes:
        offset = page_id * PAGE_SIZE
        self.file.seek(offset)

        data = self.file.read(PAGE_SIZE)

        # pad if page doesn't fully exist
        if len(data) < PAGE_SIZE:
            data += b'\x00' * (PAGE_SIZE - len(data))

        return data

    # -------------------------
    # Allocate Page
    # -------------------------
    def allocate_page(self) -> int:
        page_id = self.next_page_id
        self.next_page_id += 1

        # move to end of file
        self.file.seek(0, 2)

        # write empty page
        self.file.write(b'\x00' * PAGE_SIZE)

        self.file.flush()
        os.fsync(self.file.fileno())

        return page_id

    # -------------------------
    # Close File
    # -------------------------
    def close(self) -> None:
        if self.file:
            self.file.close()