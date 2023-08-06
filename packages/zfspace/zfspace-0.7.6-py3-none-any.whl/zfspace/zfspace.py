#!/usr/bin/env python3
""" Usage: zfspace <dataset name>

Console tool to find occupied pool space in ZFS on Linux.

The main purpose is to visualize missing space that is hidden in snapshots.
ZFS only shows space occupied by a snapshot's unique data and doesn't
show space occupied by data referenced in 2+ snapshots. Therefore searching
for missing space can be troublesome. zfspace helps with that and tries to be
explanatory for inexperienced users.
"""

import os
import math
import difflib
import argparse
import copy

# Version is updated with bump2version helper. Do not update manually or you will lose sync
__version__ = '0.7.6'
filter_level = 0.368  # This value will be overwritten by default argparse filter value

term_format = dict(PURPLE='\033[95m', CYAN='\033[96m', DARKCYAN='\033[36m', BLUE='\033[94m',
                   GREEN='\033[92m', YELLOW='\033[93m', RED='\033[91m', BOLD='\033[1m',
                   UNDERLINE='\033[4m', WHITEBOLD='\033[1;37m', END='\033[0m')


def size2human(size_bytes: int, fmt='full'):
    """Convert size in bytes into human readable format like MiB or GiB.
    Sizes up to YiB (>10^24) are supported. The result is rounded to 2-4 meaningful digits.

    :param int size_bytes: The bytes number that needs to be put into human readable form
    :param str fmt: Output format specifier. Default value 'full'.
        Human readable form with several digits, and spaces is 'full'.
        Computer and human readable form with no fractional part, no space, and one letter size is 'short'.
    :return: String representing size (14.1 GiB for full format)
    :rtype: str
    """
    if fmt not in ['full', 'short']:
        raise ValueError('Unknown format {}.'.format(fmt))
    if size_bytes == 0:
        return '0 B'
    size_name = ('B', 'kiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    short_size_name = ('B', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    order = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, order)
    digits = int(math.floor(math.log(size_bytes / p, 10)))  # Calculate meaningful digits to keep length in 4 characters
    if fmt == 'short':
        s = int(round(size_bytes / p))
        return '{}{}'.format(s, short_size_name[order])
    elif fmt == 'full':
        if digits > 1:  # Only integer output is suitable for values over 100.
            s = int(round(size_bytes / p))
            return '{} {}'.format(s, size_name[order])
        else:  # Limit accuracy to 1 or 2 fractional decimals to get representations 1.23 and 12.3 and not 12.34
            s = round(size_bytes / p, 2 - digits)
            return '{:.4} {}'.format(s, size_name[order])


def split_terminal_line(term_columns, slices=0, fractions_list=None, padding=0):
    # Convert slices into fractions_list
    if fractions_list is None:
        fractions_list = []
    if len(fractions_list) == 0:
        if slices == 0:
            raise TypeError('At least one parameter must be set. '
                            'Either slices > 0 or fractions_list must be a not empty list.')
        else:
            fractions_list = [1/slices] * slices
    else:
        slices = len(fractions_list)

    # Normalize fractions_list
    fractions_list = [float(i) / sum(fractions_list) for i in fractions_list]

    # Calculate fractional space for strings considering (slices + 1) separators and padding
    start_pos = list()
    end_pos = list()
    writable_columns = (term_columns - slices - 1 - padding * 2)
    pos = 1 + padding
    for frac in fractions_list:
        start_pos.append(int(pos))
        pos += writable_columns * frac
        end_pos.append(int(pos))
        pos += 1  # space for separator
    return start_pos, end_pos


def print_in_line(string, str_length, emphasis=None):
    """Prints centered output, considering that console cursor is in the beginning of the span to print.
    Prints . or nothing if there is not enough space to print wrole string

    :param string: String to print
    :param int str_length: Integer number of symbols to fill with string
    :param string emphasis: Make terminal text highlighted, colored, bold or whatever, based on term_format dict
    :return: None
    """
    if emphasis is not None and emphasis not in term_format:
        raise ValueError('Incorrect emphasis passed to print_in_line.')
    if len(string) > str_length:
        string = '.' * str_length
    if str_length == 0:
        return
    len_format = '{:^' + '{:d}'.format(str_length) + 's}'  # Prepare format string with desired width
    if emphasis is None:
        print(len_format.format(string), end='')
    else:
        print(term_format[emphasis] + len_format.format(string) + term_format['END'], end='')


def shorten_names(names_list, length_list):
    """ Finds common part of the names to shorten it so that it will fit into corresponding length
    :param names_list: A list of strings to shorten
    :param length_list: A list of lengths for names to fit in
    :return: List of shortened names
    """
    # Basic sane check
    if len(names_list) <= 1:
        return names_list

    # Find candidates for removal by first two names
    match = difflib.SequenceMatcher(None, names_list[0], names_list[1])
    # We save size with sequences longer than '...'
    ops = list(filter(lambda element: element[2] - element[1] >= 3, match.get_opcodes()))
    candidates = [names_list[0][c[1]:c[2]] for c in sorted(ops, key=lambda x: x[2] - x[1], reverse=True)]

    # Run through all candidates
    winner = ''
    for cnd in candidates:
        all_contain = True  # Let's suppose all names contain the candidate
        for name in names_list[2:]:
            if cnd not in name:
                all_contain = False  # Alas this name doesn't contain the candidate
                break
        if all_contain:  # We have a winner
            winner = cnd  # Store the winner
            break  # No need to continue
    ret = []
    if winner != '':
        for index, name in enumerate(names_list):
            excess = len(name) - length_list[index]
            if excess > 0:
                ret.append(name.replace(winner[-(excess+3):], '...'))
            else:
                ret.append(name)
        return ret
    else:
        return names_list


class DivBar:
    """
    An object to draw console visual representations of parts as bars forming a whole
    """
    def __init__(self):
        self.term_columns, self.term_lines = os.get_terminal_size()

    def print_dict(self, names_list):
        """ Print a bar in terminal divided into segments. It helps to visualize the differences in sizes.

        :param names_list: a list of tuples consisting of a name of a segment and its integer size
        :return: None
        """
        names, sizes = zip(*names_list)
        start, end = split_terminal_line(self.term_columns, fractions_list=sizes)
        for i, name in enumerate(names):
            print('|', end='')
            print_in_line(name + ' ' + size2human(sizes[i]), end[i] - start[i])
        print('|')  # New line afterwards

    def print_hr(self):
        print('-'*self.term_columns)


class ZfsBridge:
    zfs_path = '/sbin/zfs'

    def __init__(self):
        # Check whether zfs is present in the system
        if not os.path.isfile('/sbin/zfs'):
            raise FileNotFoundError(
                '{} is not found on your computer. Is ZFS-on-Linux installed?'.format(self.zfs_path))
        # Check and store existing ZFS datasets to be able to explain the user's input errors
        stream = os.popen('{} list'.format(self.zfs_path))
        output = stream.read().split('\n')[1:-1]  # Take all strings of ZFS listing except first and last one
        self.zfs_datasets = list()
        for string in output:
            self.zfs_datasets.append(string.split(' ')[0])

    @staticmethod
    def strip_filesystem_name(snapshot_name: str):
        """Given the name of a snapshot, strip the filesystem part.

        We require (and check) that the snapshot name contains a single
        '@' separating filesystem name from the 'snapshot' part of the name.
        :param str snapshot_name: A standard single snapshot name with trailing filesystem and @ symbol
        :return: The name of the snapshot that goes after @ symbol
        :rtype: str
        """
        assert snapshot_name.count('@') == 1
        return snapshot_name.split('@')[1]

    def _check_dataset_name(self, dataset_name):
        if dataset_name not in self.zfs_datasets:
            candidate_list = difflib.get_close_matches(dataset_name, self.zfs_datasets, n=1)
            if len(candidate_list) == 1:
                suggest_str = '\nDid you mean using ' + \
                              term_format['WHITEBOLD'] + '"{}"'.format(candidate_list[0]) + term_format['END'] + \
                              ' instead?'
            else:
                suggest_str = ''
            raise ValueError('There is no dataset "{}" in the system.{}'.format(dataset_name, suggest_str))

    @staticmethod
    def _zfs_output_convert(line: str):
        """
        Takes a line of ZFS output and convert it to a list with name and integer values
        :param line: ZFS console output
        :return: list starting with a string and followed by integers with data from input line
        """
        lst = list(filter(None, line.split(' ')))
        return [lst[0], *list(map(int, lst[1:]))]  # Convert to integers all but name of the dataset

    def get_filesystem_mountpoint(self, dataset_name):
        self._check_dataset_name(dataset_name)
        command = '{} get -Hp mountpoint {}'.format(self.zfs_path, dataset_name)
        stream = os.popen(command)
        output = stream.read().split('\t')[2]
        return output

    def get_filesystem_refreservation(self, dataset_name):
        self._check_dataset_name(dataset_name)
        command = '{} get -Hp refreservation {}'.format(self.zfs_path, dataset_name)
        stream = os.popen(command)
        output = stream.read().split('\t')[2]
        return int(output)

    def get_children_summary(self, dataset_name):
        self._check_dataset_name(dataset_name)
        command = '{} list -d 1 -p -S used -o space {}'.format(self.zfs_path, dataset_name)
        stream = os.popen(command)
        output = stream.read().split('\n')[:-1]  # Get all lines except the last one, that is empty
        names = list(filter(None, output[0].split(' ')))
        children = list()
        for child in output[1:]:
            data = self._zfs_output_convert(child)
            if data[0] == dataset_name:  # Filter out the parent
                continue
            children.append(list(zip(names, data)))
        return children

    def get_snapshot_names(self, dataset_name):
        self._check_dataset_name(dataset_name)
        command = '{} list -H -d 1 -t snapshot -s creation -o name {}'.format(self.zfs_path, dataset_name)
        stream = os.popen(command)
        output = stream.read().split('\n')[:-1]  # Take all strings of ZFS snapshot listing except last one
        return list(map(self.strip_filesystem_name, output))

    def _get_snapshot_range_space(self, dataset, first_snap, last_snap):
        command = '{} destroy -nvp {}@{}%{}'.format(self.zfs_path, dataset, first_snap, last_snap)
        stream = os.popen(command)
        return stream.read().split('\n')[-2].split('\t')[-1]  # Take the second part of the last line

    def get_snapshots_space(self, dataset_name, snapshot_list):
        self._check_dataset_name(dataset_name)
        used_matrix = [[0 for _ in range(len(snapshot_list))] for _ in range(len(snapshot_list))]
        for end, end_name in enumerate(snapshot_list):
            for start, start_name in enumerate(snapshot_list):
                if start <= end:
                    used_matrix[end - start][start] = \
                        int(self._get_snapshot_range_space(dataset_name, start_name, end_name))
        # The occupied space we have in the matrix shows how much space will be freed if we delete the combination
        # While this might be useful to make a decision, this does not show used space hierarchy
        # Let's calculate the space occupied by snapshots combination and not by its subsets

        # Save this matrix because it is also good for analysis
        would_free_matrix = copy.deepcopy(used_matrix)

        # Now define a helper function for triangle substraction
        def substract_children(matrix, startx, starty):
            for x in range(startx):
                for y in range(starty, starty + startx - x + 1):
                    matrix[startx][starty] -= matrix[x][y]
        # Then row by row we substract space occupied by subsets
        # This is the correct way
        for i in range(1, len(snapshot_list)):
            for j, _ in enumerate(snapshot_list):
                if j < len(snapshot_list) - i:
                    substract_children(used_matrix, i, j)
        # Now we can get the whole snapshots occupied space by summing every matrix cell
        return used_matrix, would_free_matrix

    def get_dataset_summary(self, dataset_name):
        self._check_dataset_name(dataset_name)
        command = '{} list -p -o space {}'.format(self.zfs_path, dataset_name)
        stream = os.popen(command)
        string_list = stream.read().split('\n')[0:2]  # Get names and data strings
        # Split it by spaces and remove empty strings.
        names = list(filter(None, string_list[0].split(' ')))
        data = self._zfs_output_convert(string_list[1])
        return list(zip(names, data))


class SnapshotSpace:
    zfs_max_snapshots = 30

    def __init__(self, dataset_name):
        self.term_columns, self.term_lines = os.get_terminal_size()
        self.zb = ZfsBridge()
        self.snapshot_names = self.zb.get_snapshot_names(dataset_name)
        self.dataset_name = dataset_name
        if len(self.snapshot_names) >= self.zfs_max_snapshots:
            raise ValueError('You have more than {} snapshots in {}. It is too many to show in console.'
                             .format(len(self.snapshot_names), dataset_name))
        self.snapshot_size_matrix, self.would_free_matrix = \
            self.zb.get_snapshots_space(dataset_name, self.snapshot_names)

    def _highlight_matrix(self, highlight_level):
        # Initialize return matrix with False values
        ret = [[False for _ in range(len(self.snapshot_size_matrix[0]))] for _ in range(len(self.snapshot_size_matrix))]

        # Now get total size from would_free_matrix top element
        total_size = self.would_free_matrix[-1][0]

        # Sort sizes to apply highlight_level
        flatten_sizes = [j for sub in self.snapshot_size_matrix for j in sub]
        flatten_sizes.sort(reverse=True)

        # Calculate threshold
        accumulator = 0  # Accumulate sum of sizes, until reach the desired fraction of total size
        threshold = 0  # A variable for threshold
        for s in flatten_sizes:
            accumulator += s
            if accumulator >= total_size * highlight_level:
                threshold = s
                break

        # Fill the matrix, knowing size threshold
        for i, row in enumerate(ret):
            for j, _ in enumerate(row):
                if self.snapshot_size_matrix[i][j] >= threshold:
                    ret[i][j] = True
        return ret

    def _print_line(self, sizes, highlight):
        max_split = len(self.snapshot_names)
        start, end = split_terminal_line(self.term_columns, slices=len(sizes),
                                         padding=int((max_split - len(sizes)) * self.term_columns / max_split / 2))
        print(' ' * (start[0] - 1) + '|', end='')  # shifting for padding
        for i, size in enumerate(sizes):
            print_in_line(size2human(size), end[i] - start[i], emphasis='CYAN' if highlight[i] else None)
            print('|', end='')
        print('')  # New line afterwards

    def _print_names(self):
        start, end = split_terminal_line(self.term_columns, slices=len(self.snapshot_names))
        lengths = [end[i] - start[i] for i, _ in enumerate(start)]
        for i, name in enumerate(shorten_names(self.snapshot_names, lengths)):
            print('|', end='')
            print_in_line(name, lengths[i])
        print('|')  # New line afterwards

    def print_used(self, highlight: float):
        """
        Prints the pyramid of snapshots space occupied. Snapshots names are at the bottom. Sizes are on top.
        They are divided with vertical lines, showing some span, the size corresponds to.
        Each size tells how much space is wasted in a combination, substracting space wasted in its any component.
        :param float highlight: Biggest sizes that add up to the highlight fraction of total size
            will be highlighted.
        :return:
        """
        hl = self._highlight_matrix(highlight)
        for i in reversed(range(1, len(self.snapshot_names))):
            self._print_line(self.snapshot_size_matrix[i][:-i], hl[i][:-i])
        self._print_line(self.snapshot_size_matrix[0], hl[0])  # Last line falls out of general rule
        self._print_names()

    def get_destroy_recommendations(self, recommendations=2):
        # Normalize would free matrix to the number of snapshots to be removed
        free_norm_matrix = [[elem/(index + 1) for elem in row] for index, row in enumerate(self.would_free_matrix)]

        # Now sort the candidates in descending order
        flatten_sizes = [j for sub in free_norm_matrix for j in sub]
        flatten_sizes.sort(reverse=True)

        # Find the threshold for normalize values to neglect if equal or less
        threshold = flatten_sizes[recommendations]

        # Build recommendations knowing the threshold
        answer = ''
        for i, row in enumerate(free_norm_matrix):
            for j, _ in enumerate(row):
                if free_norm_matrix[i][j] > threshold:
                    answer += f'Removing {i+1} snapshot(s) will free {size2human(self.would_free_matrix[i][j])}. ' \
                              f'Use "{self.zb.zfs_path} destroy ' \
                              f'{self.dataset_name}@{self.snapshot_names[j]}%{self.snapshot_names[j+i]}"\n'

        return answer


def deep_analysis(zb: ZfsBridge, dataset_name, name, size):
    global filter_level

    def hello_helper(section_name, size_bytes, text):
        print(term_format['WHITEBOLD'] + section_name + term_format['END'] + ' occupy ' + term_format['CYAN'] +
              size2human(size_bytes) + term_format['END'] + '. ' + text)

    if name == 'USEDSNAP':
        hello_helper('Snapshots', size, 'This space consists of data unique for individual snapshots and data stored in'
                     ' snapshots combinations. Therefore we will use pyramid representation:')
        ss = SnapshotSpace(dataset_name)
        ss.print_used(filter_level)
        print(ss.get_destroy_recommendations(3))

    elif name == 'USEDDS':
        path = zb.get_filesystem_mountpoint(dataset_name)
        if not path.endswith('/'):
            path = path + '/'
        hello_helper('Files in {}'.format(path), size,
                     f"""Run "du -xsh {path}*" preferrably by root user. \
This will calculate the occupied space for each file and subfolder in your ZFS filesystem, \
excluding other filesystem mounts like network mounts and ZFS children filesystems.
It will not exclude folders with mountpoints right in the {path}. \
You will have to exclude them separately with du --exclude option. \
Running as a regular user will skip some directories with "Permission denied" error.""")

    elif name == 'USEDREFRESERV':
        refres = zb.get_filesystem_refreservation(dataset_name)
        hello_helper('Refreservation option', size,
                     'Current refreservation value is {}. '.format(size2human(refres)) +
                     'Limit it to the current requirement with "{} set refreservation={} {}".'.format(
                         zb.zfs_path, size2human(refres - size, fmt='short'), dataset_name
                     )
                     )

    elif name == 'USEDCHILD':
        hello_helper('Children ZFS filesystems', size, 'The following children may be considered to be cleaned:')
        dv = DivBar()
        used_all_children = zb.get_dataset_summary(dataset_name)[6][1]
        part_count = 0
        for child in zb.get_children_summary(dataset_name):
            part_count += child[2][1] / used_all_children  # Normalized sum
            print(term_format['BOLD'] + str(child[0][1]) + term_format['END'] +
                  term_format['CYAN'] + ' {}'.format(size2human(child[2][1]) + term_format['END'] + ' of ' +
                  term_format['CYAN'] + '{}'.format(size2human(used_all_children)) + term_format['END'] +
                  ' ({:.3}%). '.format(round(100 * child[2][1] / used_all_children, 1)) +
                  'Run "zfspace {}" to make a more detailed analysis:'.format(child[0][1])))
            dv.print_dict(child[3:])
            if part_count > filter_level:
                break

    else:
        raise ValueError('Unknown ZFS {} space user: {}'.format(dataset_name, name))


def main():
    parser = argparse.ArgumentParser(description='analyse space occupied by a ZFS filesystem.')
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-f', '--filter', type=float,
                        help='Threshold in range [0,1] to filter out all less significant parts on analysis.',
                        default=0.632)
    parser.add_argument('dataset_name', type=str, help='a ZFS dataset name for analysis.')

    args = parser.parse_args()
    if args.filter > 1 or args.filter < 0:
        raise ValueError('The filter cannot be out of [0,1] range.')
    global filter_level
    filter_level = 1 - args.filter

    # Initializing ZFS helper class
    zb = None  # Fix warnings about possible usage before initialization
    try:
        zb = ZfsBridge()
    except Exception as err:
        print(err)
        exit()

    # Starting with dataset analysis
    summary = zb.get_dataset_summary(args.dataset_name)

    # Printing user intro
    dv = DivBar()
    dv.print_hr()
    print('Analyzing ' + term_format['WHITEBOLD'] + args.dataset_name + term_format['END'] + ' ZFS dataset. '
          'Total used space is ' + term_format['CYAN'] + size2human(summary[2][1]) + term_format['END'] + '. '
          'It is divided in the following way:')
    dv.print_dict(summary[3:])

    # Find the most important parts in summary according to filter level
    summary_sorted = sorted(summary[3:], key=lambda x: -x[1])
    part_count = 0
    for item in summary_sorted:
        part_count += item[1] / summary[2][1]  # Normalized sum
        try:
            dv.print_hr()
            deep_analysis(zb, args.dataset_name, *item)  # Analyze each part individually
        except Exception as err:
            print(err)
            raise
        if part_count > filter_level:
            break
