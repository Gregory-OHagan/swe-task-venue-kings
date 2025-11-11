from main import *


# Returns a valid response with no data
# Separating the sources from the processing code earlier makes it easy to mock data sources.
async def mock_get_data_empty(session, page):
	return 200, {"products": []}


# Returns an error response
async def mock_get_data_error(session, page):
	return 404, None


# returns valid data
async def mock_get_data(session, page):
	if page == 1:
		return 200, {"products": [
			{"id": 1, "title": "brown shirt", "category": "clothes"},
			{"id": 2, "title": "grey pants", "category": "clothes", "price": 25},
			{"id": 3, "title": "blue hoodie", "category": "clothes", "price": 30},
			{"id": 4, "title": "calculator", "category": "electronics", "price": 60}
		]}
	return 200, {"products": []}


# returns multiple pages of valid data
async def mock_get_data_2(session, page):
	if page == 1:
		return 200, {"products": [
			{"id": 1, "title": "brown dinosaur", "category": "toy", "price": 15},
			{"id": 2, "title": "grey rocket", "category": "toy", "price": 23}
		]}
	if page == 2:
		return 200, {"products": [
			{"id": 3, "title": "blue hoodie", "category": "toy", "price": 30},
			{"id": 4, "title": "tablet", "category": "electronics", "price": 110}
		]}
	if page == 3:
		return 200, {"products": [
			{"id": 5, "title": "red car", "category": "toy", "price": 17}
		]}
	return 200, {"products": []}


test_config = {
	"first_retry_delay_seconds": 0.2,
	"retry_backoff_multiplier": 2,
	"num_retries": 3,
	"endpoint_delay_between_requests_seconds": 0.2,
	"worker_thread_count": 4,
	"timeout_seconds": 2
}


def test_get_data():
	asyncio.run(_test_get_data())


# Tests that a simple data stream is fetched and processed properly
async def _test_get_data():
	pool = MyThreadingPool(4)
	(res,) = await asyncio.gather(get_data(test_config, mock_get_data, "source", "a.", pool))
	pool.join_all()

	assert len(res.products) == 4
	assert res.products[0]["id"] == "a.1"
	assert res.products[0]["category"] == 'clothes'
	assert res.products[0]["title"] == "brown shirt"
	assert res.products[0]["source"] == "source"


# Tests that the number and delay on retrying after failed requests is correct
def test_retry_backoff():
	asyncio.run(_test_retry_backoff())


async def _test_retry_backoff():
	pool = MyThreadingPool(4)

	start = time.time()
	(res,) = await asyncio.gather(get_data(test_config, mock_get_data_error, "source", "a.", pool))

	pool.join_all()
	assert res.failed_requests == 4
	assert 1.3 < time.time() - start < 1.5		# actual expected value: 1.4
	assert res.errors[0]['error'] == "timeout_after_retries"


# Integration test that expected behaviour holds when running multiple sources in parallel
def test_get_data_complex():
	asyncio.run(_test_get_data_complex())


async def _test_get_data_complex():
	pool = MyThreadingPool(4)

	start = time.time()
	(res1, res2, res3, res4) = await asyncio.gather(get_data(test_config, mock_get_data_empty, "A", "a.", pool),
													get_data(test_config, mock_get_data_error, "B", "b.", pool),
													get_data(test_config, mock_get_data, "C", "c.", pool),
													get_data(test_config, mock_get_data_2, "D", "d.", pool))

	pool.join_all()

	assert res1.failed_requests == 0
	assert res1.successful_requests == 1
	assert len(res1.products) == 0

	assert res2.failed_requests == 4
	assert res2.successful_requests == 0
	assert len(res2.products) == 0

	assert res3.successful_requests == 2
	assert len(res3.products) == 4

	assert res4.successful_requests == 4
	assert len(res4.products) == 5
