"""
Unit tests for Candidate Repository.

Tests cover:
- Candidate CRUD operations
- Thread-safe operations
- Verification status queries
- Party-based queries
- Error handling
"""

import pytest
import threading
from entities import Candidate
from repositories import InMemoryCandidateRepository


class TestInMemoryCandidateRepository:
    """Test cases for InMemoryCandidateRepository"""

    def test_repository_initialization(self, candidate_repository):
        """Test repository initialization"""
        assert candidate_repository is not None
        assert hasattr(candidate_repository, '_storage')
        assert hasattr(candidate_repository, '_lock')

    def test_save_candidate_valid(self, candidate_repository, sample_candidate):
        """Test saving a valid candidate"""
        candidate_repository.save(sample_candidate)

        assert sample_candidate.candidate_id in candidate_repository._storage
        assert candidate_repository._storage[sample_candidate.candidate_id] == sample_candidate

    def test_find_by_id_existing(self, candidate_repository, sample_candidate):
        """Test finding existing candidate by ID"""
        candidate_repository.save(sample_candidate)

        found_candidate = candidate_repository.find_by_id(sample_candidate.candidate_id)

        assert found_candidate is not None
        assert found_candidate == sample_candidate

    def test_find_all_empty(self, candidate_repository):
        """Test finding all candidates when repository is empty"""
        candidates = candidate_repository.find_all()
        assert isinstance(candidates, list)
        assert len(candidates) == 0

    def test_find_all_with_candidates(self, candidate_repository):
        """Test finding all candidates"""
        candidates = []
        for i in range(3):
            candidate = Candidate(f"candidate_{i}", f"Candidate {i}", f"Party {i}", f"Description {i}")
            candidates.append(candidate)
            candidate_repository.save(candidate)

        found_candidates = candidate_repository.find_all()
        assert len(found_candidates) == 3
        assert set(found_candidates) == set(candidates)

    def test_exists_by_id(self, candidate_repository, sample_candidate):
        """Test checking if candidate exists by ID"""
        assert not candidate_repository.exists_by_id(sample_candidate.candidate_id)

        candidate_repository.save(sample_candidate)
        assert candidate_repository.exists_by_id(sample_candidate.candidate_id)

    def test_delete_by_id(self, candidate_repository, sample_candidate):
        """Test deleting candidate by ID"""
        candidate_repository.save(sample_candidate)
        assert candidate_repository.exists_by_id(sample_candidate.candidate_id)

        result = candidate_repository.delete_by_id(sample_candidate.candidate_id)
        assert result is True
        assert not candidate_repository.exists_by_id(sample_candidate.candidate_id)

    def test_count(self, candidate_repository):
        """Test counting candidates"""
        assert candidate_repository.count() == 0

        for i in range(5):
            candidate = Candidate(f"candidate_{i}", f"Candidate {i}", "Party", "Description")
            candidate_repository.save(candidate)

        assert candidate_repository.count() == 5

    def test_find_by_party(self, candidate_repository):
        """Test finding candidates by party"""
        # Create candidates with different parties
        parties = ["Democratic", "Republican", "Independent"]
        candidates_by_party = {}

        for party in parties:
            candidates_by_party[party] = []
            for i in range(2):
                candidate = Candidate(f"candidate_{party}_{i}", f"Candidate {party} {i}",
                                    party, f"Description for {party}")
                candidates_by_party[party].append(candidate)
                candidate_repository.save(candidate)

        # Test finding by each party
        for party in parties:
            found_candidates = candidate_repository.find_by_party(party)
            assert len(found_candidates) == 2
            assert set(found_candidates) == set(candidates_by_party[party])

    def test_find_by_party_case_insensitive(self, candidate_repository):
        """Test party search is case insensitive"""
        candidate = Candidate("candidate_123", "John", "Democratic Party", "Description")
        candidate_repository.save(candidate)

        # Search with different cases
        found1 = candidate_repository.find_by_party("democratic party")
        found2 = candidate_repository.find_by_party("DEMOCRATIC PARTY")
        found3 = candidate_repository.find_by_party("Democratic Party")

        assert len(found1) == 1
        assert len(found2) == 1
        assert len(found3) == 1
        assert found1[0] == candidate
        assert found2[0] == candidate
        assert found3[0] == candidate

    def test_find_verified_candidates(self, candidate_repository):
        """Test finding verified candidates"""
        # Create verified and unverified candidates
        verified_candidate = Candidate("verified", "Verified", "Party", "Description")
        unverified_candidate = Candidate("unverified", "Unverified", "Party", "Description")

        verified_candidate.verify()
        candidate_repository.save(verified_candidate)
        candidate_repository.save(unverified_candidate)

        verified_candidates = candidate_repository.find_verified_candidates()
        assert len(verified_candidates) == 1
        assert verified_candidates[0] == verified_candidate

    def test_find_unverified_candidates(self, candidate_repository):
        """Test finding unverified candidates"""
        # Create verified and unverified candidates
        verified_candidate = Candidate("verified", "Verified", "Party", "Description")
        unverified_candidate = Candidate("unverified", "Unverified", "Party", "Description")

        verified_candidate.verify()
        candidate_repository.save(verified_candidate)
        candidate_repository.save(unverified_candidate)

        unverified_candidates = candidate_repository.find_unverified_candidates()
        assert len(unverified_candidates) == 1
        assert unverified_candidates[0] == unverified_candidate

    def test_find_candidates_by_verification_status(self, candidate_repository):
        """Test finding candidates by verification status"""
        verified = Candidate("v1", "Verified", "Party", "Desc")
        unverified = Candidate("v2", "Unverified", "Party", "Desc")

        verified.verify()
        candidate_repository.save(verified)
        candidate_repository.save(unverified)

        # Test verified
        verified_results = candidate_repository.find_candidates_by_verification_status(True)
        assert len(verified_results) == 1
        assert verified_results[0] == verified

        # Test unverified
        unverified_results = candidate_repository.find_candidates_by_verification_status(False)
        assert len(unverified_results) == 1
        assert unverified_results[0] == unverified

    def test_get_all_parties(self, candidate_repository):
        """Test getting all unique parties"""
        parties = ["Party A", "Party B", "Party C", "Party A"]  # Duplicate party

        for i, party in enumerate(parties):
            candidate = Candidate(f"candidate_{i}", f"Candidate {i}", party, "Description")
            candidate_repository.save(candidate)

        all_parties = candidate_repository.get_all_parties()
        assert len(all_parties) == 3  # Should be unique
        assert set(all_parties) == {"Party A", "Party B", "Party C"}

    def test_thread_safety_operations(self, candidate_repository):
        """Test thread safety of repository operations"""
        results = []
        errors = []

        def candidate_operation(operation_id):
            try:
                candidate = Candidate(f"candidate_{operation_id}", f"Candidate {operation_id}",
                                    f"Party {operation_id}", f"Description {operation_id}")
                candidate_repository.save(candidate)
                results.append(operation_id)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=candidate_operation, args=[i])
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        assert len(results) == 20
        assert len(errors) == 0
        assert candidate_repository.count() == 20

    def test_bulk_operations(self, candidate_repository):
        """Test bulk operations"""
        candidates = []
        for i in range(50):
            candidate = Candidate(f"candidate_{i}", f"Candidate {i}", "Party", "Description")
            candidates.append(candidate)
            candidate_repository.save(candidate)

        assert candidate_repository.count() == 50

        # Bulk delete
        for candidate in candidates:
            candidate_repository.delete_by_id(candidate.candidate_id)

        assert candidate_repository.count() == 0

    def test_verification_status_updates(self, candidate_repository):
        """Test verification status updates in repository"""
        candidate = Candidate("candidate_123", "John", "Party", "Description")
        candidate_repository.save(candidate)

        # Initially unverified
        unverified = candidate_repository.find_unverified_candidates()
        assert len(unverified) == 1

        # Verify candidate (this modifies the object in memory)
        candidate.verify()

        # Check repository queries reflect the change
        verified = candidate_repository.find_verified_candidates()
        unverified_after = candidate_repository.find_unverified_candidates()

        assert len(verified) == 1
        assert len(unverified_after) == 0

    def test_party_statistics(self, candidate_repository):
        """Test party-based statistics"""
        # Create candidates across different parties
        parties_data = {
            "Democratic": 5,
            "Republican": 3,
            "Independent": 2,
            "Green": 1
        }

        for party, count in parties_data.items():
            for i in range(count):
                candidate = Candidate(f"candidate_{party}_{i}", f"Candidate {i}", party, "Description")
                candidate_repository.save(candidate)

        # Verify counts by party
        for party, expected_count in parties_data.items():
            candidates = candidate_repository.find_by_party(party)
            assert len(candidates) == expected_count

    def test_candidate_search_and_filter(self, candidate_repository):
        """Test advanced search and filtering capabilities"""
        # Create diverse set of candidates
        candidates_data = [
            ("John Smith", "Democratic", "Education focus", True),
            ("Jane Doe", "Republican", "Economy focus", False),
            ("Bob Johnson", "Independent", "Environment focus", True),
            ("Alice Brown", "Green", "Healthcare focus", False),
            ("Charlie Wilson", "Democratic", "Infrastructure focus", True),
        ]

        candidates = []
        for i, (name, party, desc, verify) in enumerate(candidates_data):
            candidate = Candidate(f"candidate_{i}", name, party, desc)
            if verify:
                candidate.verify()
            candidates.append(candidate)
            candidate_repository.save(candidate)

        # Test various filters
        democrats = candidate_repository.find_by_party("Democratic")
        assert len(democrats) == 2

        verified_candidates = candidate_repository.find_verified_candidates()
        assert len(verified_candidates) == 3

        unverified_candidates = candidate_repository.find_unverified_candidates()
        assert len(unverified_candidates) == 2

        all_parties = candidate_repository.get_all_parties()
        assert len(all_parties) == 4

    def test_repository_isolation(self):
        """Test repository isolation"""
        repo1 = InMemoryCandidateRepository()
        repo2 = InMemoryCandidateRepository()

        candidate = Candidate("candidate_123", "Test", "Party", "Description")
        repo1.save(candidate)

        assert repo1.exists_by_id("candidate_123")
        assert not repo2.exists_by_id("candidate_123")

    def test_error_handling(self, candidate_repository):
        """Test error handling"""
        # Test with None values
        with pytest.raises(AttributeError):
            candidate_repository.save(None)

        with pytest.raises(TypeError):
            candidate_repository.find_by_id(None)

    def test_large_dataset_performance(self, candidate_repository):
        """Test performance with large datasets"""
        # Create many candidates
        for i in range(1000):
            candidate = Candidate(f"candidate_{i}", f"Candidate {i}", "Party", "Description")
            candidate_repository.save(candidate)

        assert candidate_repository.count() == 1000

        # Test queries still work
        all_candidates = candidate_repository.find_all()
        assert len(all_candidates) == 1000

        party_candidates = candidate_repository.find_by_party("Party")
        assert len(party_candidates) == 1000
