import sys
import zlib


def crc32(fileName):
    """
    Returns Crc32 checksum of a file.
    """

    prev = 0
    for eachLine in open(fileName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return prev & 0xFFFFFFFF
