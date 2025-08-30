"""
Train Ticket Booking System - Main Entry Point

This module demonstrates the complete train ticket booking system
with all core functionality implemented.
"""

from orchestrator import TrainTicketBookingSystem


def main():
    """Main entry point for the train ticket booking system"""
    # Create and run the system demo
    system = TrainTicketBookingSystem()
    system.run_demo()


if __name__ == "__main__":
    main()