import os
import sys
import urllib.request
import gzip
from collections import defaultdict
from heapq import heappop, heappush

contents_dir = './contents'  # The dictionary stores the Contents indices files
# Url of the Debian mirror
mirror_url = "http://ftp.uk.debian.org/debian/dists/stable/main/"
architectures_set = set(['amd64', 'arm64', 'armel', 'armhf',
                         'i386', 'mips64el', 'mipsel', 'ppc64el', 's390x'])  # set of the names of architectures


class Package_Frequency:    # Class to store package and number of files associated with it
    def __init__(self, pkg_name, freq):
        self.pkg_name = pkg_name
        self.freq = freq

    def __lt__(self, other):    # Overload the operator for customizing heap
        if self.freq != other.freq:
            return self.freq < other.freq   # Compare the number of associated files first
        # Compare the package name if the number of associated files are the same
        return self.pkg_name > other.pkg_name


def download_content(architecture):
    '''
        Download the specific Contents indices file

        param architecture: str, the name of the architecture
        return: 
            str, the local path of the Content indices file if the architecture is valid
            None, if not
    '''
    if architecture not in architectures_set:
        print("Error: %s is not a valid architecture." % architecture)
        return None
    # the name of the Contents indices file
    content_name = 'Contents-%s' % (architecture)
    # the local path of the file
    content_path = os.path.join(contents_dir, content_name)
    if os.path.exists(content_path):    # already download the file
        return content_path
    try:
        urllib.request.urlretrieve(
            mirror_url+content_name+'.gz', content_path+'.gz')  # download the gzip file
    except Exception as e:
        print(e)
        print("Error: There is no Content for the %s architecture." % architecture)
        return None
    g_file = gzip.GzipFile(content_path+'.gz')
    open(content_path, "wb+").write(g_file.read())  # decompress the gzip file
    g_file.close()
    os.remove(content_path+'.gz')   # delete the decompress file
    return content_path


def deprecated_package_name(pkg_name):
    # TODO deprecated the whole pkg or only the area?
    return True if len(pkg_name.split('/')) > 2 else False


def package_counter(content_path):
    '''
    Count the number of assocaited files of each package in the Content indices file.

    param content_path: str, the local path of the Content indices file
    return: dict, the hashmap of (package name, the number of assocaited files) pair
    '''
    pkg_freq = defaultdict(int)
    try:
        with open(content_path) as pkg_file:
            for line in pkg_file:
                # split the packages and multiple package names
                pkgs = line.split()[-1].split(',')
                for pkg in pkgs:
                    if deprecated_package_name(pkg):
                        continue
                    pkg_freq[pkg] += 1
    except Exception as e:
        print(e)
        print("Error: The Content path %s is invalid." % content_path)
        exit()
    return pkg_freq


def print_top_package(pkg_freq, size=10):
    '''
    Print out the top <size> packages that have the most files associated with them

    param pkg_freq: dict, the hashmap of the number of assocaited files of each package
    param size: the number of the top packages to be printed
    '''
    top_pkg_heap = []   # we use heap to store the top <size> packages
    for pkg_name, freq in pkg_freq.items():
        heappush(top_pkg_heap, Package_Frequency(pkg_name, freq))
        if len(top_pkg_heap) > size:    # fixed the size of the heap
            heappop(top_pkg_heap)
    ans = []
    while top_pkg_heap:
        # record the packages in the final heap
        ans.append(heappop(top_pkg_heap))
    for i in range(len(ans)-1, -1, -1):
        # print out the records based on the requirement
        print("%i. %s\t%s " % (len(ans)-i, ans[i].pkg_name, ans[i].freq))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Missing architecture!")
        print("Usage: %s <architecture>" % (sys.argv[0]))
        exit()
    architecture = sys.argv[1]  # get the architecture argument
    if not os.path.exists(contents_dir):
        os.makedirs(contents_dir)
    content_path = download_content(architecture)
    if not content_path:    # download fails
        exit()
    pkg_freq = package_counter(content_path)
    if not pkg_freq:    # no valid files
        exit()
    print_top_package(pkg_freq)  # print out the result
