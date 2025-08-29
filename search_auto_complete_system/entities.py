from typing import List, Optional
from datetime import datetime


class User:
    """Represents a user in the search auto-complete system."""

    def __init__(self, user_id: str, username: str, email: str) -> None:
        """Initialize a User entity.

        Args:
            user_id: Unique identifier for the user
            username: Username for the user
            email: Email address of the user

        Raises:
            ValueError: If any required fields are empty or invalid
        """
        self._validate_user_data(user_id, username, email)

        self.user_id: str = user_id
        self.username: str = username
        self.email: str = email
        self.created_at: datetime = datetime.now()
        self.is_active: bool = True

    def _validate_user_data(self, user_id: str, username: str, email: str) -> None:
        """Validate user data during initialization.

        Args:
            user_id: User ID to validate
            username: Username to validate
            email: Email to validate

        Raises:
            ValueError: If validation fails
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

        if not username or not username.strip():
            raise ValueError("Username cannot be empty")

        if not email or not email.strip():
            raise ValueError("Email cannot be empty")

        if "@" not in email:
            raise ValueError("Email must be valid format")

    def update_username(self, new_username: str) -> None:
        """Update the user's username.

        Args:
            new_username: New username for the user

        Raises:
            ValueError: If username is invalid
        """
        if not new_username or not new_username.strip():
            raise ValueError("Username cannot be empty")
        self.username = new_username

    def update_email(self, new_email: str) -> None:
        """Update the user's email.

        Args:
            new_email: New email for the user

        Raises:
            ValueError: If email is invalid
        """
        if not new_email or not new_email.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in new_email:
            raise ValueError("Email must be valid format")
        self.email = new_email

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

    def __str__(self) -> str:
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"

    def __repr__(self) -> str:
        return self.__str__()


class SearchQuery:
    """Represents a search query in the auto-complete system."""

    def __init__(self, query_id: str, user_id: str, query_text: str) -> None:
        """Initialize a SearchQuery entity.

        Args:
            query_id: Unique identifier for the search query
            user_id: ID of the user who made the query
            query_text: The actual search text

        Raises:
            ValueError: If any required fields are empty or invalid
        """
        self._validate_query_data(query_id, user_id, query_text)

        self.query_id: str = query_id
        self.user_id: str = user_id
        self.query_text: str = query_text.strip()
        self.created_at: datetime = datetime.now()
        self.frequency_count: int = 1

    def _validate_query_data(self, query_id: str, user_id: str, query_text: str) -> None:
        """Validate search query data during initialization.

        Args:
            query_id: Query ID to validate
            user_id: User ID to validate
            query_text: Query text to validate

        Raises:
            ValueError: If validation fails
        """
        if not query_id or not query_id.strip():
            raise ValueError("Query ID cannot be empty")

        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

    def increment_frequency(self) -> None:
        """Increment the frequency count of this query."""
        self.frequency_count += 1

    def get_query_length(self) -> int:
        """Get the length of the query text.

        Returns:
            Length of the query text
        """
        return len(self.query_text)

    def get_words(self) -> List[str]:
        """Split the query into individual words.

        Returns:
            List of words in the query
        """
        return self.query_text.split()

    def __str__(self) -> str:
        return f"SearchQuery(id={self.query_id}, text='{self.query_text}', freq={self.frequency_count})"

    def __repr__(self) -> str:
        return self.__str__()


class SearchResult:
    """Represents a search result in the auto-complete system."""

    def __init__(self, result_id: str, query_id: str, suggested_word: str, relevance_score: float) -> None:
        """Initialize a SearchResult entity.

        Args:
            result_id: Unique identifier for the search result
            query_id: ID of the query this result belongs to
            suggested_word: The suggested word/phrase
            relevance_score: Score indicating how relevant this result is (0.0 to 1.0)

        Raises:
            ValueError: If any required fields are invalid
        """
        self._validate_result_data(result_id, query_id, suggested_word, relevance_score)

        self.result_id: str = result_id
        self.query_id: str = query_id
        self.suggested_word: str = suggested_word.strip()
        self.relevance_score: float = relevance_score
        self.created_at: datetime = datetime.now()

    def _validate_result_data(self, result_id: str, query_id: str, suggested_word: str, relevance_score: float) -> None:
        """Validate search result data during initialization.

        Args:
            result_id: Result ID to validate
            query_id: Query ID to validate
            suggested_word: Suggested word to validate
            relevance_score: Relevance score to validate

        Raises:
            ValueError: If validation fails
        """
        if not result_id or not result_id.strip():
            raise ValueError("Result ID cannot be empty")

        if not query_id or not query_id.strip():
            raise ValueError("Query ID cannot be empty")

        if not suggested_word or not suggested_word.strip():
            raise ValueError("Suggested word cannot be empty")

        if not (0.0 <= relevance_score <= 1.0):
            raise ValueError("Relevance score must be between 0.0 and 1.0")

    def update_relevance_score(self, new_score: float) -> None:
        """Update the relevance score of this result.

        Args:
            new_score: New relevance score (0.0 to 1.0)

        Raises:
            ValueError: If score is invalid
        """
        if not (0.0 <= new_score <= 1.0):
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        self.relevance_score = new_score

    def get_word_length(self) -> int:
        """Get the length of the suggested word.

        Returns:
            Length of the suggested word
        """
        return len(self.suggested_word)

    def __str__(self) -> str:
        return f"SearchResult(id={self.result_id}, word='{self.suggested_word}', score={self.relevance_score:.2f})"

    def __repr__(self) -> str:
        return self.__str__()
