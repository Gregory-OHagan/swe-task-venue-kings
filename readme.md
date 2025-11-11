This project is part of Gregory O'Hagan's application to Venue King.
Don't hesitate to reach out to me at gregoryrohagan@gmail.com if you have any questions.

Date: November 2025


## Instructions

Run the file "main.py" using Python. The json output is saved as "results.json"

Tests are in the Python files that start with "test_". I've used PyCharm's default tools for picking
up the tests (every function starting with "test") which I believe is also standard with pytest


## Requirements:

* Python 3.X (tested using python 3.11)
* aiohttp ("pip install aiohttp[speedups]")


## Assumptions:

Here are the assumptions made about the requirements when writing this script.
If any of these assumptions are incorrect, please let me know and I'll update this project to match.
Some of these come from the project specifications, and some come from observations of the sample data.

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
be created in a way to match items across sources, or some post-processing to find these.
* The requirements specified that web requests would return paginated data with 20 items.
The request functions are mocked to behave like this as the sample sources do not provide this,
but the rest of the implementation would handle arbitrary page sizes without issue (up to memory limits).
* Object fields that are not present in the provided/mock data are set to None/null.
* The output data file format is made to match the format of the sample, but the json
includes some assumptions to do so while including the requested information.
* The delay between web requests is generally larger than the time to process the previous call.
This isn't strictly necessary, but if false, will result in inefficient memory usage as tasks
queue up. If this became a performance bottleneck, it could be fixed by having each source wait
until it's previous request is processed before making a new one, but this would largely defeat
the purpose of using the threading library in this implementation.


## Code Structure

As this is a small project, most of the core code is in "main.py"

The function "main" provides the required setup and config loading to start, and then
calculates some basic statistics at the end.

Each data source has a "request_source_<x>" function that handles the web request itself.
The only processing of the response done in these functions is to standardize the json
returned, which in some cases includes mocking the data a bit to simulate pagination.
If this project grows, these functions would move to a helper file.

The function "get_data", asynchronously called from the main function for each data source,
handles determining when to make web requests and sends the results from the web request to
a worker thread

The function "process_one_set" is called using a worker thread on each successful web request.
Processing is very quick in this demo, so you can add a time.sleep() to this function if you
wish to simulate data processing taking time.

When processing is complete, the function "write_output" creates a json output file,
"results.json".

threading_helpers.py contains two objects to help with multithreading:
1. A data object with threadsafe modifier functions, used to coordinate results between threads.
Primarily used by the worker threads to coordinate and create output
2. A thread pool object that queues, starts, and cleans up the worker threads.
This is set up once and used by the "get_data" function calls to run their work.


## Notes

The bonus configuration file is included (config.json), which contains variables to set any of the following:
* maximum number of worker threads (note that the main thread is not included in this number)
* web request timeout
* web request maximum retries and several factors for backoff behaviour
* web request maximum rate

Time between web requests was chosen instead of maximum requests per second. This technically
makes the requests somewhat slower, but is a more consistent rate limiter.


## Areas for Future Improvements

If I was planning to maintain and reuse this project in the future (as opposed to using it as a one-off script),
here are some areas I'd change to support this.

* The endpoints are currently hard-coded. I would update this to allow selecting a sublist of implemented
endpoints through a config file.
* The included tests are functional and useful, but not comprehensive (notably, the function "main" isn't covered).
I would increase the code coverage of the tests.

