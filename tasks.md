# Tasks

1. Study the code (30 minutes)
1. Study the companion documentation (60 minutes)
1. Add a new test case: `tests/unit/test_price_calculation.py:test_calculate_price_with_fees_zero_quantity` (10 minutes)
   - What should happen when quantity is 0?
   - Write the test first (TDD style)
   - If it fails, fix the business logic
1. Write a new unit test for `EventService.check_availability` method (30 minutes)
   - Mock the event repository
   - Test the case when event is not found
   - Test the case when sales are closed
   - Test the case when insufficient capacity
   - Write the tests in a new file: `tests/unit/test_event_service.py`
1. Write a new integration test in `tests/integration/test_user_repository.py` (30 minutes)
   - Test creating a user
   - Test retrieving a user by email
   - Test that duplicate emails are prevented
1. Rewrite the tests in `tests/unit/test_price_calculation.py` to use parametrized execution instead of multiple test functions (10 minutes)
   - Use the `@pytest.mark.parametrize` decorator
   - Merge multiple test functions into one