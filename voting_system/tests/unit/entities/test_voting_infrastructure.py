"""
Unit tests for Voting Infrastructure entities (VotingBooth, VotingMachine, VotingSystem).

Tests cover:
- Infrastructure creation and validation
- Booth and machine management
- System configuration
- Assignment and allocation logic
- Edge cases and error handling
"""

import pytest
from datetime import datetime
from entities import VotingBooth, VotingMachine, VotingSystem


class TestVotingBoothEntity:
    """Test cases for VotingBooth entity"""

    def test_voting_booth_creation_valid(self):
        """Test successful voting booth creation"""
        booth = VotingBooth("booth_123", "Downtown Center", 50)

        assert booth.booth_id == "booth_123"
        assert booth.location == "Downtown Center"
        assert booth.capacity == 50
        assert booth.occupancy == 0
        assert booth.assigned_machine_ids == []
        assert booth.is_active == True

    def test_voting_booth_creation_invalid_id(self):
        """Test voting booth creation with invalid ID"""
        with pytest.raises(ValueError, match="Invalid booth ID"):
            VotingBooth("", "Location", 50)

        with pytest.raises(ValueError, match="Invalid booth ID"):
            VotingBooth("   ", "Location", 50)

    def test_voting_booth_creation_invalid_location(self):
        """Test voting booth creation with invalid location"""
        with pytest.raises(ValueError, match="Invalid location"):
            VotingBooth("booth_123", "", 50)

        with pytest.raises(ValueError, match="Invalid location"):
            VotingBooth("booth_123", "   ", 50)

    def test_voting_booth_creation_invalid_capacity(self):
        """Test voting booth creation with invalid capacity"""
        with pytest.raises(ValueError, match="Invalid capacity"):
            VotingBooth("booth_123", "Location", 0)

        with pytest.raises(ValueError, match="Invalid capacity"):
            VotingBooth("booth_123", "Location", -5)

        with pytest.raises(ValueError, match="Invalid capacity"):
            VotingBooth("booth_123", "Location", 1001)  # Over 1000

    def test_voting_booth_machine_assignment(self):
        """Test voting booth machine assignment"""
        booth = VotingBooth("booth_123", "Location", 50)

        # Assign machine
        booth.assign_machine("machine_1")
        assert "machine_1" in booth.assigned_machine_ids
        assert len(booth.assigned_machine_ids) == 1

        # Assign another machine
        booth.assign_machine("machine_2")
        assert len(booth.assigned_machine_ids) == 2

        # Unassign machine
        booth.unassign_machine("machine_1")
        assert "machine_1" not in booth.assigned_machine_ids
        assert len(booth.assigned_machine_ids) == 1

    def test_voting_booth_machine_assignment_invalid(self):
        """Test invalid machine assignment"""
        booth = VotingBooth("booth_123", "Location", 50)

        # Invalid machine ID
        with pytest.raises(ValueError, match="Invalid machine ID"):
            booth.assign_machine("")

        with pytest.raises(ValueError, match="Invalid machine ID"):
            booth.assign_machine("   ")

        # Unassign non-existent machine
        with pytest.raises(ValueError, match="Machine not assigned to this booth"):
            booth.unassign_machine("non_existent")

        # Assign duplicate machine
        booth.assign_machine("machine_1")
        with pytest.raises(ValueError, match="Machine already assigned to this booth"):
            booth.assign_machine("machine_1")

    def test_voting_booth_occupancy_management(self):
        """Test voting booth occupancy management"""
        booth = VotingBooth("booth_123", "Location", 50)

        # Increase occupancy
        booth.increase_occupancy()
        assert booth.occupancy == 1

        booth.increase_occupancy()
        assert booth.occupancy == 2

        # Decrease occupancy
        booth.decrease_occupancy()
        assert booth.occupancy == 1

        # Cannot go below 0
        booth.occupancy = 0
        booth.decrease_occupancy()
        assert booth.occupancy == 0

    def test_voting_booth_occupancy_limits(self):
        """Test voting booth occupancy limits"""
        booth = VotingBooth("booth_123", "Location", 2)

        # Fill to capacity
        booth.increase_occupancy()
        booth.increase_occupancy()
        assert booth.occupancy == 2
        assert booth.is_full()

        # Cannot exceed capacity
        booth.increase_occupancy()
        assert booth.occupancy == 2  # Should not exceed capacity

    def test_voting_booth_activation(self):
        """Test voting booth activation/deactivation"""
        booth = VotingBooth("booth_123", "Location", 50)
        assert booth.is_active == True

        # Deactivate
        booth.deactivate()
        assert booth.is_active == False

        # Reactivate
        booth.activate()
        assert booth.is_active == True

    def test_voting_booth_string_representation(self):
        """Test voting booth string representation"""
        booth = VotingBooth("booth_123", "Downtown Center", 50)
        expected = f"VotingBooth(id={booth.booth_id}, location={booth.location}, occupancy={booth.occupancy}/{booth.capacity})"
        assert str(booth) == expected

    def test_voting_booth_equality(self):
        """Test voting booth equality"""
        booth1 = VotingBooth("booth_123", "Location", 50)
        booth2 = VotingBooth("booth_123", "Location", 50)
        booth3 = VotingBooth("booth_456", "Different Location", 30)

        assert booth1 == booth2
        assert booth1 != booth3


class TestVotingMachineEntity:
    """Test cases for VotingMachine entity"""

    def test_voting_machine_creation_valid(self):
        """Test successful voting machine creation"""
        machine = VotingMachine("machine_123", "TouchScreen-2024")

        assert machine.machine_id == "machine_123"
        assert machine.model == "TouchScreen-2024"
        assert machine.is_active == True
        assert machine.assigned_booth_id is None
        assert machine.created_at is not None

    def test_voting_machine_creation_invalid_id(self):
        """Test voting machine creation with invalid ID"""
        with pytest.raises(ValueError, match="Invalid machine ID"):
            VotingMachine("", "Model")

        with pytest.raises(ValueError, match="Invalid machine ID"):
            VotingMachine("   ", "Model")

    def test_voting_machine_creation_invalid_model(self):
        """Test voting machine creation with invalid model"""
        with pytest.raises(ValueError, match="Invalid model"):
            VotingMachine("machine_123", "")

        with pytest.raises(ValueError, match="Invalid model"):
            VotingMachine("machine_123", "   ")

    def test_voting_machine_booth_assignment(self):
        """Test voting machine booth assignment"""
        machine = VotingMachine("machine_123", "Model")

        # Assign to booth
        machine.assign_to_booth("booth_123")
        assert machine.assigned_booth_id == "booth_123"

        # Unassign from booth
        machine.unassign_from_booth()
        assert machine.assigned_booth_id is None

    def test_voting_machine_assignment_invalid(self):
        """Test invalid booth assignment"""
        machine = VotingMachine("machine_123", "Model")

        # Invalid booth ID
        with pytest.raises(ValueError, match="Invalid booth ID"):
            machine.assign_to_booth("")

        with pytest.raises(ValueError, match="Invalid booth ID"):
            machine.assign_to_booth("   ")

    def test_voting_machine_activation(self):
        """Test voting machine activation/deactivation"""
        machine = VotingMachine("machine_123", "Model")
        assert machine.is_active == True

        # Deactivate
        machine.deactivate()
        assert machine.is_active == False

        # Reactivate
        machine.activate()
        assert machine.is_active == True

    def test_voting_machine_string_representation(self):
        """Test voting machine string representation"""
        machine = VotingMachine("machine_123", "TouchScreen-2024")
        expected = f"VotingMachine(id={machine.machine_id}, model={machine.model}, active={machine.is_active})"
        assert str(machine) == expected

    def test_voting_machine_equality(self):
        """Test voting machine equality"""
        machine1 = VotingMachine("machine_123", "Model")
        machine2 = VotingMachine("machine_123", "Model")
        machine3 = VotingMachine("machine_456", "Different Model")

        assert machine1 == machine2
        assert machine1 != machine3


class TestVotingSystemEntity:
    """Test cases for VotingSystem entity"""

    def test_voting_system_creation_valid(self):
        """Test successful voting system creation"""
        system = VotingSystem("system_123", "National Election System")

        assert system.system_id == "system_123"
        assert system.name == "National Election System"
        assert system.is_active == True
        assert system.created_at is not None
        assert system.total_users == 0
        assert system.total_elections == 0
        assert system.total_votes == 0

    def test_voting_system_creation_invalid_id(self):
        """Test voting system creation with invalid ID"""
        with pytest.raises(ValueError, match="Invalid system ID"):
            VotingSystem("", "Name")

        with pytest.raises(ValueError, match="Invalid system ID"):
            VotingSystem("   ", "Name")

    def test_voting_system_creation_invalid_name(self):
        """Test voting system creation with invalid name"""
        with pytest.raises(ValueError, match="Invalid name"):
            VotingSystem("system_123", "")

        with pytest.raises(ValueError, match="Invalid name"):
            VotingSystem("system_123", "   ")

    def test_voting_system_statistics_update(self):
        """Test voting system statistics updates"""
        system = VotingSystem("system_123", "Name")

        # Update statistics
        system.update_statistics(users=100, elections=5, votes=1000)
        assert system.total_users == 100
        assert system.total_elections == 5
        assert system.total_votes == 1000

        # Update again
        system.update_statistics(users=50, elections=2, votes=500)
        assert system.total_users == 150
        assert system.total_elections == 7
        assert system.total_votes == 1500

    def test_voting_system_activation(self):
        """Test voting system activation/deactivation"""
        system = VotingSystem("system_123", "Name")
        assert system.is_active == True

        # Deactivate
        system.deactivate()
        assert system.is_active == False

        # Reactivate
        system.activate()
        assert system.is_active == True

    def test_voting_system_string_representation(self):
        """Test voting system string representation"""
        system = VotingSystem("system_123", "National Election System")
        expected = f"VotingSystem(id={system.system_id}, name={system.name}, active={system.is_active})"
        assert str(system) == expected

    def test_voting_system_equality(self):
        """Test voting system equality"""
        system1 = VotingSystem("system_123", "Name")
        system2 = VotingSystem("system_123", "Name")
        system3 = VotingSystem("system_456", "Different Name")

        assert system1 == system2
        assert system1 != system3


class TestInfrastructureIntegration:
    """Test integration between infrastructure entities"""

    def test_booth_machine_integration(self):
        """Test integration between booth and machine assignment"""
        booth = VotingBooth("booth_123", "Location", 50)
        machine = VotingMachine("machine_123", "Model")

        # Assign machine to booth
        booth.assign_machine(machine.machine_id)
        machine.assign_to_booth(booth.booth_id)

        assert machine.machine_id in booth.assigned_machine_ids
        assert machine.assigned_booth_id == booth.booth_id

        # Unassign
        booth.unassign_machine(machine.machine_id)
        machine.unassign_from_booth()

        assert machine.machine_id not in booth.assigned_machine_ids
        assert machine.assigned_booth_id is None

    def test_multiple_machines_per_booth(self):
        """Test multiple machines assigned to one booth"""
        booth = VotingBooth("booth_123", "Location", 50)
        machines = []

        # Create and assign multiple machines
        for i in range(5):
            machine = VotingMachine(f"machine_{i}", f"Model_{i}")
            machines.append(machine)
            booth.assign_machine(machine.machine_id)
            machine.assign_to_booth(booth.booth_id)

        assert len(booth.assigned_machine_ids) == 5
        for machine in machines:
            assert machine.assigned_booth_id == booth.booth_id
            assert machine.machine_id in booth.assigned_machine_ids

    def test_system_infrastructure_tracking(self):
        """Test system tracking of infrastructure"""
        system = VotingSystem("system_123", "Name")

        # Add infrastructure components
        booths = [VotingBooth(f"booth_{i}", f"Location_{i}", 50) for i in range(3)]
        machines = [VotingMachine(f"machine_{i}", "Model") for i in range(5)]

        # Update system statistics
        system.update_statistics(
            users=100,
            elections=5,
            votes=1000
        )

        assert system.total_users == 100
        assert system.total_elections == 5
        assert system.total_votes == 1000

    def test_infrastructure_capacity_planning(self):
        """Test capacity planning for infrastructure"""
        # Create booths with different capacities
        small_booth = VotingBooth("small", "Location", 10)
        medium_booth = VotingBooth("medium", "Location", 50)
        large_booth = VotingBooth("large", "Location", 100)

        # Test capacity limits
        assert not small_booth.is_full()
        assert not medium_booth.is_full()
        assert not large_booth.is_full()

        # Fill booths to capacity
        for _ in range(10):
            small_booth.increase_occupancy()
        for _ in range(50):
            medium_booth.increase_occupancy()
        for _ in range(100):
            large_booth.increase_occupancy()

        assert small_booth.is_full()
        assert medium_booth.is_full()
        assert large_booth.is_full()

    def test_infrastructure_status_management(self):
        """Test status management across infrastructure"""
        booth = VotingBooth("booth_123", "Location", 50)
        machine = VotingMachine("machine_123", "Model")
        system = VotingSystem("system_123", "Name")

        # All should start active
        assert booth.is_active == True
        assert machine.is_active == True
        assert system.is_active == True

        # Deactivate all
        booth.deactivate()
        machine.deactivate()
        system.deactivate()

        assert booth.is_active == False
        assert machine.is_active == False
        assert system.is_active == False

        # Reactivate all
        booth.activate()
        machine.activate()
        system.activate()

        assert booth.is_active == True
        assert machine.is_active == True
        assert system.is_active == True
