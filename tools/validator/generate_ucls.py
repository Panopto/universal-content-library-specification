#!/usr/bin/python

import argparse
import os
import sys
import uuid
import datetime
import subprocess
import distutils.spawn
import lib.logging
from lib.ffprobe_info import FFprobeInfo
from lib.ucls_directory import SubdirectoriesType
from lib.ucls_directory import SessionsType
from lib.ucls_directory import File as UCSFile
from lib.ucls_directory import Directory as UCLSDirectory
from lib.ucs_session import VideoType
from lib.ucs_session import VideosType
from lib.ucs_session import Session
from lib.ucls_library import Library
from lib.ucls_library import RootDirectoriesType
from lib.dir_entry import DirEntry


# Global creation date
CREATION_DATE = datetime.datetime.now()


def is_media_file(filename):
    """
    Uses ffrobe to detect whether a file is an audio or video file
    """
    isAudioOrVideo = False
    cmnd = ['ffprobe', '-v', 'quiet', '-print_format',
            'json', '-show_format', '-show_streams', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    ffprobe_info = FFprobeInfo(out)
    if(bool(ffprobe_info.__dict__) and ffprobe_info.streams is not None):
        for stream in ffprobe_info.streams:
            if('bit_rate' in list(stream.keys())):
                if not ((stream['bit_rate'] is None)
                        or (stream['bit_rate'] == 'N/A')):
                    isAudioOrVideo = True
                    break

    return isAudioOrVideo


def get_parent_dir(rel_dir_path):
    """
    Gets relative path of parent dir, e.g. parent of dir "foo\bar" is "foo"
    """
    return os.path.dirname(rel_dir_path)


def process_directory(
        dir_entries,
        root_dir,
        rel_path,
        xml_file,
        dir_id):
    """
    Process a directory, creating UCS xml for each media file in it and
    then recursively process its subdirs before writing the UCLS xml for
    the directory

    :param dir_entries: The global dictionary of DirEntry objects
    :param root_dir: The global root dir passed in as program arg
    :type rel_path: The relative path of directory we're processing here
    :type dir_id: The id created for this directory during processing of parent
    """
    dirEntry = dir_entries[rel_path]
    ucls_dir = UCLSDirectory(
        Name=dirEntry.name,
        id=dir_id,
        CreationDate=CREATION_DATE,
        Subdirectories=SubdirectoriesType(),
        Sessions=SessionsType(),
    )

    for file in dirEntry.files:
        ucs_xml = os.path.join(rel_path, file.replace(".", "_") + "_ucs.xml")
        ucs_file = UCSFile(None, file)
        ucls_dir.Sessions.add_Session(UCSFile(None,  ucs_xml))

        # Serialize UCS xml for video file
        video = VideoType(
            Title=file,
            Start='PT0S',
            File=ucs_file,
            Type='Primary',
            )
        videos = VideosType([video])

        session = Session(
            Title=file,
            Date=CREATION_DATE,
            Videos=videos,
            )

        outfile = open(os.path.join(root_dir, ucs_xml), 'w')
        outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        session.export(outfile, 0)
        outfile.close()

    # Recursively process subdirs
    for subdir in dirEntry.subdirs:
        dir_id = str(uuid.uuid4())
        subdir_xml = subdir + '_' + dir_id + ".xml"
        ucs_file = UCSFile(None, subdir_xml)
        ucls_dir.Subdirectories.add_Directory(ucs_file)
        process_directory(
            dir_entries, root_dir,
            os.path.join(rel_path, subdir),
            subdir_xml,
            dir_id)

    # All subdirs has been processed for current dir (i.e. its
    # ucls_dir.Subdirectories have been properly populated),
    # ready to write out xml file for it
    outfile = open(os.path.join(root_dir, xml_file), 'w')
    outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
    ucls_dir.export(outfile, 0)
    outfile.close()


def skip_file(file):
    """
    This lets us skip ffprobe checks for common file types that we
    know aren't audio or video files.
    """
    isKnownNonMediaFile = False
    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension.lower()
    if(file_extension == ".txt"
       or file_extension == ".xml"
       or file_extension == ".js"
       or file_extension == ".htm"
       or file_extension == ".html"
       or file_extension == ".gif"
       or file_extension == ".jpg"
       or file_extension == ".jpeg"
       or file_extension == ".pdf"
       or file_extension == ".doc"
       or file_extension == ".docx"
       or file_extension == ".ppt"
       or file_extension == ".pptx"
       or file_extension == ".xls"
       or file_extension == ".xlsx"
       or file_extension == ".exe"
       or file_extension == ".zip"
       ):
        isKnownNonMediaFile = True

    return isKnownNonMediaFile


def updateConsole(files_processed, media_files_found):
    sys.stdout.write("\rTotal files found: %i; Media files found %i"
                     % (files_processed, media_files_found))
    sys.stdout.flush()


def main():
    """
    Crawls a directory for all media (audio or video) files and generates
    UCLS/UCS xml files for them. Each media file becomes a UCS session.
    """
    if sys.version_info[0] < 2:
        raise Exception("The version of Python must 2 or greater.")

    # Check that ffprobe exists, since it's a hard requirement
    if distutils.spawn.find_executable("ffprobe") is None:
        print ('ffprobe not found. For installation information, '
               'visit https://www.ffmpeg.org.')
        exit()

    parser = argparse.ArgumentParser(
        description='Crawls a directory for all media (audio or video) '
                    'files and generates UCLS/UCS xml files for them')
    parser.add_argument(
        '-r',
        '--root-dir',
        default=None,
        dest='root_dir',
        required=False,
        help='Full path to the root folder to crawl for media files.')
    parser.add_argument(
        '-n',
        '--library-name',
        default='UCLS migration',
        dest='library_name',
        required=False,
        help='Name to use in the generated library.xml')
    parser.add_argument(
        '-l',
        '--log-file',
        dest='log_file',
        required=False,
        help='Filename of output log file. Based on current time if '
             'not overridden')

    args = parser.parse_args()

    log_file = lib.logging.create_log_file(args)
    root_dir = args.root_dir
    dir_entries = dict()
    library_dir = DirEntry('')

    log_file.write('Crawling files in ' + root_dir + ' ...\n')

    files_processed = 0
    media_file_count = 0
    for dir, dirs, files in os.walk(root_dir, topdown=False):
        for file_name in files:
            updateConsole(files_processed, media_file_count)
            files_processed += 1

            file_path = os.path.join(dir, file_name)
            if not skip_file(file_path) and is_media_file(file_path):
                log_file.write('Media file found: ' + file_path + '\n')
                media_file_count += 1

                # Add this file to DirEntry.files list for current dir
                rel_dir_path = os.path.relpath(dir, root_dir)
                dir_name = os.path.basename(rel_dir_path)
                if rel_dir_path not in dir_entries:
                    dir_entries[rel_dir_path] = DirEntry(dir_name)
                dir_entries[rel_dir_path].files.append(file_name)

                # Now walk up the file's directory path and update subdirs for
                # each dir path, e.g. if relative file path under library root
                # dir was foo\bar\foobar\foo.mp4, then this will update subdirs
                # for the following DirEntry items:
                # [dir path to update for, subdir to add]
                #
                # ['', 'foo'], ['foo','bar'], ['foo\bar', 'foobar']
                subdir = dir_name
                rel_par_path = get_parent_dir(rel_dir_path)
                while rel_par_path is not '':
                    dir_name = os.path.basename(rel_par_path)
                    if rel_par_path not in dir_entries:
                        dir_entries[rel_par_path] = DirEntry(dir_name)

                    ucls_par_dir = dir_entries[rel_par_path]
                    if(subdir not in ucls_par_dir.subdirs):
                        ucls_par_dir.subdirs.append(subdir)

                    subdir = dir_name
                    rel_par_path = get_parent_dir(rel_par_path)

                # After while loop above, subdir would now be a top level
                # folder under the library root dir. Add it as a subdir of
                # the uber library DirEntry
                if(subdir not in library_dir.subdirs):
                    library_dir.subdirs.append(subdir)

    #
    # Generate UCLS/UCS xml files from the complete
    # information we now have on files and folders
    #

    ucls_lib = Library()
    ucls_lib.Name = args.library_name
    ucls_lib.CreationDate = CREATION_DATE
    ucls_lib.UniqueIdentifier = uuid.uuid4()
    ucls_lib.RootDirectories = RootDirectoriesType()

    # Recursively process each root directory (i.e. top level
    # folders under the passed in root dir)
    for root_dir_name in library_dir.subdirs:
        dir_id = str(uuid.uuid4())
        xml_file = root_dir_name + '_' + dir_id + ".xml"
        ucs_file = UCSFile(None, xml_file)
        ucls_lib.RootDirectories.add_RootDirectory(ucs_file)
        process_directory(
            dir_entries,
            root_dir,
            root_dir_name,
            xml_file,
            dir_id)

    # All directories processed, can now generate UCLS library xml
    outfile = open(os.path.join(root_dir, 'library.xml'), 'w')
    outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
    ucls_lib.export(outfile, 0)
    outfile.close()

    print(', check logs for complete list.\r')
    print('Done')


if __name__ == '__main__':
    main()
