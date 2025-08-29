"""
Unit tests for Candidate Manager.

Tests cover:
- Candidate creation and validation
- Candidate verification management
- Party-based operations
- Business logic validation
- Error handling
"""

import pytest
from entities import Candidate
from managers import CandidateManager
from repositories import InMemoryCandidateRepository


class TestCandidateManager:
    """Test cases for CandidateManager"""

    def test_manager_initialization(self, candidate_manager):
        """Test manager initialization"""
        assert candidate_manager is not None
        assert hasattr(candidate_manager, '_candidate_repository')
        assert isinstance(candidate_manager._candidate_repository, InMemoryCandidateRepository)

    def test_create_candidate_valid(self, candidate_manager):
        """Test creating a valid candidate"""
        candidate_data = {
            "candidate_id": "candidate_123",
            "name": "Jane Smith",
            "party": "Democratic Party",
            "description": "Experienced leader with focus on education"
        }

        candidate = candidate_manager.create_candidate(**candidate_data)

        assert candidate is not None
        assert candidate.candidate_id == candidate_data["candidate_id"]
        assert candidate.name == candidate_data["name"]
        assert candidate.party == candidate_data["party"]
        assert candidate.description == candidate_data["description"]
        assert candidate.verified == False  # Default should be False

    def test_create_candidate_invalid_data(self, candidate_manager):
        """Test creating candidate with invalid data"""
        # Invalid candidate ID
        with pytest.raises(ValueError, match="Invalid candidate ID"):
            candidate_manager.create_candidate("", "Jane Smith", "Democratic", "Description")

        # Invalid party
        with pytest.raises(ValueError, match="Invalid party"):
            candidate_manager.create_candidate("candidate_123", "Jane Smith", "", "Description")

        # Invalid description
        with pytest.raises(ValueError, match="Invalid description"):
            candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "")

    def test_get_candidate_by_id_existing(self, candidate_manager):
        """Test getting existing candidate by ID"""
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")

        found_candidate = candidate_manager.get_candidate_by_id("candidate_123")

        assert found_candidate is not None
        assert found_candidate == candidate

    def test_get_candidate_by_id_nonexistent(self, candidate_manager):
        """Test getting non-existent candidate by ID"""
        found_candidate = candidate_manager.get_candidate_by_id("nonexistent_id")

        assert found_candidate is None

    def test_get_all_candidates_empty(self, candidate_manager):
        """Test getting all candidates when none exist"""
        candidates = candidate_manager.get_all_candidates()

        assert isinstance(candidates, list)
        assert len(candidates) == 0

    def test_get_all_candidates_with_data(self, candidate_manager):
        """Test getting all candidates"""
        # Create multiple candidates
        candidates = []
        for i in range(3):
            candidate = candidate_manager.create_candidate(
                f"candidate_{i}",
                f"Candidate {i}",
                f"Party {i}",
                f"Description {i}"
            )
            candidates.append(candidate)

        found_candidates = candidate_manager.get_all_candidates()

        assert len(found_candidates) == 3
        assert set(found_candidates) == set(candidates)

    def test_verify_candidate_existing(self, candidate_manager):
        """Test verifying existing candidate"""
        # Create candidate
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")
        assert candidate.verified == False

        # Verify candidate
        result = candidate_manager.verify_candidate("candidate_123")

        assert result is True

        # Check candidate was verified
        verified_candidate = candidate_manager.get_candidate_by_id("candidate_123")
        assert verified_candidate.verified == True

    def test_verify_candidate_nonexistent(self, candidate_manager):
        """Test verifying non-existent candidate"""
        result = candidate_manager.verify_candidate("nonexistent_id")

        assert result is False

    def test_unverify_candidate_existing(self, candidate_manager):
        """Test unverifying existing candidate"""
        # Create and verify candidate
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")
        candidate_manager.verify_candidate("candidate_123")

        # Unverify candidate
        result = candidate_manager.unverify_candidate("candidate_123")

        assert result is True

        # Check candidate was unverified
        unverified_candidate = candidate_manager.get_candidate_by_id("candidate_123")
        assert unverified_candidate.verified == False

    def test_unverify_candidate_nonexistent(self, candidate_manager):
        """Test unverifying non-existent candidate"""
        result = candidate_manager.unverify_candidate("nonexistent_id")

        assert result is False

    def test_delete_candidate_existing(self, candidate_manager):
        """Test deleting existing candidate"""
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")

        result = candidate_manager.delete_candidate("candidate_123")

        assert result is True
        assert candidate_manager.get_candidate_by_id("candidate_123") is None

    def test_delete_candidate_nonexistent(self, candidate_manager):
        """Test deleting non-existent candidate"""
        result = candidate_manager.delete_candidate("nonexistent_id")

        assert result is False

    def test_get_candidates_by_party(self, candidate_manager):
        """Test getting candidates by party"""
        # Create candidates with different parties
        parties = ["Democratic", "Republican", "Independent"]
        candidates_by_party = {}

        for party in parties:
            candidates_by_party[party] = []
            for i in range(2):
                candidate = candidate_manager.create_candidate(
                    f"candidate_{party}_{i}",
                    f"Candidate {party} {i}",
                    party,
                    f"Description for {party}"
                )
                candidates_by_party[party].append(candidate)

        # Test finding by each party
        for party in parties:
            found_candidates = candidate_manager.get_candidates_by_party(party)
            assert len(found_candidates) == 2
            assert set(found_candidates) == set(candidates_by_party[party])

    def test_get_candidates_by_party_case_insensitive(self, candidate_manager):
        """Test party search is case insensitive"""
        candidate = candidate_manager.create_candidate("candidate_123", "Jane", "Democratic Party", "Description")

        # Search with different cases
        found1 = candidate_manager.get_candidates_by_party("democratic party")
        found2 = candidate_manager.get_candidates_by_party("DEMOCRATIC PARTY")

        assert len(found1) == 1
        assert len(found2) == 1
        assert found1[0] == candidate
        assert found2[0] == candidate

    def test_get_verified_candidates(self, candidate_manager):
        """Test getting verified candidates"""
        # Create verified and unverified candidates
        verified = candidate_manager.create_candidate("verified", "Verified", "Party", "Description")
        unverified = candidate_manager.create_candidate("unverified", "Unverified", "Party", "Description")

        candidate_manager.verify_candidate("verified")

        verified_candidates = candidate_manager.get_verified_candidates()
        assert len(verified_candidates) == 1
        assert verified_candidates[0] == verified

    def test_get_unverified_candidates(self, candidate_manager):
        """Test getting unverified candidates"""
        # Create verified and unverified candidates
        verified = candidate_manager.create_candidate("verified", "Verified", "Party", "Description")
        unverified = candidate_manager.create_candidate("unverified", "Unverified", "Party", "Description")

        candidate_manager.verify_candidate("verified")

        unverified_candidates = candidate_manager.get_unverified_candidates()
        assert len(unverified_candidates) == 1
        assert unverified_candidates[0] == unverified

    def test_get_candidates_by_verification_status(self, candidate_manager):
        """Test getting candidates by verification status"""
        verified = candidate_manager.create_candidate("v1", "Verified", "Party", "Desc")
        unverified = candidate_manager.create_candidate("v2", "Unverified", "Party", "Desc")

        candidate_manager.verify_candidate("v1")

        # Test verified
        verified_results = candidate_manager.get_candidates_by_verification_status(True)
        assert len(verified_results) == 1
        assert verified_results[0] == verified

        # Test unverified
        unverified_results = candidate_manager.get_candidates_by_verification_status(False)
        assert len(unverified_results) == 1
        assert unverified_results[0] == unverified

    def test_candidate_exists_by_id(self, candidate_manager):
        """Test checking if candidate exists by ID"""
        assert not candidate_manager.candidate_exists_by_id("candidate_123")

        candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")

        assert candidate_manager.candidate_exists_by_id("candidate_123")

    def test_count_candidates(self, candidate_manager):
        """Test counting candidates"""
        assert candidate_manager.count_candidates() == 0

        for i in range(5):
            candidate_manager.create_candidate(f"candidate_{i}", f"Candidate {i}", "Party", "Description")

        assert candidate_manager.count_candidates() == 5

    def test_count_candidates_by_party(self, candidate_manager):
        """Test counting candidates by party"""
        # Create candidates with different parties
        parties = ["Democratic", "Republican", "Independent"]
        counts = [3, 2, 1]

        for party, count in zip(parties, counts):
            for i in range(count):
                candidate_manager.create_candidate(f"candidate_{party}_{i}", f"Candidate {i}", party, "Description")

        for party, expected_count in zip(parties, counts):
            assert candidate_manager.count_candidates_by_party(party) == expected_count

    def test_count_verified_candidates(self, candidate_manager):
        """Test counting verified candidates"""
        # Create candidates
        for i in range(5):
            candidate_manager.create_candidate(f"candidate_{i}", f"Candidate {i}", "Party", "Description")

        # Verify some candidates
        for i in range(3):
            candidate_manager.verify_candidate(f"candidate_{i}")

        assert candidate_manager.count_verified_candidates() == 3
        assert candidate_manager.count_unverified_candidates() == 2

    def test_get_all_parties(self, candidate_manager):
        """Test getting all unique parties"""
        parties = ["Party A", "Party B", "Party C", "Party A"]  # Duplicate party

        for i, party in enumerate(parties):
            candidate_manager.create_candidate(f"candidate_{i}", f"Candidate {i}", party, "Description")

        all_parties = candidate_manager.get_all_parties()
        assert len(all_parties) == 3  # Should be unique
        assert set(all_parties) == {"Party A", "Party B", "Party C"}

    def test_update_candidate_party(self, candidate_manager):
        """Test updating candidate party"""
        candidate = candidate_manager.create_candidate("candidate_123", "Jane", "Old Party", "Description")

        result = candidate_manager.update_candidate_party("candidate_123", "New Party")

        assert result is True

        updated_candidate = candidate_manager.get_candidate_by_id("candidate_123")
        assert updated_candidate.party == "New Party"

    def test_update_candidate_party_invalid(self, candidate_manager):
        """Test updating candidate party with invalid data"""
        candidate_manager.create_candidate("candidate_123", "Jane", "Party", "Description")

        # Invalid party
        with pytest.raises(ValueError, match="Invalid party"):
            candidate_manager.update_candidate_party("candidate_123", "")

        # Non-existent candidate
        result = candidate_manager.update_candidate_party("nonexistent", "New Party")
        assert result is False

    def test_update_candidate_description(self, candidate_manager):
        """Test updating candidate description"""
        candidate = candidate_manager.create_candidate("candidate_123", "Jane", "Party", "Old Description")

        new_description = "Updated description with new achievements"
        result = candidate_manager.update_candidate_description("candidate_123", new_description)

        assert result is True

        updated_candidate = candidate_manager.get_candidate_by_id("candidate_123")
        assert updated_candidate.description == new_description

    def test_update_candidate_description_invalid(self, candidate_manager):
        """Test updating candidate description with invalid data"""
        candidate_manager.create_candidate("candidate_123", "Jane", "Party", "Description")

        # Invalid description
        with pytest.raises(ValueError, match="Invalid description"):
            candidate_manager.update_candidate_description("candidate_123", "")

        # Non-existent candidate
        result = candidate_manager.update_candidate_description("nonexistent", "New description")
        assert result is False

    def test_bulk_candidate_operations(self, candidate_manager):
        """Test bulk candidate operations"""
        # Create many candidates
        candidates = []
        for i in range(50):
            candidate = candidate_manager.create_candidate(
                f"candidate_{i}",
                f"Candidate {i}",
                f"Party {i % 3}",
                f"Description {i}"
            )
            candidates.append(candidate)

        assert candidate_manager.count_candidates() == 50

        # Bulk verification
        for i in range(25):
            candidate_manager.verify_candidate(f"candidate_{i}")

        assert candidate_manager.count_verified_candidates() == 25
        assert candidate_manager.count_unverified_candidates() == 25

    def test_candidate_data_integrity(self, candidate_manager):
        """Test candidate data integrity across operations"""
        # Create candidate
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")
        original_data = {
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "party": candidate.party,
            "description": candidate.description,
            "verified": candidate.verified
        }

        # Update operations
        candidate_manager.verify_candidate("candidate_123")
        candidate_manager.update_candidate_party("candidate_123", "Republican")
        candidate_manager.update_candidate_description("candidate_123", "New description")

        # Retrieve and verify data integrity
        retrieved_candidate = candidate_manager.get_candidate_by_id("candidate_123")
        assert retrieved_candidate.candidate_id == original_data["candidate_id"]
        assert retrieved_candidate.name == original_data["name"]
        assert retrieved_candidate.party == "Republican"  # Should be updated
        assert retrieved_candidate.description == "New description"  # Should be updated
        assert retrieved_candidate.verified == True  # Should be updated

    def test_candidate_manager_error_handling(self, candidate_manager):
        """Test error handling in candidate manager"""
        # Test with None values
        with pytest.raises(TypeError):
            candidate_manager.create_candidate(None, "Jane", "Party", "Description")

        with pytest.raises(TypeError):
            candidate_manager.get_candidate_by_id(None)

    def test_candidate_manager_repository_integration(self, candidate_manager):
        """Test integration between manager and repository"""
        # Create candidate through manager
        candidate = candidate_manager.create_candidate("candidate_123", "Jane Smith", "Democratic", "Description")

        # Verify repository has the candidate
        repo_candidate = candidate_manager._candidate_repository.find_by_id("candidate_123")
        assert repo_candidate is not None
        assert repo_candidate == candidate

        # Delete through manager
        candidate_manager.delete_candidate("candidate_123")

        # Verify repository no longer has the candidate
        assert candidate_manager._candidate_repository.find_by_id("candidate_123") is None

    def test_candidate_manager_statistics(self, candidate_manager):
        """Test candidate manager statistics functionality"""
        # Create candidates with different characteristics
        parties = ["Democratic", "Republican", "Independent"]
        for party in parties:
            for i in range(3):
                candidate = candidate_manager.create_candidate(
                    f"candidate_{party}_{i}",
                    f"Candidate {party} {i}",
                    party,
                    f"Description for {party}"
                )

        # Verify first few candidates
        for i in range(5):
            candidate_manager.verify_candidate(f"candidate_Democratic_{i % 3}")

        # Test statistics
        stats = {
            "total_candidates": candidate_manager.count_candidates(),
            "verified_candidates": candidate_manager.count_verified_candidates(),
            "unverified_candidates": candidate_manager.count_unverified_candidates(),
            "parties": candidate_manager.get_all_parties(),
            "candidates_by_party": {
                party: candidate_manager.count_candidates_by_party(party)
                for party in parties
            }
        }

        assert stats["total_candidates"] == 9
        assert stats["verified_candidates"] == 3
        assert stats["unverified_candidates"] == 6
        assert len(stats["parties"]) == 3
        for party in parties:
            assert stats["candidates_by_party"][party] == 3
