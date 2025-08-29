"""
Voting System Demo Application

This module provides a comprehensive demonstration of the voting system
functionality including all major use cases and features.
"""

import time
import threading
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from orchestrator import VotingSystemOrchestrator
from concurrency_utils import initialize_concurrency_system, get_concurrency_manager
from design_patterns import VotingSystemInitializer


class VotingSystemDemo:
    """Demo application for the voting system"""

    def __init__(self):
        """Initialize the demo"""
        print("🚀 Initializing Voting System Demo...")
        print("=" * 50)

        # Initialize the system
        self.orchestrator = VotingSystemOrchestrator()
        self.orchestrator.initialize_system("Demo Voting System")

        # Initialize concurrency system
        self.concurrency_manager = initialize_concurrency_system(num_workers=4, rate_limit=20.0)

        # Demo data
        self.users = []
        self.candidates = []
        self.elections = []

        print("✅ System initialized successfully!")
        print()

    def run_full_demo(self) -> None:
        """Run the complete system demonstration"""
        print("🎯 Starting Complete Voting System Demo")
        print("=" * 50)

        try:
            # Phase 1: Setup
            self._setup_phase()

            # Phase 2: User and Candidate Registration
            self._registration_phase()

            # Phase 3: Election Creation
            self._election_creation_phase()

            # Phase 4: Voting Phase
            self._voting_phase()

            # Phase 5: Results and Analysis
            self._results_phase()

            # Phase 6: Concurrent Operations Demo
            self._concurrency_demo()

            # Phase 7: System Statistics
            self._statistics_demo()

            print("\n🎉 Demo completed successfully!")
            print("The voting system is fully operational with all features working!")

        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self._cleanup()

    def _setup_phase(self) -> None:
        """Demonstrate system setup and infrastructure"""
        print("\n📋 Phase 1: System Setup and Infrastructure")
        print("-" * 40)

        # Create voting booths
        print("Creating voting booths...")
        booth1 = self.orchestrator.create_voting_booth("Downtown Center", 50)
        booth2 = self.orchestrator.create_voting_booth("City Hall", 30)
        booth3 = self.orchestrator.create_voting_booth("Community Center", 40)

        print(f"✅ Created booth: {booth1}")
        print(f"✅ Created booth: {booth2}")
        print(f"✅ Created booth: {booth3}")

        # Create voting machines
        print("\nCreating voting machines...")
        machine1 = self.orchestrator.create_voting_machine(booth1.booth_id, "TouchScreen-2024")
        machine2 = self.orchestrator.create_voting_machine(booth1.booth_id, "TouchScreen-2024")
        machine3 = self.orchestrator.create_voting_machine(booth2.booth_id, "SmartVote-2024")

        print(f"✅ Created machine: {machine1}")
        print(f"   📍 Assigned to booth: {booth1.location} ({booth1.booth_id})")
        print(f"✅ Created machine: {machine2}")
        print(f"   📍 Assigned to booth: {booth1.location} ({booth1.booth_id})")
        print(f"✅ Created machine: {machine3}")
        print(f"   📍 Assigned to booth: {booth2.location} ({booth2.booth_id})")

        # Show booth assignments summary
        print("\n📊 Booth Assignments Summary:")
        print(f"   {booth1.location}: {len(booth1.assigned_machine_ids)} machines")
        print(f"   {booth2.location}: {len(booth2.assigned_machine_ids)} machines")
        print(f"   {booth3.location}: {len(booth3.assigned_machine_ids)} machines")

        # Show available booths
        available_booths = self.orchestrator.get_available_booths()
        print(f"\n📊 Available booths: {len(available_booths)}")

    def _registration_phase(self) -> None:
        """Demonstrate user and candidate registration"""
        print("\n👥 Phase 2: User and Candidate Registration")
        print("-" * 45)

        # Register users
        print("Registering users...")
        user_data = [
            ("Alice Johnson", "alice@email.com", 28),
            ("Bob Smith", "bob@email.com", 35),
            ("Charlie Brown", "charlie@email.com", 42),
            ("Diana Prince", "diana@email.com", 31),
            ("Edward Norton", "edward@email.com", 29),
            ("Fiona Green", "fiona@email.com", 38),
            ("George Lucas", "george@email.com", 45),
            ("Helen Troy", "helen@email.com", 33)
        ]

        for name, email, age in user_data:
            user = self.orchestrator.register_user(name, email, age)
            self.users.append(user)
            print(f"✅ Registered: {user}")

        # Register candidates
        print("\nRegistering candidates...")
        candidate_data = [
            ("Mayor Martinez", "Progressive Party", "Experienced leader focused on community development"),
            ("Councilor Davis", "Conservative Alliance", "Fiscal responsibility and public safety advocate"),
            ("Dr. Rodriguez", "Green Future", "Environmental sustainability and renewable energy expert"),
            ("Ms. Thompson", "Independent", "Grassroots community organizer with fresh perspectives")
        ]

        for name, party, description in candidate_data:
            candidate = self.orchestrator.register_candidate(name, party, description)
            self.candidates.append(candidate)
            print(f"✅ Registered: {candidate}")

            # Debug: Verify candidate was saved
            retrieved = self.orchestrator.get_candidate(candidate.candidate_id)
            if retrieved:
                print(f"   ✅ Verified: {retrieved.candidate_id}")
            else:
                print(f"   ❌ Not found: {candidate.candidate_id}")

        print(f"\n📊 Total users: {len(self.users)}")
        print(f"📊 Total candidates: {len(self.candidates)}")

    def _election_creation_phase(self) -> None:
        """Demonstrate election creation and management"""
        print("\n🗳️  Phase 3: Election Creation and Management")
        print("-" * 43)

        # Create main election
        print("Creating presidential election...")
        # Start election immediately and end in 1 hour for demo purposes
        start_date = datetime.now() - timedelta(minutes=1)  # Started 1 minute ago
        end_date = start_date + timedelta(hours=1)  # Ends in 1 hour

        candidate_ids = [c.candidate_id for c in self.candidates]

        election = self.orchestrator.create_election(
            title="City Mayor Election 2024",
            description="Election for the next City Mayor - Choose wisely!",
            start_date=start_date,
            end_date=end_date,
            candidate_ids=candidate_ids
        )

        self.elections.append(election)
        print(f"✅ Created election: {election}")
        print(f"   📅 Start: {election.start_date}")
        print(f"   📅 End: {election.end_date}")
        print(f"   👥 Candidates: {len(election.candidates)}")

        # Start the election (should work now since start_date is in the past)
        print("\nStarting election...")
        success = self.orchestrator.start_election(election.election_id)
        if success:
            print("✅ Election started successfully!")
        else:
            print("❌ Failed to start election")

        # Show election candidates
        print("\nElection candidates:")
        election_candidates = self.orchestrator.get_election_candidates(election.election_id)
        for i, candidate in enumerate(election_candidates, 1):
            print(f"  {i}. {candidate.name} ({candidate.party})")

    def _voting_phase(self) -> None:
        """Demonstrate the voting process"""
        print("\n🗳️  Phase 4: Voting Phase")
        print("-" * 20)

        if not self.elections:
            print("❌ No active elections found")
            return

        election = self.elections[0]
        print(f"Voting in election: {election.title}")

        # Simulate voting process
        votes_cast = 0
        eligible_users = [u for u in self.users if u.status.name == "ACTIVE"]

        print(f"\nEligible voters: {len(eligible_users)}")

        for i, user in enumerate(eligible_users, 1):
            # Randomly select a candidate
            candidate = random.choice(self.candidates)

            try:
                vote = self.orchestrator.cast_vote(
                    user_id=user.user_id,
                    election_id=election.election_id,
                    candidate_id=candidate.candidate_id
                )

                print(f"✅ Vote {i}: {user.name} voted for {candidate.name}")
                votes_cast += 1

                # Add small delay to simulate real voting
                time.sleep(0.1)

            except Exception as e:
                print(f"❌ Vote {i}: {user.name} - {str(e)}")

        print(f"\n📊 Total votes cast: {votes_cast}")

        # Show current vote counts
        print("\nCurrent vote counts:")
        for candidate in self.candidates:
            vote_count = self.orchestrator._vote_manager.count_votes_for_candidate_in_election(
                candidate.candidate_id, election.election_id
            )
            print(f"  {candidate.name}: {vote_count} votes")

    def _results_phase(self) -> None:
        """Demonstrate results calculation and display"""
        print("\n📊 Phase 5: Results and Analysis")
        print("-" * 30)

        if not self.elections:
            print("❌ No elections found")
            return

        election = self.elections[0]

        # End the election
        print("Ending election...")
        print(f"Debug: Election ID: {election.election_id}")
        print(f"Debug: Election status before ending: {election.status}")

        try:
            success = self.orchestrator.end_election(election.election_id)
            print(f"Debug: end_election returned: {success}")
            if success:
                print("✅ Election ended successfully!")
            else:
                print("❌ Failed to end election")
        except Exception as e:
            print(f"❌ Error ending election: {e}")
            import traceback
            traceback.print_exc()
            return

        # Calculate and display results
        print("\nCalculating final results...")
        results = self.orchestrator.calculate_election_results(election.election_id)

        if results:
            print("\n📈 FINAL RESULTS:")
            print("=" * 30)
            print(f"Total votes: {results.total_votes}")
            print(f"Voting percentage: {results.voting_percentage}%")

            print("\nCandidate breakdown:")
            for candidate_id, votes in results.candidate_votes.items():
                candidate = next((c for c in self.candidates if c.candidate_id == candidate_id), None)
                candidate_name = candidate.name if candidate else "Unknown"
                percentage = (votes / results.total_votes * 100) if results.total_votes > 0 else 0
                print(f"  {candidate_name}: {votes} votes ({percentage:.1f}%)")

            if results.winner_candidate_id:
                winner = next((c for c in self.candidates if c.candidate_id == results.winner_candidate_id), None)
                winner_name = winner.name if winner else "Unknown"
                print(f"\n🏆 WINNER: {winner_name}")
            else:
                print("\n🤝 No clear winner (tie)")
        else:
            print("❌ No results available")

    def _concurrency_demo(self) -> None:
        """Demonstrate concurrent operations"""
        print("\n⚡ Phase 6: Concurrency Demonstration")
        print("-" * 35)

        print("Testing concurrent voting operations...")

        # Create test users and candidates for concurrency test
        test_users = []
        for i in range(10):
            user = self.orchestrator.register_user(
                f"TestUser{i+1}",
                f"test{i+1}@email.com",
                25 + i
            )
            test_users.append(user)

        # Create a quick election for testing
        test_candidates = []
        for i in range(3):
            candidate = self.orchestrator.register_candidate(
                f"TestCandidate{i+1}",
                f"TestParty{i+1}",
                f"Test candidate {i+1}"
            )
            test_candidates.append(candidate)

        test_election = self.orchestrator.create_election(
            title="Concurrency Test Election",
            description="Testing concurrent voting",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=1),
            candidate_ids=[c.candidate_id for c in test_candidates]
        )

        self.orchestrator.start_election(test_election.election_id)

        # Simulate concurrent voting
        def concurrent_vote(user, election_id, candidates):
            """Function for concurrent voting"""
            try:
                candidate = random.choice(candidates)
                vote = self.orchestrator.cast_vote(
                    user_id=user.user_id,
                    election_id=election_id,
                    candidate_id=candidate.candidate_id
                )
                return f"✅ {user.name} voted"
            except Exception as e:
                return f"❌ {user.name} failed: {str(e)}"

        # Submit concurrent operations
        print("Submitting concurrent voting operations...")
        for user in test_users:
            self.concurrency_manager.submit_operation(
                concurrent_vote,
                args=(user, test_election.election_id, test_candidates),
                priority=2
            )

        # Wait a bit for operations to complete
        time.sleep(2)

        # Check results
        final_results = self.orchestrator.calculate_election_results(test_election.election_id)
        if final_results:
            print(f"\nConcurrent voting results: {final_results.total_votes} votes cast")

        print("✅ Concurrency test completed!")

    def _statistics_demo(self) -> None:
        """Demonstrate system statistics and reporting"""
        print("\n📈 Phase 7: System Statistics and Reporting")
        print("-" * 40)

        # Get system statistics
        stats = self.orchestrator.get_system_statistics()
        print("📊 System Statistics:")
        print(f"   Total Systems: {stats.get('total_systems', 0)}")
        print(f"   Active Systems: {stats.get('active_systems', 0)}")
        print(f"   Total Elections: {stats.get('total_elections', 0)}")
        print(f"   Total Users: {stats.get('total_users', 0)}")
        print(f"   Total Votes: {stats.get('total_votes', 0)}")

        # Get system health
        health = self.orchestrator.get_system_health()
        print("\n🏥 System Health:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Active Elections: {health.get('active_elections', 0)}")
        print(f"   Timestamp: {health.get('timestamp', 'unknown')}")

        # Get concurrency status
        concurrency_status = self.concurrency_manager.get_system_status()
        print("\n⚡ Concurrency Status:")
        print(f"   Active: {concurrency_status.get('active', False)}")
        print(f"   Queue Size: {concurrency_status.get('queue_size', 0)}")
        print(f"   Workers: {concurrency_status.get('num_workers', 0)}")
        print(f"   Rate Limiter Tokens: {concurrency_status.get('rate_limiter_tokens', 0):.1f}")

        # Export election data (if we have elections)
        if self.elections:
            print("\n💾 Exporting election data...")
            export_data = self.orchestrator.export_election_data(self.elections[0].election_id)
            if export_data:
                print("✅ Election data exported successfully")
                print(f"   Election: {export_data['election']['title']}")
                print(f"   Total Votes: {len(export_data['votes'])}")
                print(f"   Candidates: {len(export_data['candidates'])}")
            else:
                print("❌ Failed to export election data")

    def _cleanup(self) -> None:
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")

        # Stop concurrency system
        if hasattr(self, 'concurrency_manager'):
            self.concurrency_manager.stop()

        # Clear event history
        self.orchestrator.clear_event_history()

        print("✅ Cleanup completed!")

    def run_interactive_demo(self) -> None:
        """Run an interactive demo with user input"""
        print("🎮 Interactive Voting System Demo")
        print("=" * 35)
        print("This demo allows you to interact with the voting system directly.")
        print("Commands:")
        print("  register_user <name> <email> <age>")
        print("  register_candidate <name> <party> <description>")
        print("  create_election <title> <description> <duration_hours>")
        print("  vote <user_email> <election_id> <candidate_name>")
        print("  show_results <election_id>")
        print("  show_stats")
        print("  quit")
        print()

        while True:
            try:
                command = input("Enter command: ").strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()

                if cmd == "quit":
                    break
                elif cmd == "register_user" and len(parts) >= 4:
                    name = " ".join(parts[1:-2])
                    email = parts[-2]
                    age = int(parts[-1])
                    user = self.orchestrator.register_user(name, email, age)
                    print(f"✅ User registered: {user}")
                elif cmd == "register_candidate" and len(parts) >= 4:
                    name = " ".join(parts[1:-2])
                    party = parts[-2]
                    description = " ".join(parts[-1:])
                    candidate = self.orchestrator.register_candidate(name, party, description)
                    print(f"✅ Candidate registered: {candidate}")
                elif cmd == "create_election" and len(parts) >= 4:
                    title = " ".join(parts[1:-2])
                    description = parts[-2]
                    duration_hours = int(parts[-1])
                    start_date = datetime.now() + timedelta(minutes=1)
                    end_date = start_date + timedelta(hours=duration_hours)

                    # Get all candidate IDs
                    candidate_ids = [c.candidate_id for c in self.orchestrator.get_all_candidates()]

                    election = self.orchestrator.create_election(
                        title, description, start_date, end_date, candidate_ids
                    )
                    self.orchestrator.start_election(election.election_id)
                    print(f"✅ Election created and started: {election}")
                elif cmd == "vote" and len(parts) >= 4:
                    user_email = parts[1]
                    election_id = parts[2]
                    candidate_name = " ".join(parts[3:])

                    # Find user by email
                    user = None
                    for u in self.orchestrator.get_all_users():
                        if u.email == user_email:
                            user = u
                            break

                    if not user:
                        print(f"❌ User with email {user_email} not found")
                        continue

                    # Find candidate by name
                    candidate = None
                    for c in self.orchestrator.get_all_candidates():
                        if c.name == candidate_name:
                            candidate = c
                            break

                    if not candidate:
                        print(f"❌ Candidate {candidate_name} not found")
                        continue

                    vote = self.orchestrator.cast_vote(user.user_id, election_id, candidate.candidate_id)
                    print(f"✅ Vote cast: {vote}")
                elif cmd == "show_results" and len(parts) >= 2:
                    election_id = parts[1]
                    results = self.orchestrator.get_election_results(election_id)
                    if results:
                        print(f"📊 Results for election {election_id}:")
                        for candidate_id, votes in results.candidate_votes.items():
                            candidate = next((c for c in self.orchestrator.get_all_candidates()
                                            if c.candidate_id == candidate_id), None)
                            candidate_name = candidate.name if candidate else "Unknown"
                            print(f"  {candidate_name}: {votes} votes")
                    else:
                        print("❌ No results found")
                elif cmd == "show_stats":
                    stats = self.orchestrator.get_system_statistics()
                    print("📊 System Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                else:
                    print("❌ Invalid command or insufficient arguments")

            except Exception as e:
                print(f"❌ Error: {e}")

        print("👋 Interactive demo ended!")


def main():
    """Main entry point for the demo"""
    demo = VotingSystemDemo()

    # Ask user for demo type
    print("Choose demo type:")
    print("1. Full automated demo")
    print("2. Interactive demo")
    print("3. Quick test")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        demo.run_full_demo()
    elif choice == "2":
        demo.run_interactive_demo()
    elif choice == "3":
        print("Running quick test...")
        demo._setup_phase()
        demo._registration_phase()
        demo._statistics_demo()
        print("✅ Quick test completed!")
    else:
        print("Invalid choice. Running full demo...")
        demo.run_full_demo()


if __name__ == "__main__":
    main()
