import asyncio
import aiohttp

import datetime
import json
import time

from threading_helpers import *


async def main():
	start = time.time()

	# Load configuration file
	with open("config.json") as infile:
		config = json.load(infile)
	# TODO: consider adding defaults to loaded config in case of a malformed config file

	pool = MyThreadingPool(config["worker_thread_count"])

	# Process each endpoint asynchronously
	res_a, res_c, res_d = await asyncio.gather(get_data(config, request_source_a, "jsonplaceholder", "a.", pool),
											   get_data(config, request_source_c, "escuelajs", "c.", pool),
											   get_data(config, request_source_d, "dummyjson", "d.", pool))
	res_list = [res_a, res_c, res_d]

	# Wait until all processing threads are complete
	pool.join_all()

	# Calculate combined statistics
	successful_calls = sum([x.successful_requests for x in res_list])
	failed_calls = sum([x.failed_requests for x in res_list])
	success_rate = successful_calls / (successful_calls + failed_calls)

	# Combine the results
	data = []
	errors = []
	for res in res_list:
		data.extend(res.products)
		errors.extend(res.errors)

	# Calculate the processing time
	end = time.time()
	duration = end - start

	# Write the results to an output file
	write_output(data, duration, success_rate, ["a", "c", "d"], errors)


# Fetches data from https://jsonplaceholder.typicode.com/posts, formatted as 20 item pages.
# Note this pagination is intentionally inefficient; it is intended to mock data from a source that is paginated.
# Parameters:
# - session: an open aiohttp.ClientSession().
# - page: the requested page number.
# Returns:
# - the status of the web request return
# - the response json
async def request_source_a(session, page):
	async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
		data = await response.json() if response.status == 200 else []

		# clip the data to simulate pagination.
		start = 20 * (page - 1)
		end = 20 * page
		if start >= len(data):
			return response.status, {'products': []}
		if end < len(data):
			data = data[:end]
		return response.status, {'products': data[start:]}


# Fetches data from https://api.escuelajs.co/api/v1/products, formatted as 25 item pages.
# Note this pagination is intentionally inefficient; it is intended to mock data from a source that is paginated.
# Parameters:
# - session: an open aiohttp.ClientSession().
# - page: the requested page number.
# Returns:
# - the status of the web request return
# - the response json
async def request_source_c(session, page):
	async with session.get("https://api.escuelajs.co/api/v1/products") as response:
		data = await response.json() if response.status == 200 else []
		# clip the data to simulate pagination.
		start = 25 * (page - 1)
		end = 25 * page
		if start >= len(data):
			return response.status, {'products': []}
		elif end < len(data):
			data = data[:end]

		# Format the 'category' value to match the expected format, discarding the extra data
		# This is not part of mocking the data, and is used so that format-specific processing is done in the
		# "request_source_<x>" function while all the generic/standardized processing can stay in get_data
		for item in data:
			item['category'] = item['category']['slug']
		return response.status, {'products': data[start:]}


# Fetches data from https://dummyjson.com/products, formatted as 20 item pages.
# Parameters:
# - session: an open aiohttp.ClientSession().
# - page: the requested page number.
# Returns:
# - the status of the web request return
# - the response json.
async def request_source_d(session, page):
	async with session.get("https://dummyjson.com/products?skip={}&limit=20".format((page - 1) * 20)) as response:
		data = await response.json()
		return response.status, data


# Fetches and processes data. Also handles network retries.
# Parameters:
# - config: a dictionary with configuration variables, typically loaded from a json file
# - request func: function of form (aiohttp.ClientSession(), page_num) => (response_status, response_json)
#   - used for specifying the data source
# - source_string: string. The text name of the data source
# - source_prefix: string. The prefix used to create the unified_id field.
#   - must be unique to guarantee unified_id field is unique.
# Return: A list of processed objects (dictionaries), each corresponding to one product
async def get_data(config, request_func, source_string, source_prefix, pool):
	results = MyMultithreadingData()

	try:
		async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config["timeout_seconds"])) as session:
			is_more_data = True
			page = 1
			retry_count = 0
			while is_more_data:
				try:
					status, response_json = await request_func(session, page)
				except asyncio.TimeoutError:
					status = "timeout"

				# Retry on request failure
				if status != 200:
					results.add_failed_request()
					# End early if we fail too many times in a row
					if retry_count >= config["num_retries"]:
						timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
						results.add_error({"endpoint": source_string, "error": "timeout_after_retries", "timestamp": timestamp})
						break
					# Otherwise, retry with an exponential backoff
					else:
						delay = config["first_retry_delay_seconds"] \
								* pow(config["retry_backoff_multiplier"], retry_count)
						retry_count += 1
						await asyncio.sleep(delay)
						continue

				results.add_successful_request()
				retry_count = 1

				if len(response_json['products']) > 0:
					pool.apply(process_one_set, (response_json['products'], source_string, source_prefix, results))

					page += 1

					await asyncio.sleep(config["endpoint_delay_between_requests_seconds"])

				else:
					is_more_data = False

	# Note: generally, any possible errors should be handled before this hard catch statement,
	# but including it provides protection against any one pipeline taking down the whole script.
	# Disable this statement when trying to debug pipeline crashes.
	except:
		timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		results.add_error({"endpoint": source_string, "error": "pipeline_hard_crash", "timestamp": timestamp})

	return results


# Converts the json response into a list of objects
# Parameters:
# - data: a list of objects (dictionaries), each one corresponding to one item
# - source: string. The data source name
# - id_prefix: string. The prefix used to generate unified unique id values
# - results: MyMultithreadingData. Used to store/return the outputs in a threadsafe manner.
# Return: a list of objects (dictionaries), each one corresponding to one processed item
def process_one_set(data, source, id_prefix, results):
	new_objects = []
	for product in data:
		# skips products without an ID
		if not 'id' in product:
			continue

		product_obj = {
			'id': id_prefix + str(product['id']),
			'title': product['title'] if 'title' in product else "",
			'source': source,
			'price': product['price'] if 'price' in product else None,
			'category': product['category'] if 'category' in product else None,
			'processed_at': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		}
		new_objects.append(product_obj)
	results.add_products(new_objects)


# Creates the output file based on the processed items
# Parameters:
# - data: a list of objects (dictionaries), each one corresponding to one item
# - processing_time: float. The processing time in seconds
# - success_rate: float. The success rate of the network calls
# - sources: list of strings. A list of sources used in the output.
def write_output(data, processing_time, success_rate, sources, errors):
	output = {
		"summary": {
			"total_products": len(data),
			"processing_time_seconds": processing_time,
			"success_rate": success_rate,
			"sources": sources
		},
		"products": data,
		"errors": errors
	}

	with open("results.json", "w") as outfile:
		json.dump(output, outfile, indent=4)


# Run the script
if __name__ == '__main__':
	asyncio.run(main())
