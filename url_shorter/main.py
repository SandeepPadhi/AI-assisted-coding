"""
URL Shortener

Goal:
- Create a URL Shortener


Functional Requirements:
- User can create a short URL for a long URL
- User can redirect to the long URL from the short URL
- User can see the number of clicks on a short URL
- User can see the top 100 most clicked short URLs

Non-Functional Requirements:
- The system should be able to handle 1000 requests per second
- The system should be able to scale to 1000000 requests per second


Coding guidelines:
Design guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Implement the repository in-memory, but design it so it can be extended to other storage systems
- do not sure any external libraries.
- Write the code in a way that it is easy to understand and easy to maintain.
- Keep the code modular and short which satisfies the requirements. and single responsibility principle.
- Respository function names should be self-explanatory.
- YOu can use repository class to store different entities and then extend it to in-memory or other storage systems.
- Do not use generics for now but create different abstractions for different entities.
- Each entity should be able to handle its invariants and validations and business logic.
- Use type hints for all functions and variables.

"""


import sys
from abc import ABC, abstractmethod
from typing import List  # For type hints

class URL:
    def __init__(self, long_url: str, short_url: str) -> None:
        self.validate_long_url(long_url)  # Validate long URL
        self.validate_short_url(short_url)  # Validate short URL
        self.long_url: str = long_url
        self.short_url: str = short_url
        self.click_count: int = 0  # Initialized to zero
    
    def validate_long_url(self, long_url: str) -> None:
        if not isinstance(long_url, str) or not (long_url.startswith('http://') or long_url.startswith('https://')):
            raise ValueError("Invalid long URL: must be a string starting with http:// or https://")
    
    def validate_short_url(self, short_url: str) -> None:
        if not isinstance(short_url, str) or len(short_url) == 0:
            raise ValueError("Invalid short URL: must be a non-empty string")
    
    def increment_clicks(self) -> None:
        if self.click_count < 0:
            raise ValueError("Click count cannot be negative")
        self.click_count += 1
    
    def get_click_count(self) -> int:
        return self.click_count

class URLRepository(ABC):
    @abstractmethod
    def add_url_entity(self, url_entity: URL) -> None:
        pass
    
    @abstractmethod
    def get_url_entity_by_short_url(self, short_url: str) -> URL:
        pass
    
    @abstractmethod
    def increment_click_count_for_short_url(self, short_url: str) -> None:
        pass
    
    @abstractmethod
    def get_top_100_urls_by_click_count(self) -> List[URL]:
        pass

class InMemoryURLRepository(URLRepository):
    def __init__(self) -> None:
        self.urls: dict[str, URL] = {}  # Dictionary to store URLs, keyed by short URL
    
    def add_url_entity(self, url_entity: URL) -> None:
        if url_entity.short_url in self.urls:
            raise ValueError("Short URL already exists")
        self.urls[url_entity.short_url] = url_entity
    
    def get_url_entity_by_short_url(self, short_url: str) -> URL:
        return self.urls.get(short_url)
    
    def increment_click_count_for_short_url(self, short_url: str) -> None:
        url: URL = self.get_url_entity_by_short_url(short_url)
        if url:
            url.increment_clicks()
    
    def get_top_100_urls_by_click_count(self) -> List[URL]:
        sorted_urls = sorted(self.urls.values(), key=lambda x: x.click_count, reverse=True)
        return sorted_urls[:100]

class URLShortenerService:
    def __init__(self, repository: URLRepository) -> None:
        self.repository: URLRepository = repository
    
    def create_short_url(self, long_url: str, short_url: str) -> str:
        url_entity: URL = URL(long_url, short_url)
        self.repository.add_url_entity(url_entity)
        return short_url
    
    def redirect_to_long_url(self, short_url: str) -> str:
        url_entity: URL = self.repository.get_url_entity_by_short_url(short_url)
        if url_entity:
            self.repository.increment_click_count_for_short_url(short_url)
            return url_entity.long_url
        raise ValueError("Short URL not found")
    
    def get_click_count(self, short_url: str) -> int:
        url_entity: URL = self.repository.get_url_entity_by_short_url(short_url)
        if url_entity:
            return url_entity.get_click_count()
        raise ValueError("Short URL not found")
    
    def get_top_100(self) -> List[URL]:
        return self.repository.get_top_100_urls_by_click_count()

# Simple orchestrator example to tie everything together
def main():
    repository = InMemoryURLRepository()  # Create repository instance
    service = URLShortenerService(repository)  # Create service instance with repository injected
    
    while True:
        print("\nURL Shortener Interactive Mode:")
        print("1. Create short URL")
        print("2. Redirect to long URL")
        print("3. Get click count")
        print("4. Get top 100 URLs")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        
        try:
            if choice == '1':
                long_url = input("Enter long URL: ")
                short_url = input("Enter short URL: ")
                result = service.create_short_url(long_url, short_url)
                print(f"Created short URL: {result}")
            elif choice == '2':
                short_url = input("Enter short URL: ")
                redirect_url = service.redirect_to_long_url(short_url)
                print(f"Redirecting to: {redirect_url}")
            elif choice == '3':
                short_url = input("Enter short URL: ")
                click_count = service.get_click_count(short_url)
                print(f"Click count: {click_count}")
            elif choice == '4':
                top_urls = service.get_top_100()
                print("Top 100 URLs:", [url.short_url for url in top_urls])
            elif choice == '5':
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()  # Run the orchestrator