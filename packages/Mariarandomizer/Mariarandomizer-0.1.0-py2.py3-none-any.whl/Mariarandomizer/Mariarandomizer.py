"""Main module."""
import requests

class Mariarandomizer:
    def jokes(self):
        # API URL for Jokes API
        url = "https://icanhazdadjoke.com/"

        # Set the headers to request JSON response from the API
        headers = {
            "Accept": "application/json"
        }

        # Make a GET request to the API and fetch the response
        response = requests.get(url, headers=headers)

        # Parse the response JSON to extract the joke
        joke = response.json()

        # Extract the joke from the response
        standalone_joke = joke['joke']

        # Return the standalone joke
        return standalone_joke
    
    def quotes(self):
        # API URL for Quotes API
        url = "https://api.quotable.io/random"

        # Make a GET request to the API and fetch the response
        response = requests.get(url)

        # Parse the response JSON to extract the quote
        quote = response.json()

        # Extract the quote content and author from the response
        quote_content = quote['content']
        quote_author = quote['author']

        # Create a formatted string with the quote and author
        formatted_quote = f"{quote_content} - {quote_author}"

        # Return the formatted quote
        return formatted_quote

obj =Mariarandomizer()
print(obj.quotes())

