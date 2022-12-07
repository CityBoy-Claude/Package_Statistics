# Package_Statistics
A python command line tool that takes the architecture (amd64, arm64, mipsel etc.) as an argument and downloads the compressed Contents file associated with it from the [Debian mirror](http://ftp.uk.debian.org/debian/dists/stable/main/), and parse the file and output the statistics of the top 10 packages that have the most files associated with them.
## Requirment
python 3.6 or newer
## Sample Execution & Output
The usage of the tool is command like
```
./package_statistic.py <architecture>
```
For example, if run using
```
./package_statistic.py amd64
```
output similar to
```
   package name                         number of files
1. devel/piglit                                 51784 
2. science/esys-particle                        18015 
......
10. kernel/linux-headers-5.10.0-16-amd64        6150
```
will be displayed. Note that the precision results will vary by architecture and mirror. After running, the Content file of the architecture will be stored at `./contents/`.

If run without the command line argument to specify the architecture, using
```
./package_statistic.py
```
the following usage message will be displayed.
```
Error: Missing architecture!
Usage: ./package_statistic.py <architecture>
```
If run with an invalid architecture name, the valid architecture names will be shown, the output may be similar to
```
Error: [invalid_name] is not a valid architecture.
Valid architectures:  ['mipsel', 'armhf', 'mips64el', 'amd64', 'i386', 'ppc64el', 's390x', 'armel', 'arm64']
```
If run with a valid architecture name, but there is no Contents files from the Debian mirror, an error like
```
HTTP Error 404: Not Found
Error: There is no Content for the valid_but_no_content architecture.
```
will be thrown.
## Process
I firstly divide the process into 4 steps, Preprocess, Download, Count and Output
### Preprocess
1. Make sure the usage if the tool is valid, including the architecture argument. The error outputs are mentioned in the previous section.
2. Create the `./contents/` directory, if not exit, to store the Content files.
### Download
1. Make sure the architecture name are valid and the resource is available. The error outputs are mentioned in the previous section.
2. If the Content file of the target architecture is not in `./contents`, download it from the Debian mirror with `urllib.request`.
3. Decompress the downloaded gzip file.
4. To save disk space, delete the gzip file and only remain the Content file.
### Count
1. Use a `dict()` to store the number of files associated with each package.
2. Loop each line in the target Content file.
   * Skip the first row if the columns are "FILE" and "LOCATION".
   * Split the second column of each row by comma to get a list of package names.
   * Based on the [rule of Contents indices](https://wiki.debian.org/DebianRepository/Format?action=show&redirect=RepositoryFormat#A.22Contents.22_indices), deprecate the package name including $AREA field.
   * Add up the number of associated files of each vaild package name in the list.
### Output
1. To get the top 10 packages that have the most files associated with them, I plan to use heap and its `nlargest()` method, because the time complexity of the method is `O(m*log(n))` where `m` is the number of unique package and `n` is the size of the heap. Here, `n` is a constant,10, so the time complexity is `O(m)` and the space complexity is `O(1)`. 
2. To customize the comparing method of the heap, I use a class `Package_Frequency` to store the package names and the number of associated files, and overload the `__lt__()` method.
3. Print out the result as the required format.

## Time I spend
Basic worflow: 30-45 mins
Optimization & fixing details: ~30 mins
Comments & Document: ~60 mins
