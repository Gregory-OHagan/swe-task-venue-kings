# Take-Home Coding Challenge: Async Data Pipeline

## Overview
Build a concurrent data processing pipeline that fetches, processes, and stores data from multiple APIs. This task evaluates your skills in asynchronous programming, concurrency control, and error handling.
 
**Language:** Python

## The Challenge

Imagine you’re building a small data aggregation service that collects product information from multiple mock e-commerce APIs and processes them concurrently.

### Requirements

#### 1. Data Fetching (Async/Concurrent)
- Fetch product data from 3 different mock API endpoints (options provided below)
- Implement concurrent requests with proper rate limiting (max 5 requests/second per endpoint)
- Handle network timeouts and retries (max 3 retries with exponential backoff)
- Each endpoint returns 100+ products, paginated (20 items per page)

#### 2. Data Processing (Multithreading/Worker Pool)
- Process fetched data using a worker pool/thread pool
- Normalize product data from different APIs into a consistent format
- Calculate additional metrics (e.g., price trends, category distribution)
- Implement proper synchronization for shared data structures

#### 3. Error Handling & Resilience
- Gracefully handle API failures (some endpoints may be unreliable)
- Implement circuit breaker pattern for failing endpoints
- Log errors with appropriate detail levels
- Ensure partial failures don't crash the entire pipeline

#### 4. Performance & Monitoring
- Process all data within 60 seconds
- Implement basic monitoring (track success/failure rates, processing times)
- Memory-efficient processing (don't load all data into memory at once)

## Mock API Endpoints

**Important:** All endpoints should be treated as rate-limited (implement proper rate limiting in your solution).

You can choose from mock API providers like these options or create your own:

### Option 1: Free Testing APIs
```
https://jsonplaceholder.typicode.com/posts (treat as products)
https://reqres.in/api/users?page={page} (treat as product data - needs a free API key)
https://api.escuelajs.co/api/v1/products (actual product data)
https://dummyjson.com/products (actual product data)
```

### Option 2: Create Local Mock Servers
You can create simple Flask/FastAPI mock servers that:
- Return paginated JSON data
- Simulate different response times
- Occasionally return errors (for testing resilience)
- Implement actual rate limiting

Choose the approach that best demonstrates your skills. Document your choice and reasoning.

## Expected Deliverables

### 1. Core Implementation
- Main pipeline orchestrator
- Async fetching module with rate limiting
- Worker pool for data processing
- Error handling and retry logic

### 2. Documentation
- README with setup and run instructions
- Code comments explaining concurrency decisions
- Brief architecture overview (1-2 paragraphs)
- **AI_USAGE.md** documenting AI tool usage (required)

### 3. Testing
- Unit tests for key components
- Integration test for the full pipeline
- Error scenario tests (network failures, malformed data)

### 4. Bonus Points (Optional)
- Configuration file for tuning concurrency parameters
- Simple CLI interface with progress indicators
- Metrics collection and basic reporting
- Docker containerization

## Technical Constraints

**Must demonstrate understanding of:**
- `asyncio` for async operations and concurrency control
- HTTP client libraries (`aiohttp`, `httpx`, or `requests` with threading)
- Worker pools/thread pools (`concurrent.futures`, `threading`, or async alternatives)
- Error handling, retries, and circuit breaker patterns

**Allowed libraries** (choose what's appropriate for your solution):
- HTTP clients: `aiohttp`, `httpx`, `requests`
- Retry/resilience: `tenacity`, `backoff`, or custom implementation
- Testing: `pytest`, `asyncio.test`, `unittest`
- CLI/progress: `click`, `typer`, `tqdm`, `rich`
- Data processing: `pandas` (if needed for complex analysis)
- Configuration: `pydantic`, `dataclasses`, or simple config files

**What to avoid:**
- Heavy frameworks that abstract away async concepts (e.g., Celery, complex ETL frameworks)
- Libraries that would make the core challenge trivial

**Library choice evaluation:**
- Document why you chose specific libraries in your README
- Explain alternatives you considered
- Show understanding of what the libraries provide vs. what you implemented

## AI Tool Usage Policy

**You are encouraged to use AI tools** (ChatGPT, Claude, GitHub Copilot, etc.) during this challenge, but with important requirements:

### Documentation Required
1. **AI Usage Log**: Create a file `AI_USAGE.md` documenting:
   - Which AI tools you used and when
   - Your exact prompts/questions to the AI
   - What code/solutions the AI provided
   - How you modified or adapted the AI's suggestions

2. **Decision Explanations**: For any AI-generated code you use:
   - Explain why you chose this approach
   - Describe what the code does in your own words
   - Note any modifications you made and why
   - Identify potential issues or limitations

### What We're Looking For
- **Understanding over copying**: You should be able to explain every line of code
- **Critical thinking**: Show that you evaluated AI suggestions rather than blindly accepting them
- **Personal judgment**: Demonstrate your own decision-making in choosing between options
- **Problem-solving process**: Document your thought process, not just the final solution

### Example AI Usage Entry
```
Prompt: How to implement exponential backoff in Python asyncio?

AI Response: [paste the AI's code suggestion]

My Analysis: The AI suggested ... I modified it ... I chose this approach because...

Final Implementation: [your adapted code with explanations]
```

This policy allows you to leverage modern development practices while demonstrating your understanding and judgment.

## Evaluation Criteria
We don’t expect a production-ready implementation. Focus on demonstrating your understanding of concurrency, async programming, and error handling. Partial but well-explained solutions are perfectly fine.

### Primary (70%)
1. **Correctness:** Does the solution work as specified?
2. **Concurrency:** Proper use of async/threading patterns
3. **Error Handling:** Robust handling of failures and edge cases
4. **Code Quality:** Clean, readable, well-structured code

### Secondary (30%)
1. **Performance:** Efficient resource usage and timing
2. **Testing:** Good test coverage and quality
3. **Documentation:** Clear explanations and setup instructions
4. **Best Practices:** Following language-specific conventions

## Sample Data Structure

Expected output format:
```json
{
  "summary": {
    "total_products": 300,
    "processing_time_seconds": 45.2,
    "success_rate": 0.97,
    "sources": ["endpoint_a", "endpoint_b", "endpoint_c"]
  },
  "products": [
    {
      "id": "unified_id_1",
      "title": "Product Name",
      "source": "endpoint_a",
      "price": 29.99,
      "category": "electronics",
      "processed_at": "2025-07-18T10:30:00Z"
    }
  ],
  "errors": [
    {
      "endpoint": "endpoint_c",
      "error": "timeout_after_retries",
      "timestamp": "2025-07-18T10:25:30Z"
    }
  ]
}
```

## Getting Started

1. Implement a basic version that fetches from one endpoint
2. Add concurrency and error handling
3. Extend to multiple endpoints with rate limiting
4. Add processing pipeline and worker pools
5. Implement testing and documentation

## Submission Guidelines

- Create a Git repository with clear commit history
- Include all source code, tests, and documentation
- Provide a brief summary of your approach and any tradeoffs made
- Mention any assumptions or simplifications
- AI usage log
- Submit as a GitHub repository link

## Questions?

If you have any clarifying questions about the requirements, please reach out. We're looking for practical solutions that demonstrate real-world async programming skills.

Good luck!