import openai
import sys
import traceback

class ErrorSuggester:
    def __init__(self, api_key):
        openai.api_key = api_key

    def enable_auto_suggestions(self):
        # Override sys.excepthook to intercept exceptions
        def exception_handler(exc_type, exc_value, exc_traceback):
            # Format the error message for ChatGPT
            error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # Generate suggestions using ChatGPT
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=error_message,
                max_tokens=50,
                n=1,  # Number of suggestions to generate
                stop=None,
                temperature=0.5
            )

            # Extract the suggestions from the response
            suggestions = [choice['text'] for choice in response['choices']]

            print("Suggestions for resolving the error:")
            for suggestion in suggestions:
                print(suggestion)

        # Set sys.excepthook to the custom exception handler
        sys.excepthook = exception_handler

