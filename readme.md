This projects is for Gregory O'Hagan's application to Venue King.

## Requirements:

* Python 3.X (tested using python 3.11)
* aiohttp ("pip install aiohttp[speedups]")


## Assumptions:

Here are the assumptions made about the requirements when writing this script.
If these assumptions are false, please let me know and I'll update this project to match
* The web calls need to be handled efficiently in terms of memory,
but the contents of the output file do fit in memory.
If this isn't true, then the output file would need to be written in chunks with guaranteed unique ids
instead of amalgamating the results before writing the output file.
