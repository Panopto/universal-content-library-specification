import io
from time import gmtime, strftime


def create_log_file(args):
    """
    Set up a file for logging
    """
    currenttime = strftime("%Y-%m-%d %HH-%MM-%SS", gmtime())
    if args.log_file is None:
        log_file = open(currenttime + '.log', 'w')
    else:
        log_file = open(args.log_file, 'a')

    log_file.write("Executing program at " + currenttime + '\n')

    return log_file
