"""
Unit tests for Candidate entity.

Tests cover:
- Candidate creation and validation
- Property access and modification
- Verification status management
- Business logic validation
- Edge cases and error handling
"""

import pytest
from datetime import datetime
from entities import Candidate


class TestCandidateEntity:
    """Test cases for Candidate entity"""

    def test_candidate_creation_valid_data(self, sample_candidate_data):
        """Test successful candidate creation with valid data"""
        candidate = Candidate(**sample_candidate_data)

        assert candidate.candidate_id == sample_candidate_data["candidate_id"]
        assert candidate.name == sample_candidate_data["name"]
        assert candidate.party == sample_candidate_data["party"]
        assert candidate.description == sample_candidate_data["description"]
        assert candidate.verified == False  # Default should be False
        assert candidate.created_at is not None
        assert candidate.updated_at is not None

    def test_candidate_creation_invalid_candidate_id(self):
        """Test candidate creation with invalid candidate ID"""
        with pytest.raises(ValueError, match="Invalid candidate ID"):
            Candidate("", "John Doe", "Democratic", "Good candidate")

        with pytest.raises(ValueError, match="Invalid candidate ID"):
            Candidate("   ", "John Doe", "Democratic", "Good candidate")

    def test_candidate_creation_invalid_name(self):
        """Test candidate creation with invalid name"""
        with pytest.raises(ValueError, match="Invalid name"):
            Candidate("candidate_123", "", "Democratic", "Good candidate")

        with pytest.raises(ValueError, match="Invalid name"):
            Candidate("candidate_123", "   ", "Democratic", "Good candidate")

        with pytest.raises(ValueError, match="Invalid name"):
            Candidate("candidate_123", "John123", "Democratic", "Good candidate")

    def test_candidate_creation_invalid_party(self):
        """Test candidate creation with invalid party"""
        with pytest.raises(ValueError, match="Invalid party"):
            Candidate("candidate_123", "John Doe", "", "Good candidate")

        with pytest.raises(ValueError, match="Invalid party"):
            Candidate("candidate_123", "John Doe", "   ", "Good candidate")

    def test_candidate_creation_invalid_description(self):
        """Test candidate creation with invalid description"""
        with pytest.raises(ValueError, match="Invalid description"):
            Candidate("candidate_123", "John Doe", "Democratic", "")

        with pytest.raises(ValueError, match="Invalid description"):
            Candidate("candidate_123", "John Doe", "Democratic", "   ")

    def test_candidate_property_access(self, sample_candidate):
        """Test candidate property access"""
        assert sample_candidate.candidate_id == "candidate_123"
        assert sample_candidate.name == "Jane Smith"
        assert sample_candidate.party == "Democratic Party"
        assert sample_candidate.description == "Experienced leader with focus on education"
        assert sample_candidate.verified == False

    def test_candidate_verification(self, sample_candidate):
        """Test candidate verification process"""
        assert sample_candidate.verified == False

        # Verify candidate
        sample_candidate.verify()
        assert sample_candidate.verified == True
        assert sample_candidate.updated_at > sample_candidate.created_at

        # Unverify candidate
        sample_candidate.unverify()
        assert sample_candidate.verified == False

    def test_candidate_string_representation(self, sample_candidate):
        """Test candidate string representation"""
        expected = f"Candidate(id={sample_candidate.candidate_id}, name={sample_candidate.name}, party={sample_candidate.party}, verified={sample_candidate.verified})"
        assert str(sample_candidate) == expected
        assert repr(sample_candidate) == expected

    def test_candidate_equality(self, sample_candidate_data):
        """Test candidate equality comparison"""
        candidate1 = Candidate(**sample_candidate_data)
        candidate2 = Candidate(**sample_candidate_data)
        candidate3 = Candidate("different_id", "Different Name", "Different Party", "Different desc")

        assert candidate1 == candidate2
        assert candidate1 != candidate3
        assert candidate1 != "not_a_candidate"

    def test_candidate_hash(self, sample_candidate_data):
        """Test candidate hash function"""
        candidate1 = Candidate(**sample_candidate_data)
        candidate2 = Candidate(**sample_candidate_data)

        assert hash(candidate1) == hash(candidate2)
        assert hash(candidate1) == hash(sample_candidate_data["candidate_id"])

    def test_candidate_update_description(self, sample_candidate):
        """Test updating candidate description"""
        original_updated = sample_candidate.updated_at
        new_description = "Updated description with new achievements"

        sample_candidate.update_description(new_description)

        assert sample_candidate.description == new_description
        assert sample_candidate.updated_at > original_updated

    def test_candidate_update_party(self, sample_candidate):
        """Test updating candidate party"""
        original_updated = sample_candidate.updated_at
        new_party = "Independent"

        sample_candidate.update_party(new_party)

        assert sample_candidate.party == new_party
        assert sample_candidate.updated_at > original_updated

    def test_candidate_update_party_invalid(self, sample_candidate):
        """Test updating candidate party with invalid data"""
        with pytest.raises(ValueError, match="Invalid party"):
            sample_candidate.update_party("")

        with pytest.raises(ValueError, match="Invalid party"):
            sample_candidate.update_party("   ")

    def test_candidate_update_description_invalid(self, sample_candidate):
        """Test updating candidate description with invalid data"""
        with pytest.raises(ValueError, match="Invalid description"):
            sample_candidate.update_description("")

        with pytest.raises(ValueError, match="Invalid description"):
            sample_candidate.update_description("   ")

    def test_candidate_verification_affects_string_repr(self, sample_candidate):
        """Test that verification status affects string representation"""
        unverified_str = str(sample_candidate)
        assert "verified=False" in unverified_str

        sample_candidate.verify()
        verified_str = str(sample_candidate)
        assert "verified=True" in verified_str

    def test_candidate_party_normalization(self):
        """Test candidate party handling with various formats"""
        # Test with extra spaces
        candidate = Candidate("c1", "Test", "  Democratic Party  ", "Description")
        assert candidate.party == "  Democratic Party  "  # Should preserve original format

        # Test with special characters
        candidate = Candidate("c2", "Test", "People's Party", "Description")
        assert candidate.party == "People's Party"

    def test_candidate_description_length(self):
        """Test candidate description with various lengths"""
        # Short description
        candidate = Candidate("c1", "Test", "Party", "Short")
        assert candidate.description == "Short"

        # Long description
        long_desc = "A" * 1000
        candidate = Candidate("c2", "Test", "Party", long_desc)
        assert candidate.description == long_desc

    def test_candidate_timestamps_consistency(self, sample_candidate):
        """Test that timestamps are consistent across operations"""
        initial_created = sample_candidate.created_at
        initial_updated = sample_candidate.updated_at

        # Multiple operations should maintain created_at
        sample_candidate.verify()
        assert sample_candidate.created_at == initial_created
        assert sample_candidate.updated_at > initial_updated

        updated_after_verify = sample_candidate.updated_at

        sample_candidate.update_description("New description")
        assert sample_candidate.created_at == initial_created
        assert sample_candidate.updated_at > updated_after_verify

    def test_candidate_multiple_verification_calls(self, sample_candidate):
        """Test multiple verification calls"""
        # Multiple verify calls should not change state
        sample_candidate.verify()
        assert sample_candidate.verified == True

        original_updated = sample_candidate.updated_at
        sample_candidate.verify()  # Second call
        assert sample_candidate.verified == True
        assert sample_candidate.updated_at == original_updated  # Should not update timestamp

    def test_candidate_verification_toggle(self, sample_candidate):
        """Test verification status toggling"""
        # Start unverified
        assert sample_candidate.verified == False

        # Verify
        sample_candidate.verify()
        assert sample_candidate.verified == True

        # Unverify
        sample_candidate.unverify()
        assert sample_candidate.verified == False

        # Verify again
        sample_candidate.verify()
        assert sample_candidate.verified == True
