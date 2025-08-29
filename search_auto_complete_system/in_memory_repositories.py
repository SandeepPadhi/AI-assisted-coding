from typing import List, Optional, Dict
from repositories import AbstractUserRepository, AbstractSearchQueryRepository, AbstractSearchResultRepository
from entities import User, SearchQuery, SearchResult


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory implementation of the User repository."""

    def __init__(self) -> None:
        """Initialize the in-memory user repository."""
        self._users: Dict[str, User] = {}
        self._username_index: Dict[str, str] = {}  # username -> user_id
        self._email_index: Dict[str, str] = {}  # email -> user_id

    def save_user(self, user: User) -> None:
        """Save a user to the in-memory repository.

        Args:
            user: User entity to save
        """
        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id
        self._email_index[user.email] = user.user_id

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: Unique identifier of the user

        Returns:
            User entity if found, None otherwise
        """
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username.

        Args:
            username: Username of the user

        Returns:
            User entity if found, None otherwise
        """
        user_id = self._username_index.get(username)
        if user_id:
            return self._users.get(user_id)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email.

        Args:
            email: Email address of the user

        Returns:
            User entity if found, None otherwise
        """
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None

    def get_all_users(self) -> List[User]:
        """Retrieve all users from the repository.

        Returns:
            List of all User entities
        """
        return list(self._users.values())

    def update_user(self, user: User) -> None:
        """Update an existing user in the repository.

        Args:
            user: User entity with updated information
        """
        if user.user_id in self._users:
            # Remove old indices
            old_user = self._users[user.user_id]
            if old_user.username in self._username_index:
                del self._username_index[old_user.username]
            if old_user.email in self._email_index:
                del self._email_index[old_user.email]

            # Update user and indices
            self._users[user.user_id] = user
            self._username_index[user.username] = user.user_id
            self._email_index[user.email] = user.user_id

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the repository.

        Args:
            user_id: Unique identifier of the user to delete

        Returns:
            True if user was deleted, False if not found
        """
        if user_id in self._users:
            user = self._users[user_id]
            # Remove from indices
            if user.username in self._username_index:
                del self._username_index[user.username]
            if user.email in self._email_index:
                del self._email_index[user.email]

            # Remove from main storage
            del self._users[user_id]
            return True
        return False

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the repository.

        Args:
            user_id: Unique identifier of the user

        Returns:
            True if user exists, False otherwise
        """
        return user_id in self._users


class InMemorySearchQueryRepository(AbstractSearchQueryRepository):
    """In-memory implementation of the SearchQuery repository."""

    def __init__(self) -> None:
        """Initialize the in-memory search query repository."""
        self._search_queries: Dict[str, SearchQuery] = {}
        self._user_queries_index: Dict[str, List[str]] = {}  # user_id -> list of query_ids
        self._text_prefix_index: Dict[str, List[str]] = {}  # prefix -> list of query_ids

    def save_search_query(self, search_query: SearchQuery) -> None:
        """Save a search query to the in-memory repository.

        Args:
            search_query: SearchQuery entity to save
        """
        self._search_queries[search_query.query_id] = search_query

        # Update user queries index
        if search_query.user_id not in self._user_queries_index:
            self._user_queries_index[search_query.user_id] = []
        if search_query.query_id not in self._user_queries_index[search_query.user_id]:
            self._user_queries_index[search_query.user_id].append(search_query.query_id)

        # Update text prefix index for auto-complete
        self._update_text_prefix_index(search_query)

    def _update_text_prefix_index(self, search_query: SearchQuery) -> None:
        """Update the text prefix index for auto-complete functionality.

        Args:
            search_query: SearchQuery entity to index
        """
        query_text = search_query.query_text.lower()
        for i in range(1, len(query_text) + 1):
            prefix = query_text[:i]
            if prefix not in self._text_prefix_index:
                self._text_prefix_index[prefix] = []
            if search_query.query_id not in self._text_prefix_index[prefix]:
                self._text_prefix_index[prefix].append(search_query.query_id)

    def get_search_query_by_id(self, query_id: str) -> Optional[SearchQuery]:
        """Retrieve a search query by its ID.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            SearchQuery entity if found, None otherwise
        """
        return self._search_queries.get(query_id)

    def get_search_queries_by_user_id(self, user_id: str) -> List[SearchQuery]:
        """Retrieve all search queries for a specific user.

        Args:
            user_id: Unique identifier of the user

        Returns:
            List of SearchQuery entities for the user
        """
        query_ids = self._user_queries_index.get(user_id, [])
        return [self._search_queries[qid] for qid in query_ids if qid in self._search_queries]

    def get_all_search_queries(self) -> List[SearchQuery]:
        """Retrieve all search queries from the repository.

        Returns:
            List of all SearchQuery entities
        """
        return list(self._search_queries.values())

    def get_search_queries_by_text_prefix(self, text_prefix: str) -> List[SearchQuery]:
        """Retrieve search queries that start with the given text prefix.

        Args:
            text_prefix: Text prefix to search for

        Returns:
            List of SearchQuery entities matching the prefix
        """
        prefix = text_prefix.lower()
        query_ids = self._text_prefix_index.get(prefix, [])
        return [self._search_queries[qid] for qid in query_ids if qid in self._search_queries]

    def update_search_query(self, search_query: SearchQuery) -> None:
        """Update an existing search query in the repository.

        Args:
            search_query: SearchQuery entity with updated information
        """
        if search_query.query_id in self._search_queries:
            # Remove old prefix index entries
            old_query = self._search_queries[search_query.query_id]
            self._remove_from_text_prefix_index(old_query)

            # Update the query
            self._search_queries[search_query.query_id] = search_query

            # Update prefix index with new query
            self._update_text_prefix_index(search_query)

    def _remove_from_text_prefix_index(self, search_query: SearchQuery) -> None:
        """Remove a search query from the text prefix index.

        Args:
            search_query: SearchQuery entity to remove from index
        """
        query_text = search_query.query_text.lower()
        for i in range(1, len(query_text) + 1):
            prefix = query_text[:i]
            if prefix in self._text_prefix_index and search_query.query_id in self._text_prefix_index[prefix]:
                self._text_prefix_index[prefix].remove(search_query.query_id)
                if not self._text_prefix_index[prefix]:
                    del self._text_prefix_index[prefix]

    def increment_query_frequency(self, query_id: str) -> bool:
        """Increment the frequency count of a search query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if frequency was incremented, False if query not found
        """
        if query_id in self._search_queries:
            self._search_queries[query_id].increment_frequency()
            return True
        return False

    def delete_search_query(self, query_id: str) -> bool:
        """Delete a search query from the repository.

        Args:
            query_id: Unique identifier of the search query to delete

        Returns:
            True if query was deleted, False if not found
        """
        if query_id in self._search_queries:
            search_query = self._search_queries[query_id]

            # Remove from user queries index
            if search_query.user_id in self._user_queries_index:
                if query_id in self._user_queries_index[search_query.user_id]:
                    self._user_queries_index[search_query.user_id].remove(query_id)
                if not self._user_queries_index[search_query.user_id]:
                    del self._user_queries_index[search_query.user_id]

            # Remove from text prefix index
            self._remove_from_text_prefix_index(search_query)

            # Remove from main storage
            del self._search_queries[query_id]
            return True
        return False

    def search_query_exists(self, query_id: str) -> bool:
        """Check if a search query exists in the repository.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            True if query exists, False otherwise
        """
        return query_id in self._search_queries


class InMemorySearchResultRepository(AbstractSearchResultRepository):
    """In-memory implementation of the SearchResult repository."""

    def __init__(self) -> None:
        """Initialize the in-memory search result repository."""
        self._search_results: Dict[str, SearchResult] = {}
        self._query_results_index: Dict[str, List[str]] = {}  # query_id -> list of result_ids

    def save_search_result(self, search_result: SearchResult) -> None:
        """Save a search result to the in-memory repository.

        Args:
            search_result: SearchResult entity to save
        """
        self._search_results[search_result.result_id] = search_result

        # Update query results index
        if search_result.query_id not in self._query_results_index:
            self._query_results_index[search_result.query_id] = []
        if search_result.result_id not in self._query_results_index[search_result.query_id]:
            self._query_results_index[search_result.query_id].append(search_result.result_id)

    def get_search_result_by_id(self, result_id: str) -> Optional[SearchResult]:
        """Retrieve a search result by its ID.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            SearchResult entity if found, None otherwise
        """
        return self._search_results.get(result_id)

    def get_search_results_by_query_id(self, query_id: str) -> List[SearchResult]:
        """Retrieve all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            List of SearchResult entities for the query
        """
        result_ids = self._query_results_index.get(query_id, [])
        return [self._search_results[rid] for rid in result_ids if rid in self._search_results]

    def get_search_results_by_relevance_score_range(self, min_score: float, max_score: float) -> List[SearchResult]:
        """Retrieve search results within a relevance score range.

        Args:
            min_score: Minimum relevance score (inclusive)
            max_score: Maximum relevance score (inclusive)

        Returns:
            List of SearchResult entities within the score range
        """
        return [
            result for result in self._search_results.values()
            if min_score <= result.relevance_score <= max_score
        ]

    def get_top_search_results_by_query_id(self, query_id: str, limit: int) -> List[SearchResult]:
        """Retrieve top search results for a query ordered by relevance score.

        Args:
            query_id: Unique identifier of the search query
            limit: Maximum number of results to return

        Returns:
            List of top SearchResult entities ordered by relevance score descending
        """
        results = self.get_search_results_by_query_id(query_id)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:limit]

    def get_all_search_results(self) -> List[SearchResult]:
        """Retrieve all search results from the repository.

        Returns:
            List of all SearchResult entities
        """
        return list(self._search_results.values())

    def update_search_result(self, search_result: SearchResult) -> None:
        """Update an existing search result in the repository.

        Args:
            search_result: SearchResult entity with updated information
        """
        if search_result.result_id in self._search_results:
            self._search_results[search_result.result_id] = search_result

    def delete_search_result(self, result_id: str) -> bool:
        """Delete a search result from the repository.

        Args:
            result_id: Unique identifier of the search result to delete

        Returns:
            True if result was deleted, False if not found
        """
        if result_id in self._search_results:
            search_result = self._search_results[result_id]

            # Remove from query results index
            if search_result.query_id in self._query_results_index:
                if result_id in self._query_results_index[search_result.query_id]:
                    self._query_results_index[search_result.query_id].remove(result_id)
                if not self._query_results_index[search_result.query_id]:
                    del self._query_results_index[search_result.query_id]

            # Remove from main storage
            del self._search_results[result_id]
            return True
        return False

    def delete_search_results_by_query_id(self, query_id: str) -> int:
        """Delete all search results for a specific query.

        Args:
            query_id: Unique identifier of the search query

        Returns:
            Number of search results deleted
        """
        if query_id in self._query_results_index:
            result_ids = self._query_results_index[query_id][:]
            deleted_count = 0

            for result_id in result_ids:
                if self.delete_search_result(result_id):
                    deleted_count += 1

            return deleted_count
        return 0

    def search_result_exists(self, result_id: str) -> bool:
        """Check if a search result exists in the repository.

        Args:
            result_id: Unique identifier of the search result

        Returns:
            True if result exists, False otherwise
        """
        return result_id in self._search_results
