from threading_helpers import *
from main import *


# MyMultithreadingData: simple code coverage test of all fields and functions.
def test_data_obj_simple():
	data = MyMultithreadingData()

	data.add_successful_request()
	data.add_successful_request(3)

	data.add_failed_request(2)

	data.add_products(['a', 'b'])
	data.add_products(('c',))

	data.add_error({'e': 1})

	assert data.successful_requests == 4
	assert data.failed_requests == 2

	assert len(data.products) == 3
	assert 'a' in data.products and 'b' in data.products and 'c' in data.products
	assert data.errors == [{'e': 1}]


# MyMultithreadingData: multithreading safety
def test_data_obj_multithreading():
	data = MyMultithreadingData()

	def func():
		data.add_successful_request()
		time.sleep(0.1)
		data.add_successful_request()

	for i in range(3):
		thread = threading.Thread(target=func)
		thread.start()

	time.sleep(0.2)

	assert data.successful_requests == 6


# MyThreadingPool: uses the amount of time taken to ensure thread cap is respected.
def test_max_threads_and_parallelism():
	pool = MyThreadingPool(6)

	def func():
		time.sleep(.1)

	# Test with 12 threads (6 at once)
	start = time.time()
	for i in range(12):
		pool.apply(func, ())

	pool.join_all()

	duration = time.time() - start
	# a slight range is acceptable due to potential rounding
	assert .19 < duration < .21

	# Test with 13 threads (6 at once)
	start = time.time()
	for i in range(13):
		pool.apply(func, ())

	pool.join_all()

	duration = time.time() - start
	assert .29 < duration < .31


# MyThreadingPool: makes sure every thread in the queue is executed
def test_are_all_threads_executed():
	pool = MyThreadingPool(8)
	data = MyMultithreadingData()

	def func(val):
		time.sleep(val)
		data.add_successful_request()

	for i in range(20):
		pool.apply(func, (i / 100,))

	pool.join_all()

	assert data.successful_requests == 20
