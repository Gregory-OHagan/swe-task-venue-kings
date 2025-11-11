This project is for Gregory O'Hagan's application to Venue King.

## Instructions

Run the file "main.py" using Python.

## Requirements:

* Python 3.X (tested using python 3.11)
* aiohttp ("pip install aiohttp[speedups]")


## Assumptions:

Here are the assumptions made about the requirements when writing this script.
If any of these assumptions are incorrect, please let me know and I'll update this project to match
* The web call responses need to be handled efficiently in terms of memory,
but the contents of the output file do fit in memory.
If this isn't true, then the output file would need to be written in chunks with guaranteed unique ids
instead of amalgamating the results before writing the output file.
Unless this is explicitly necessary, using json.dump is far better than writing the file by hand.
If it was necessary, it would also require a rework of the request timing to avoid the case of requests
being sent faster than they are processed, stacking up queued tasks in memory.
* There are no duplicate items. If there were, duplicate items within one source would be easy
to add without hurting runtime by changing the list of items to a dictionary of items.
If there were duplicates between sources, this would additionally require the unified ids to
be created in a way to match items across sources.
* The requirements specified that web requests would return paginated data with 20 items.
The request functions are mocked to provide this behaviour as the sample sources do not provide this,
but the rest of the implementation would handle larger pages without issue (up to memory limits).
* Object fields that are not present in the provided/mock data should be set to None/null.
* The output data file format is made to match the format of the sample, but the json
includes some assumptions to do so while including the requested information.


## Areas for Future Improvements

If I was planning to maintain and reuse this project in the future (as opposed to using it as a one-off script),
here are some areas I'd change to support this.

* The endpoints are currently hard-coded. I would update this to allow selecting a sublist of implemented
endpoints through a config file.


## Notes on Threading implementation

The threading implementation is entirely unnecessary given the asyncio implementation in the project.
The reason for this is because:

(a) if the processing time is (potentially) less than the web request rate, it is superfluous
as the requests from different sources are already asynchronously handled.

(b) if the processing time is (potentially) greater than the web request rate, the safeguards
against memory overuse will kick in and slow down the web request rate, resulting in no
performance gains

If I was designing this for production, given my current understanding of the requirements,
I would use the asyncio but not the threading library.

Hypothetically, if this project was given a version of Python without the global interpreter
lock (GIL) and was cpu bound in terms of processing the inputs, this threading implementation
would then give performance gains.
