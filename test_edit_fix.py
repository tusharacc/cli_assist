def test_function():
    try:
        result = "hello"
        return result
    except Exception as e:
        log.error(f"An error occurred: {e}")
        return None