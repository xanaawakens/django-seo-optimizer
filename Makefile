.PHONY: test coverage performance clean

test:
	pytest

coverage:
	pytest --cov=seo_optimizer --cov-report=html
	open htmlcov/index.html

performance:
	locust -f tests/performance/locustfile.py

clean:
	rm -rf .coverage htmlcov .pytest_cache __pycache__ .benchmarks
