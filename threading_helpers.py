import threading


# A simple, threadsafe object for storing data
# Always use the provided methods when possible for adding/changing data in this object. They are threadsafe.
# If a pre-built method is not available, use the lock object.
class MyMultithreadingData:
	def __init__(self):
		self.products = []
		self.errors = []

		self.successful_requests = 0
		self.failed_requests = 0

		self.lock = threading.Lock()

	def add_products(self, products):
		with self.lock:
			self.products.extend(products)

	def add_error(self, error):
		with self.lock:
			self.errors.append(error)

	def add_successful_request(self, num=1):
		with self.lock:
			self.successful_requests += num

	def add_failed_request(self, num=1):
		with self.lock:
			self.failed_requests += num


# A custom object for handling an arbitrary amount of work across a specific maximum number of worker threads.
# There are likely built-in or library classes that would be better than a custom implementation such as this, but
# this is done to demonstrate knowledge of threading concepts.
# Warning: worker thread exceptions are ignored and skipped without notification. It is up to the user of this class
# to log and properly handle exceptions that arise during the executing of a worker thread.
class MyThreadingPool:
	def __init__(self, max_worker_thread_count=4):
		self.max_worker_count = max_worker_thread_count
		self.current_worker_count = 0

		self.queued_tasks = []
		self.thread_handles = []

		self._lock = threading.Lock()

	# Calls the function with the specified parameters using the next available thread
	# Inputs:
	# - func: function. The function to be called
	# - params: any iterable. Parameters to give to the function when calling it.
	def apply(self, func, params):
		with self._lock:
			self.queued_tasks.append((func, params))
		self._start_workers()

	# Blocks the calling thread until _all_ worker threads are complete
	# Note: do not add more tasks using apply while a thread is waiting on this function
	def join_all(self):
		for thread in self.thread_handles:
			thread.join()

	# Internal method. Checks the queue and starts as many workers as are available (up to the set maximum)
	def _start_workers(self):
		with self._lock:
			for i in range(self.current_worker_count, self.max_worker_count):
				if len(self.queued_tasks) == 0:
					break
				thread = threading.Thread(target=self._worker_thread)
				thread.start()
				self.thread_handles.append(thread)


	# Internal method. One worker thread, started using _start_workers
	def _worker_thread(self):
		with self._lock:
			# Don't start up more worker threads than the maximum.
			# This extra check is here in case race conditions try to start multiple at once.
			if self.current_worker_count >= self.max_worker_count or len(self.queued_tasks) == 0:
				return
			func, params = self.queued_tasks.pop(0)
			self.current_worker_count += 1

		try:
			func(*params)
		# We need to make absolute sure that this object doesn't gum itself up with exception handling in some way
		except:
			pass

		with self._lock:
			self.current_worker_count -= 1

		# Start the next waiting worker after this one finishes (if there is one)
		self._start_workers()

