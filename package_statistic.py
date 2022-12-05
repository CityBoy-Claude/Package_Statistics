import os
import sys
import urllib.request
import gzip
from collections import defaultdict
from heapq import heappop, heappush

contents_dir = './contents'
mirror_url = "http://ftp.uk.debian.org/debian/dists/stable/main/"
architectures_set = set(['amd64', 'arm64', 'armel', 'armhf',
                         'i386', 'mips64el', 'mipsel', 'ppc64el', 's390x'])


class Package_Frequency:
    def __init__(self, pkg_name, freq):
        self.pkg_name = pkg_name
        self.freq = freq

    def __lt__(self, other):
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.pkg_name > other.pkg_name


def download_content(architecture):
    if architecture not in architectures_set:
        print("Error: %s is not a valid architecture." % architecture)
        return None
    content_name = 'Contents-%s' % (architecture)
    content_path = os.path.join(contents_dir, content_name)
    if os.path.exists(content_path):
        return content_path
    try:
        urllib.request.urlretrieve(
            mirror_url+content_name+'.gz', content_path+'.gz')
    except Exception as e:
        print(e)
        print("Error: There is no Content for the %s architecture." % architecture)
        return None
    g_file = gzip.GzipFile(content_path+'.gz')
    open(content_path, "wb+").write(g_file.read())
    g_file.close()
    os.remove(content_path+'.gz')
    return content_path


def deprecated_package_name(pkg_name):
    return True if len(pkg_name.split('/')) > 2 else False


def package_counter(content_path):
    pkg_freq = defaultdict(int)
    try:
        with open(content_path) as pkg_file:
            for line in pkg_file:
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
    size = min(len(pkg_freq), size)
    top_pkg_heap = []
    for pkg_name, freq in pkg_freq.items():
        heappush(top_pkg_heap, Package_Frequency(pkg_name, freq))
        if len(top_pkg_heap) > size:
            heappop(top_pkg_heap)
    ans = []
    while top_pkg_heap:
        ans.append(heappop(top_pkg_heap))
    for i in range(size-1, -1, -1):
        print("%i. %s\t\t%s " % (size-i, ans[i].pkg_name, ans[i].freq))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Missing architecture!")
        print("Usage: %s <architecture>" % (sys.argv[0]))
        exit()
    architecture = sys.argv[1]
    if not os.path.exists(contents_dir):
        os.makedirs(contents_dir)

    content_path = download_content(architecture)
    if not content_path:
        exit()
    pkg_freq = package_counter(content_path)
    if not pkg_freq:
        exit()
    print_top_package(pkg_freq)
