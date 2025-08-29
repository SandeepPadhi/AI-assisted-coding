import uuid
from typing import List, Optional
from repositories import AbstractUserRepository, AbstractSearchQueryRepository, AbstractSearchResultRepository
from entities import User, SearchQuery, SearchResult


class UserManager:
    """Manager class for handling user-related business operations."""

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        """Initialize the UserManager with a user repository.

        Args:
            user_repository: Repository implementation for user data storage
        """
        self.user_repository = user_repository

    def create_user(self, username: str, email: str) -> User:
        """Create a new user.

        Args:
            username: Username for the new user
            email: Email address for the new user

        Returns:
            Newly created User entity

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        if self.user_repository.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        # Check if email already exists
        if self.user_repository.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        # Generate unique user ID
        user_id = str(uuid.uuid4())

        # Create and save user
        user = User(user_id, username, email)
        self.user_repository.save_user(user)

        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: Unique identifier of the user

        Returns:
            User entity if found, None otherwise
        """
        return self.user_repository.get_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username.

        Args:
            username: Username of the user

        Returns:
            User entity if found, None otherwise
        """
        return self.user_repository.get_user_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email.

        Args:
            email: Email address of the user

        Returns:
            User entity if found, None otherwise
        """
        return self.user_repository.get_user_by_email(email)

    def get_all_users(self) -> List[User]:
        """Retrieve all users.

        Returns:
            List of all User entities
        """
        return self.user_repository.get_all_users()

    def update_user_profile(self, user_id: str, new_username: Optional[str] = None, new_email: Optional[str] = None) -> bool:
        """Update a user's profile information.

        Args:
            user_id: Unique identifier of the user to update
            new_username: New username (optional)
            new_email: New email address (optional)

        Returns:
            True if user was updated successfully, False otherwise

        Raises:
            ValueError: If new username or email already exists
        """
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return False

        # Check for username conflicts if updating username
        if new_username and new_username != user.username:
            if self.user_repository.get_user_by_username(new_username):
                raise ValueError(f"Username '{new_username}' already exists")
            user.update_username(new_username)

        # Check for email conflicts if updating email
        if new_email and new_email != user.email:
            if self.user_repository.get_user_by_email(new_email):
                raise ValueError(f"Email '{new_email}' already exists")
            user.update_email(new_email)

        self.user_repository.update_user(user)
        return True

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account.

        Args:
            user_id: Unique identifier of the user to deactivate

        Returns:
            True if user was deactivated successfully, False otherwise
        """
        user = self.user_repository.get_user_by_id(user_id)
        if user:
            user.deactivate()
            self.user_repository.update_user(user)
            return True
        return False

    def activate_user(self, user_id: str) -> bool:
        """Activate a user account.

        Args:
            user_id: Unique identifier of the user to activate

        Returns:
            True if user was activated successfully, False otherwise
        """
        user = self.user_repository.get_user_by_id(user_id)
        if user:
            user.activate()
            self.user_repository.update_user(user)
            return True
        return False

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the system.

        Args:
            user_id: Unique identifier of the user to delete

        Returns:
            True if user was deleted successfully, False otherwise
        """
        return self.user_repository.delete_user(user_id)

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists.

        Args:
            user_id: Unique identifier of the user

        Returns:
            True if user exists, False otherwise
        """
        return self.user_repository.user_exists(user_id)


class SearchQueryManager:
    """Manager class for handling search query-related business operations."""

    def __init__(self, search_query_repository: AbstractSearchQueryRepository) -> None:
        """Initialize the SearchQueryManager with a search query repository.

        Args:
            search_query_repository: Repository implementation for search query data storage
        """
        self.search_query_repository = search_query_repository

    def create_search_query(self, user_id: str, query_text: str) -> SearchQuery:
        """Create a new search query.

        Args:
            user_id: ID of the user making the query
            query_text: The search query text

        Returns:
            Newly created SearchQuery entity

        Raises:
            ValueError: If query text is empty or user doesn't exist
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        # Check if this exact query already exists for the user
        existing_queries = self.search_query_repository.get_search_queries_by_user_id(user_id)
        for existing_query in existing_queries:
            if existing_query.query_text.lower() == query_text.lower():
                # Increment frequency instead of creating duplicate
                existing_query.increment_frequency()
                self.search_query_repository.update_search_query(existing_query)
                return existing_query

        # Generate unique query ID and create new query
        query_id = str(uuid.uuid4())
        search_query = SearchQuery(query_id, user_id, query_text)
        self.search_query_repository.save_search_query(search_query)

        return search_query

    def get_search_query_by_id(self, query_id: str) -> Optional[SearchQuery]:
        """Retrieve a search query by its ID.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            SearchQuery entity if found, None otherwise
        """
        return self.search_query_repository.get_search_query_by_id(query_id)

    def get_user_search_queries(self, user_id: str) -> List[SearchQuery]:
        """Retrieve all search queries for a specific user.

        Args:
            user_id: Unique identifier of the user

        Returns:
            List of SearchQuery entities for the user
        """
        return self.search_query_repository.get_search_queries_by_user_id(user_id)

    def get_search_queries_by_text_prefix(self, text_prefix: str) -> List[SearchQuery]:
        """Retrieve search queries that start with the given text prefix.

        Args:
            text_prefix: Text prefix to search for

        Returns:
            List of SearchQuery entities matching the prefix
        """
        return self.search_query_repository.get_search_queries_by_text_prefix(text_prefix)

    def get_all_search_queries(self) -> List[SearchQuery]:
        """Retrieve all search queries from the repository.

        Returns:
            List of all SearchQuery entities
        """
        return self.search_query_repository.get_all_search_queries()

    def get_popular_search_queries(self, limit: int = 10) -> List[SearchQuery]:
        """Retrieve the most popular search queries based on frequency.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of most popular SearchQuery entities ordered by frequency
        """
        all_queries = self.search_query_repository.get_all_search_queries()
        all_queries.sort(key=lambda q: q.frequency_count, reverse=True)
        return all_queries[:limit]

    def increment_query_frequency(self, query_id: str) -> bool:
        """Increment the frequency count of a search query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if frequency was incremented, False if query not found
        """
        return self.search_query_repository.increment_query_frequency(query_id)

    def delete_search_query(self, query_id: str) -> bool:
        """Delete a search query.

        Args:
            query_id: Unique identifier of the search query to delete

        Returns:
            True if query was deleted successfully, False otherwise
        """
        return self.search_query_repository.delete_search_query(query_id)

    def search_query_exists(self, query_id: str) -> bool:
        """Check if a search query exists.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if query exists, False otherwise
        """
        return self.search_query_repository.search_query_exists(query_id)


class SearchResultManager:
    """Manager class for handling search result-related business operations."""

    def __init__(self, search_result_repository: AbstractSearchResultRepository) -> None:
        """Initialize the SearchResultManager with a search result repository.

        Args:
            search_result_repository: Repository implementation for search result data storage
        """
        self.search_result_repository = search_result_repository

    def create_search_result(self, query_id: str, suggested_word: str, relevance_score: float) -> SearchResult:
        """Create a new search result.

        Args:
            query_id: ID of the query this result belongs to
            suggested_word: The suggested word/phrase
            relevance_score: Score indicating how relevant this result is (0.0 to 1.0)

        Returns:
            Newly created SearchResult entity
        """
        result_id = str(uuid.uuid4())
        search_result = SearchResult(result_id, query_id, suggested_word, relevance_score)
        self.search_result_repository.save_search_result(search_result)

        return search_result

    def get_search_result_by_id(self, result_id: str) -> Optional[SearchResult]:
        """Retrieve a search result by its ID.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            SearchResult entity if found, None otherwise
        """
        return self.search_result_repository.get_search_result_by_id(result_id)

    def get_search_results_for_query(self, query_id: str) -> List[SearchResult]:
        """Retrieve all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            List of SearchResult entities for the query
        """
        return self.search_result_repository.get_search_results_by_query_id(query_id)

    def get_top_search_results_for_query(self, query_id: str, limit: int = 5) -> List[SearchResult]:
        """Retrieve top search results for a query ordered by relevance score.

        Args:
            query_id: Unique identifier of the search query
            limit: Maximum number of results to return

        Returns:
            List of top SearchResult entities ordered by relevance score descending
        """
        return self.search_result_repository.get_top_search_results_by_query_id(query_id, limit)

    def get_search_results_by_score_range(self, min_score: float, max_score: float) -> List[SearchResult]:
        """Retrieve search results within a relevance score range.

        Args:
            min_score: Minimum relevance score (inclusive)
            max_score: Maximum relevance score (inclusive)

        Returns:
            List of SearchResult entities within the score range
        """
        return self.search_result_repository.get_search_results_by_relevance_score_range(min_score, max_score)

    def update_search_result_score(self, result_id: str, new_score: float) -> bool:
        """Update the relevance score of a search result.

        Args:
            result_id: Unique identifier of the search result
            new_score: New relevance score (0.0 to 1.0)

        Returns:
            True if score was updated successfully, False otherwise

        Raises:
            ValueError: If score is invalid
        """
        search_result = self.search_result_repository.get_search_result_by_id(result_id)
        if search_result:
            search_result.update_relevance_score(new_score)
            self.search_result_repository.update_search_result(search_result)
            return True
        return False

    def delete_search_result(self, result_id: str) -> bool:
        """Delete a search result.

        Args:
            result_id: Unique identifier of the search result to delete

        Returns:
            True if result was deleted successfully, False otherwise
        """
        return self.search_result_repository.delete_search_result(result_id)

    def delete_all_results_for_query(self, query_id: str) -> int:
        """Delete all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            Number of search results deleted
        """
        return self.search_result_repository.delete_search_results_by_query_id(query_id)

    def search_result_exists(self, result_id: str) -> bool:
        """Check if a search result exists.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            True if result exists, False otherwise
        """
        return self.search_result_repository.search_result_exists(result_id)
