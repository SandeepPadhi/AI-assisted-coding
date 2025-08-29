from abc import ABC, abstractmethod
from typing import List, Optional
from entities import User, SearchQuery, SearchResult


class AbstractUserRepository(ABC):
    """Abstract base class for user data storage operations."""

    @abstractmethod
    def save_user(self, user: User) -> None:
        """Save a user to the repository.

        Args:
            user: User entity to save
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: Unique identifier of the user

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username.

        Args:
            username: Username of the user

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email.

        Args:
            email: Email address of the user

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Retrieve all users from the repository.

        Returns:
            List of all User entities
        """
        pass

    @abstractmethod
    def update_user(self, user: User) -> None:
        """Update an existing user in the repository.

        Args:
            user: User entity with updated information
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the repository.

        Args:
            user_id: Unique identifier of the user to delete

        Returns:
            True if user was deleted, False if not found
        """
        pass

    @abstractmethod
    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the repository.

        Args:
            user_id: Unique identifier of the user

        Returns:
            True if user exists, False otherwise
        """
        pass


class AbstractSearchQueryRepository(ABC):
    """Abstract base class for search query data storage operations."""

    @abstractmethod
    def save_search_query(self, search_query: SearchQuery) -> None:
        """Save a search query to the repository.

        Args:
            search_query: SearchQuery entity to save
        """
        pass

    @abstractmethod
    def get_search_query_by_id(self, query_id: str) -> Optional[SearchQuery]:
        """Retrieve a search query by its ID.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            SearchQuery entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_search_queries_by_user_id(self, user_id: str) -> List[SearchQuery]:
        """Retrieve all search queries for a specific user.

        Args:
            user_id: Unique identifier of the user

        Returns:
            List of SearchQuery entities for the user
        """
        pass

    @abstractmethod
    def get_all_search_queries(self) -> List[SearchQuery]:
        """Retrieve all search queries from the repository.

        Returns:
            List of all SearchQuery entities
        """
        pass

    @abstractmethod
    def get_search_queries_by_text_prefix(self, text_prefix: str) -> List[SearchQuery]:
        """Retrieve search queries that start with the given text prefix.

        Args:
            text_prefix: Text prefix to search for

        Returns:
            List of SearchQuery entities matching the prefix
        """
        pass

    @abstractmethod
    def update_search_query(self, search_query: SearchQuery) -> None:
        """Update an existing search query in the repository.

        Args:
            search_query: SearchQuery entity with updated information
        """
        pass

    @abstractmethod
    def increment_query_frequency(self, query_id: str) -> bool:
        """Increment the frequency count of a search query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if frequency was incremented, False if query not found
        """
        pass

    @abstractmethod
    def delete_search_query(self, query_id: str) -> bool:
        """Delete a search query from the repository.

        Args:
            query_id: Unique identifier of the search query to delete

        Returns:
            True if query was deleted, False if not found
        """
        pass

    @abstractmethod
    def search_query_exists(self, query_id: str) -> bool:
        """Check if a search query exists in the repository.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if query exists, False otherwise
        """
        pass


class AbstractSearchResultRepository(ABC):
    """Abstract base class for search result data storage operations."""

    @abstractmethod
    def save_search_result(self, search_result: SearchResult) -> None:
        """Save a search result to the repository.

        Args:
            search_result: SearchResult entity to save
        """
        pass

    @abstractmethod
    def get_search_result_by_id(self, result_id: str) -> Optional[SearchResult]:
        """Retrieve a search result by its ID.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            SearchResult entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_search_results_by_query_id(self, query_id: str) -> List[SearchResult]:
        """Retrieve all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            List of SearchResult entities for the query
        """
        pass

    @abstractmethod
    def get_search_results_by_relevance_score_range(self, min_score: float, max_score: float) -> List[SearchResult]:
        """Retrieve search results within a relevance score range.

        Args:
            min_score: Minimum relevance score (inclusive)
            max_score: Maximum relevance score (inclusive)

        Returns:
            List of SearchResult entities within the score range
        """
        pass

    @abstractmethod
    def get_top_search_results_by_query_id(self, query_id: str, limit: int) -> List[SearchResult]:
        """Retrieve top search results for a query ordered by relevance score.

        Args:
            query_id: Unique identifier of the search query
            limit: Maximum number of results to return

        Returns:
            List of top SearchResult entities ordered by relevance score descending
        """
        pass

    @abstractmethod
    def get_all_search_results(self) -> List[SearchResult]:
        """Retrieve all search results from the repository.

        Returns:
            List of all SearchResult entities
        """
        pass

    @abstractmethod
    def update_search_result(self, search_result: SearchResult) -> None:
        """Update an existing search result in the repository.

        Args:
            search_result: SearchResult entity with updated information
        """
        pass

    @abstractmethod
    def delete_search_result(self, result_id: str) -> bool:
        """Delete a search result from the repository.

        Args:
            result_id: Unique identifier of the search result to delete

        Returns:
            True if result was deleted, False if not found
        """
        pass

    @abstractmethod
    def delete_search_results_by_query_id(self, query_id: str) -> int:
        """Delete all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            Number of search results deleted
        """
        pass

    @abstractmethod
    def search_result_exists(self, result_id: str) -> bool:
        """Check if a search result exists in the repository.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            True if result exists, False otherwise
        """
        pass
