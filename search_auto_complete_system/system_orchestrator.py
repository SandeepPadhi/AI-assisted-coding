import uuid
from typing import List, Optional, Tuple
from managers import UserManager, SearchQueryManager, SearchResultManager
from in_memory_repositories import InMemoryUserRepository, InMemorySearchQueryRepository, InMemorySearchResultRepository
from entities import User, SearchQuery, SearchResult


class SearchAutoCompleteSystem:
    """Main orchestrator for the search auto-complete system."""

    def __init__(self) -> None:
        """Initialize the search auto-complete system with in-memory repositories."""
        # Initialize repositories
        self.user_repository = InMemoryUserRepository()
        self.search_query_repository = InMemorySearchQueryRepository()
        self.search_result_repository = InMemorySearchResultRepository()

        # Initialize managers
        self.user_manager = UserManager(self.user_repository)
        self.search_query_manager = SearchQueryManager(self.search_query_repository)
        self.search_result_manager = SearchResultManager(self.search_result_repository)

    def register_user(self, username: str, email: str) -> User:
        """Register a new user in the system.

        Args:
            username: Username for the new user
            email: Email address for the new user

        Returns:
            Newly created User entity

        Raises:
            ValueError: If username or email already exists or are invalid
        """
        return self.user_manager.create_user(username, email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username.

        Args:
            username: Username of the user

        Returns:
            User entity if found, None otherwise
        """
        return self.user_manager.get_user_by_username(username)

    def search_with_auto_complete(self, username: str, query_text: str, max_results: int = 5) -> Tuple[SearchQuery, List[str]]:
        """Perform a search with auto-complete functionality.

        Args:
            username: Username of the user performing the search
            query_text: The search query text
            max_results: Maximum number of auto-complete suggestions to return

        Returns:
            Tuple of (SearchQuery entity, List of suggested words/phrases)

        Raises:
            ValueError: If user doesn't exist or query is empty
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        # Get user
        user = self.user_manager.get_user_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")

        # Create or update search query
        search_query = self.search_query_manager.create_search_query(user.user_id, query_text)

        # Generate auto-complete suggestions
        suggestions = self._generate_auto_complete_suggestions(query_text, max_results)

        return search_query, suggestions

    def _generate_auto_complete_suggestions(self, query_text: str, max_results: int) -> List[str]:
        """Generate intelligent auto-complete suggestions using advanced matching algorithms.

        Args:
            query_text: The search query text
            max_results: Maximum number of suggestions to return

        Returns:
            List of suggested words/phrases
        """
        suggestions = []
        query_lower = query_text.lower().strip()
        seen_words = set()

        # Get ALL queries to search through them
        all_queries = self.search_query_manager.get_all_search_queries()

        # Score and rank potential suggestions
        scored_suggestions = []

        for query in all_queries:
            query_text_lower = query.query_text.lower()

            # Skip if query is the same as input
            if query_text_lower == query_lower:
                continue

            # Calculate comprehensive match score
            match_score = self._calculate_match_score(query_lower, query_text_lower)

            if match_score > 0:
                # Boost score by frequency and recency
                frequency_boost = min(query.frequency_count * 0.15, 2.0)  # Cap at 2.0x boost
                final_score = match_score * (1 + frequency_boost)

                scored_suggestions.append((query.query_text, final_score, query.frequency_count))

        # Sort by score (descending) then by frequency (descending)
        scored_suggestions.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Extract top suggestions
        for suggestion_text, score, frequency in scored_suggestions:
            if len(suggestions) >= max_results:
                break

            if suggestion_text not in seen_words:
                suggestions.append(suggestion_text)
                seen_words.add(suggestion_text)

        return suggestions

    def _calculate_match_score(self, query: str, candidate: str) -> float:
        """Calculate a comprehensive match score between query and candidate text.

        Args:
            query: The user's search query
            candidate: The candidate suggestion text

        Returns:
            Match score between 0.0 and 1.0
        """
        if not query or not candidate:
            return 0.0

        # 1. EXACT PREFIX MATCH (Highest priority)
        if candidate.startswith(query):
            return 1.0

        # 2. WORD-BASED MATCHING
        query_words = self._tokenize_text(query)
        candidate_words = self._tokenize_text(candidate)

        # Perfect word matches at start
        if candidate_words and query_words and candidate_words[0].startswith(query_words[0]):
            return 0.95

        # 3. PARTIAL WORD COMPLETION (e.g., "pyth" -> "python")
        for candidate_word in candidate_words:
            for query_word in query_words:
                if candidate_word.startswith(query_word) and len(candidate_word) > len(query_word):
                    # Higher score for longer completions
                    completion_ratio = len(query_word) / len(candidate_word)
                    return 0.85 * (1 + completion_ratio)

        # 4. SUBSTRING MATCHING WITH POSITION BONUS
        query_len = len(query)
        candidate_len = len(candidate)

        # Find best substring match
        best_substring_score = 0.0
        for i in range(len(candidate) - query_len + 1):
            if candidate[i:i + query_len] == query:
                # Bonus for matches at word boundaries
                position_bonus = 1.0
                if i == 0:  # Start of text
                    position_bonus = 1.2
                elif candidate[i-1] in ' -_':  # Start of word
                    position_bonus = 1.1

                substring_score = 0.75 * position_bonus
                best_substring_score = max(best_substring_score, substring_score)

        if best_substring_score > 0:
            return best_substring_score

        # 5. FUZZY WORD MATCHING
        common_words = set(query_words) & set(candidate_words)
        if common_words:
            # Score based on proportion of common words
            word_overlap_score = len(common_words) / len(query_words)
            return 0.5 * word_overlap_score

        # 6. EDIT DISTANCE MATCHING (Typo tolerance)
        edit_distance = self._calculate_edit_distance(query, candidate)
        max_len = max(len(query), len(candidate))
        if max_len > 0:
            edit_similarity = 1 - (edit_distance / max_len)
            if edit_similarity > 0.7:  # Only consider if >70% similar
                return 0.3 * edit_similarity

        # 7. CHARACTER-LEVEL FUZZY MATCHING
        # Check if query characters appear in order (allowing skips)
        query_chars = list(query.lower())
        candidate_chars = list(candidate.lower())

        char_match_score = self._calculate_character_match_score(query_chars, candidate_chars)
        if char_match_score > 0.6:  # Only consider if >60% character match
            return 0.25 * char_match_score

        return 0.0

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words, handling various separators.

        Args:
            text: Text to tokenize

        Returns:
            List of word tokens
        """
        import re
        # Split on whitespace, hyphens, underscores, and camelCase
        words = re.findall(r'[a-zA-Z]+(?:[A-Z][a-z]*)*|[a-zA-Z]+', text.lower())
        return [word for word in words if len(word) > 1]  # Filter out single characters

    def _calculate_edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance (number of operations needed)
        """
        if len(s1) < len(s2):
            return self._calculate_edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _calculate_character_match_score(self, query_chars: List[str], candidate_chars: List[str]) -> float:
        """Calculate character-level match score allowing for skips.

        Args:
            query_chars: Query characters
            candidate_chars: Candidate characters

        Returns:
            Match score between 0.0 and 1.0
        """
        if not query_chars or not candidate_chars:
            return 0.0

        matches = 0
        query_idx = 0

        for candidate_char in candidate_chars:
            if query_idx < len(query_chars) and candidate_char == query_chars[query_idx]:
                matches += 1
                query_idx += 1

        return matches / len(query_chars)

    def add_manual_suggestion(self, query_id: str, suggested_word: str, relevance_score: float) -> SearchResult:
        """Add a manual suggestion for a search query.

        Args:
            query_id: ID of the search query
            suggested_word: The suggested word/phrase
            relevance_score: Relevance score (0.0 to 1.0)

        Returns:
            Newly created SearchResult entity

        Raises:
            ValueError: If query doesn't exist
        """
        if not self.search_query_manager.search_query_exists(query_id):
            raise ValueError(f"Search query with ID '{query_id}' not found")

        return self.search_result_manager.create_search_result(query_id, suggested_word, relevance_score)

    def get_user_search_history(self, username: str) -> List[SearchQuery]:
        """Get the search history for a user.

        Args:
            username: Username of the user

        Returns:
            List of SearchQuery entities for the user

        Raises:
            ValueError: If user doesn't exist
        """
        user = self.user_manager.get_user_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")

        return self.search_query_manager.get_user_search_queries(user.user_id)

    def get_popular_searches(self, limit: int = 10) -> List[SearchQuery]:
        """Get the most popular search queries across all users.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of most popular SearchQuery entities
        """
        return self.search_query_manager.get_popular_search_queries(limit)

    def get_search_suggestions_for_query(self, query_id: str, limit: int = 5) -> List[SearchResult]:
        """Get search suggestions for a specific query.

        Args:
            query_id: ID of the search query
            limit: Maximum number of suggestions to return

        Returns:
            List of SearchResult entities ordered by relevance
        """
        return self.search_result_manager.get_top_search_results_for_query(query_id, limit)

    def remove_user_data(self, username: str) -> bool:
        """Remove all data associated with a user.

        Args:
            username: Username of the user

        Returns:
            True if user data was removed successfully, False otherwise
        """
        user = self.user_manager.get_user_by_username(username)
        if not user:
            return False

        # Get all user's search queries
        user_queries = self.search_query_manager.get_user_search_queries(user.user_id)

        # Delete all search results for user's queries
        for query in user_queries:
            self.search_result_manager.delete_all_results_for_query(query.query_id)

        # Delete all user's search queries
        for query in user_queries:
            self.search_query_manager.delete_search_query(query.query_id)

        # Delete the user
        return self.user_manager.delete_user(user.user_id)

    def get_system_statistics(self) -> dict:
        """Get statistics about the search auto-complete system.

        Returns:
            Dictionary containing system statistics
        """
        total_users = len(self.user_manager.get_all_users())
        total_queries = len(self.search_query_repository.get_all_search_queries())
        total_suggestions = len(self.search_result_repository.get_all_search_results())

        # Calculate average query frequency
        all_queries = self.search_query_repository.get_all_search_queries()
        avg_frequency = sum(q.frequency_count for q in all_queries) / len(all_queries) if all_queries else 0

        return {
            "total_users": total_users,
            "total_search_queries": total_queries,
            "total_suggestions": total_suggestions,
            "average_query_frequency": round(avg_frequency, 2)
        }

    def clear_all_data(self) -> None:
        """Clear all data from the system (useful for testing)."""
        # This would need to be implemented differently for persistent storage
        # For in-memory, we can recreate the repositories
        self.user_repository = InMemoryUserRepository()
        self.search_query_repository = InMemorySearchQueryRepository()
        self.search_result_repository = InMemorySearchResultRepository()

        # Reinitialize managers
        self.user_manager = UserManager(self.user_repository)
        self.search_query_manager = SearchQueryManager(self.search_query_repository)
        self.search_result_manager = SearchResultManager(self.search_result_repository)
