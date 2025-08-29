"""
Goal:
    - Create a voting system that allows users to vote on a list of options


Functional Requirements:
- Users can vote on a list of options
- Users can see the results of the voting
- Users can see the total number of votes
- Users can see the total number of votes for each option


Non-Functional Requirements:
- The system should be able to handle concurrent requests

Entities:
- User
- Vote 
- Candidate
- Election
- Voting Booth
- Voting Machine
- Voting System
- Voting Result
- Voting Record


Entity-Manager:
- UserManager
- VoteManager
- CandidateManager
- ElectionManager
- VotingBoothManager
- VotingMachineManager
- VotingSystemManager
- VotingResultManager
- VotingRecordManager

Repositories:
from abc import ABC, abstractmethod

class AbstractUserRepository(ABC):
    pass

class AbstractVoteRepository(ABC):
    pass

class AbstractCandidateRepository(ABC):
    pass

class AbstractElectionRepository(ABC):
    pass

class AbstractVotingBoothRepository(ABC):
    pass

class AbstractVotingMachineRepository(ABC):
    pass

class AbstractVotingSystemRepository(ABC):
    pass

class AbstractVotingResultRepository(ABC):
    pass

class AbstractVotingRecordRepository(ABC):
    pass




System-Orchestrator:
- VotingSystemOrchestrator


Design-patterns:
- Repository Pattern
- Factory Pattern
- Singleton Pattern
- Strategy Pattern
- Observer Pattern


Design Guidelines:
Design Guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Do not use any external libraries.
- Write the code in a way that it is easy to understand and easy to maintain.
- Keep the code modular and short which satisfies the requirements. and single responsibility principle.
- Respository function names should be self-explanatory.
- YOu can use repository class to store different entities and then extend it to in-memory or other storage systems.
- Do not use generics for now but create different abstractions for different entities.
- Each entity should be able to handle its invariants and validations and business logic.
- Use type hints for all functions and variables.
- Use the Repository Pattern for data access
- Use the Factory Pattern for object creation
- Use the Singleton Pattern for global access
- Use the Strategy Pattern for interchangeable voting algorithms
- Use the Observer Pattern for event-driven updates


"""