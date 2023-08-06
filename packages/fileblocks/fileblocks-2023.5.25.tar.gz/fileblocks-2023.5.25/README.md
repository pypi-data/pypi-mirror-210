# fbi

Strings can be one of the quickest ways to analyze unknown binaries and memory images, even with corrupted acquisitions for low-hanging fruit.

```
FBI - Walk the line, Byte by Byte Analysis

options:
  -h, --help            show this help message and exit
  -b BLOCKS, --blocks BLOCKS
                        Input Filename
  -d, --download        Download Bloom Filter
  -o OUTPUT, --output OUTPUT
                        Output Directory
  -v, --version         show program's version number and exit
```

### CHALLENGES

The first challenge is data encoding, as several applications only display ASCII characters with the potential for Unicode and UTF-8 to exist.

The second hurdle is that memory does not have the traditional data structures you would find during regular disk forensics with file systems (sectors) and operating systems (clusters).

Finally is the exponentially growing volume of data requiring analysis.

### SOLUTIONS

Python can natively handle UTF-8 decoding with Unicode exception handling.

Data structures get trickier since the input file has to be walked byte by byte, which can be resource-intensive, requiring threading to help performance.

The program hashing that much data required using the BLAKE3 cryptographic hash function, adding a Rust programming language dependency to speed things up.

https://github.com/BLAKE3-team/BLAKE3

### DATASET

Blocks of 512 bytes that match sectors found on the filesystem identify matches.  Like MD5 and SHA256, BLAKE3 has a hash value for empty files that trims whitespace to a single character in the extracted output.

```AF1349B9F5F9A1A6A0404DEA36DCC9499BCB25C9ADC112B7CC9A93CAE41F3262```

GetBlocks generates the dataset with the block (sector) hashes only available in BLAKE3 format.

https://github.com/4n6ir/getblocks

A pipeline runs every hour to determine if AWS has released any new verified Amazon Machine Image (AMI) to harvest artifacts with the current coverage available.

https://static.matchmeta.info/amazonami.json

### DISTRIBUTION

A download option in the command line interface (CLI) stores the bloom filter in the user's home directory.

```
fbi -d
```

Please use this link to download the bloom filter for offline analysis.

https://static.fileblock.info/fbi.bloom

You will be able to verify the integrity of the bloom filter by using the provided SHA256 hash value.

https://static.fileblock.info/fbi.sha256

It is available for download if you're interested in the raw data.

https://b3.lukach.io/amzn/sector

API keys are available using the self-registration process.

https://store.lukach.io/l/b3

### ANALYSIS

The analyzed file allows both the absolute and relative location.

```
fbi -b /usr/bin/df
```

or

```
fbi -b df
```

### OUTPUT

Output writes to the current working with **fbi-** appended to the front of the analyzed filename or a specified directory.

```
fbi -b /usr/bin/df -o /tmp
```

### REQUIREMENTS

```
curl https://sh.rustup.rs -sSf | sh -s -- -y
source "$HOME/.cargo/env"
```

### INSTALLATION

```
pip install fileblocks
```

### DEVELOPMENT

```
python setup.py install --user
```