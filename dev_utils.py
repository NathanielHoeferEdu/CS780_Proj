import os
import sys
import time
import logging


def config_logger(output_path, level=logging.DEBUG):
    """Configure logger to output .log file with specified logging level."""
    logger = logging.getLogger('dev')
    logger.setLevel(level)
    ch = logging.FileHandler(filename=output_path, mode='w')
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    print("Logs being stored as '{}'".format(output_path))

    return logger


class ProgressBar(object):

    TOTAL_BAR_LENGTH = 65.

    def __init__(self, total):
        _, term_width = os.popen('stty size', 'r').read().split()
        self.term_width = int(term_width)

        self.last_time = time.time()
        self.begin_time = self.last_time

        self.total = total

    def progress(self, current, msg=None):

        # No total specified - don't continue
        if not self.total:
            return

        if current == 0:
            self.begin_time = time.time()  # Reset for new bar.

        cur_len = int(self.TOTAL_BAR_LENGTH*current/self.total)
        rest_len = int(self.TOTAL_BAR_LENGTH - cur_len) - 1

        sys.stdout.write(' [')
        for i in range(cur_len):
            sys.stdout.write('=')
        sys.stdout.write('>')
        for i in range(rest_len):
            sys.stdout.write('.')
        sys.stdout.write(']')

        cur_time = time.time()
        step_time = cur_time - self.last_time
        self.last_time = cur_time
        tot_time = cur_time - self.begin_time

        L = []
        L.append('  Step: %s' % self.format_time(step_time))
        L.append(' | Tot: %s' % self.format_time(tot_time))
        if msg:
            L.append(' | ' + msg)

        msg = ''.join(L)

        max_msg_len = self.term_width - self.TOTAL_BAR_LENGTH - 3
        max_msg_len = int(max_msg_len)
        # print max_msg_len
        if len(msg) > max_msg_len:
            msg = "".join([msg[:max_msg_len - 3], "..."])

        sys.stdout.write(msg)
        for i in range(self.term_width-int(self.TOTAL_BAR_LENGTH)-len(msg)-3):
            sys.stdout.write(' ')

        # Go back to the center of the bar.
        for i in range(self.term_width-int(self.TOTAL_BAR_LENGTH/2)+2):
            sys.stdout.write('\b')
        sys.stdout.write(' %d/%d ' % (current, self.total))

        if current <= self.total:
            sys.stdout.write('\r')
        else:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def format_time(self, seconds):
        days = int(seconds / 3600/24)
        seconds = seconds - days*3600*24
        hours = int(seconds / 3600)
        seconds = seconds - hours*3600
        minutes = int(seconds / 60)
        seconds = seconds - minutes*60
        secondsf = int(seconds)
        seconds = seconds - secondsf
        millis = int(seconds*1000)

        f = ''
        i = 1
        if days > 0:
            f += str(days) + 'D'
            i += 1
        if hours > 0 and i <= 2:
            f += str(hours) + 'h'
            i += 1
        if minutes > 0 and i <= 2:
            f += str(minutes) + 'm'
            i += 1
        if secondsf > 0 and i <= 2:
            f += str(secondsf) + 's'
            i += 1
        if millis > 0 and i <= 2:
            f += str(millis) + 'ms'
            i += 1
        if f == '':
            f = '0ms'
        return f