import asyncio
import aiohttp

import datetime
import json


async def main():
    dt_start = datetime.datetime.now()

    # Load configuration file
    with open('config.json') as infile:
        config = json.load(infile)
    # TODO: consider adding defaults to loaded config in case of a malformed config file

    # Process each endpoint
    # TODO: implement at least 2 additional endpoints
    (data_d, successful_calls, failed_calls, is_failure), = await asyncio.gather(get_data_source_d(config))

    # Calculate the processing time
    dt_end = datetime.datetime.now()
    duration = (dt_end - dt_start).total_seconds()

    success_rate = successful_calls / (successful_calls + failed_calls)

    # Write the results to an output file
    write_output(data_d, duration, success_rate, ["endpoint_d"])


# Get data from the fourth provided sample source (https://dummyjson.com/products)
# Parameters:
# - config: a dictionary with configuration variables, typically loaded from a json file
# Return: A list of processed objects (dictionaries), each corresponding to one product
async def get_data_source_d(config):
    data = []
    success_count = 0
    fail_count = 0
    is_failure = False

    async with aiohttp.ClientSession() as session:
        is_more_data = True
        skip = 0
        retry_count = 0
        while is_more_data:
            async with session.get("https://dummyjson.com/products?skip={}&limit=20".format(skip)) as response:
                # Retry on request failure
                if response.status != 200:
                    fail_count += 1
                    # End early if we fail too many times in a row
                    if retry_count >= config["num_retries"]:
                        failure = True
                        break
                    # Otherwise, retry with an exponential backoff
                    else:
                        delay = config["first_retry_delay_seconds"] \
                                * pow(config["retry_backoff_multiplier"], retry_count)
                        retry_count += 1
                        await asyncio.sleep(delay)
                        continue

                success_count += 1
                retry_count = 1

                response_json = await response.json()
                if len(response_json['products']) > 0:
                    res = process_one_set(response_json['products'], "jsonplaceholder.typicode.com", "d.")
                    data.extend(res)

                    skip += 20

                    await asyncio.sleep(config['endpoint_delay_between_requests_seconds'])

                else:
                    is_more_data = False

    return data, success_count, fail_count, is_failure


# Converts the json response into a list of objects
# Parameters:
# - data: a list of objects (dictionaries), each one corresponding to one item
# - source: string, specifying the data source
# Return: a list of objects (dictionaries), each one corresponding to one processed item
def process_one_set(data, source, id_prefix):
    result = []
    for product in data:
        product_obj = {
            'id': id_prefix + str(product['id']),
            'title': product['title'],
            'source': source,
            'price': product['price'],
            'category': product['category'],
            'processed_at': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        result.append(product_obj)
    return result


# Creates the output file based on the processed items
# Parameters:
# - data: a list of objects (dictionaries), each one corresponding to one item
# - processing_time: float. The processing time in seconds
# - success_rate: float. The success rate of the network calls
# - sources: list of strings. A list of sources used in the output.
def write_output(data, processing_time, success_rate, sources):
    output = {
        "summary": {
            "total_products": len(data),
            "processing_time_seconds": processing_time,
            "success_rate": success_rate,
            "sources": sources
        },
        "products": data
    }

    with open("results.json", "w") as outfile:
        json.dump(output, outfile)


# Run the script
if __name__ == '__main__':
    asyncio.run(main())
