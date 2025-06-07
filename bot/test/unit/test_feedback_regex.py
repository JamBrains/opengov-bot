import unittest
import re


class TestFeedbackRegex(unittest.TestCase):
    """
    Test cases for the regex pattern used in the feedback command to match thread names
    with referendum numbers.
    """

    def test_thread_name_matching(self):
        """
        Test that the regex pattern correctly matches thread names with format 'Ref 1234:'
        and doesn't match other patterns.
        """
        # Define test cases with expected outcomes
        test_cases = [
            # (referendum_number, thread_name, should_match)
            (1234, "Ref 1234: Discussion", True),       # Should match - exact format
            (1234, "Ref 12345: Hi", False),             # Should not match - different number
            (1234, "Something Ref 1234: Hi", False),    # Should not match - text before Ref
            (1234, "Ref1234: Hi", False),               # Should not match - no space after Ref
            (1234, "Ref 1234 Hi", False),               # Should not match - missing colon
            (1234, "Ref 1234:", True),                  # Should match - just Ref, number and colon
            (123, "Ref 123: Test", True),               # Should match - shorter number
            (123, "Ref 12: Test", False),               # Should not match - different number
            (1, "Ref 1: Single digit", True),           # Should match - single digit
            (1234, "Ref 1234:Hi", True),                # Should match - no space after colon
        ]

        # Run tests for each case
        for referendum_number, thread_name, should_match in test_cases:
            pattern = rf'^Ref {re.escape(str(referendum_number))}:'
            result = bool(re.match(pattern, thread_name))

            # Check if the result matches the expected outcome
            self.assertEqual(
                result,
                should_match,
                f"Failed for referendum_number={referendum_number}, thread_name='{thread_name}'. "
                f"Expected match: {should_match}, got: {result}"
            )

    def test_extract_referendum_number(self):
        """
        Test that the regex pattern correctly extracts the referendum number from thread names.
        """
        # Test cases for extracting referendum numbers
        test_cases = [
            ("1234: Title", "1234"),           # Standard format
            ("123: Another title", "123"),     # Shorter number
            ("#1234: With hash", "1234"),      # With hash symbol
            ("No number here", None),          # No number
            ("1234 No colon", None),           # Missing colon
            ("12345: Too long", "12345"),      # Should match all digits before the colon
        ]

        for thread_name, expected_number in test_cases:
            # This is the regex used in the feedback command to extract referendum number from referendas threads
            match = re.search(r'^#?(\d+):', thread_name)
            extracted = match.group(1) if match else None

            self.assertEqual(
                extracted,
                expected_number,
                f"Failed to extract referendum number from '{thread_name}'. "
                f"Expected: {expected_number}, got: {extracted}"
            )


if __name__ == '__main__':
    unittest.main()
