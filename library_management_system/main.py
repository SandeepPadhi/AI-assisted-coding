"""
Library Management System

Goal:
- Create a Library Management System

Functional Requirements:
- User can add a new book to the library
- User can borrow a book from the library
- User can return a book to the library
- User can see the list of all books in the library
- User can be fined for late return of a book


Non-Functional Requirements:
- The system should be able to handle 1000 requests per second
- The system should be able to scale to 1000000 requests per second


Entities:
- Book
- User
- Library
- Fine

EntityManager:
- BookManager
- UserManager
- LibraryManager
- FineManager

Repository:
- BookRepository
- UserRepository
- LibraryRepository
- FineRepository

SystemOrchestrator:
- LibrarySystem
 
ExternalServices:
- PaymentService


Design guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Implement the repository in-memory, but design it so it can be extended to other storage systems
- do not sure any external libraries.
- Write the code in a way that it is easy to understand and easy to maintain.
- Keep the code modular and short which satisfies the requirements. and single responsibility principle.
- Respository function names should be self-explanatory.
- YOu can use repository class to store different entities and then extend it to in-memory or other storage systems.
- Do not use generics for now but create different abstractions for different entities.
- Each entity should be able to handle its invariants and validations and business logic.
- Use type hints for all functions and variables.
- Keep correct indentation and code structure.

"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Entity definitions
@dataclass
class Book:
    isbn: str
    title: str
    author: str
    is_available: bool = True

    def __post_init__(self) -> None:
        if not self.isbn or len(self.isbn) != 13:
            raise ValueError("ISBN must be a 13-digit string")
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not self.author:
            raise ValueError("Author cannot be empty")

    def mark_as_borrowed(self) -> None:
        if not self.is_available:
            raise ValueError("Book is already borrowed")
        self.is_available = False

    def mark_as_returned(self) -> None:
        if self.is_available:
            raise ValueError("Book is already available")
        self.is_available = True

@dataclass
class User:
    user_id: str
    name: str
    email: str
    borrowed_books: List[str] = None  # List of ISBN numbers

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email format")
        if self.borrowed_books is None:
            self.borrowed_books = []

@dataclass
class Fine:
    user_id: str
    book_isbn: str
    amount: float
    due_date: datetime
    return_date: Optional[datetime] = None
    is_paid: bool = False

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.book_isbn:
            raise ValueError("Book ISBN cannot be empty")
        if self.amount < 0:
            raise ValueError("Fine amount cannot be negative")
        if not isinstance(self.due_date, datetime):
            raise ValueError("Due date must be a datetime object")

    def calculate_fine(self, current_date: datetime = None) -> float:
        if current_date is None:
            current_date = datetime.now()
        if not self.return_date:
            days_overdue = (current_date - self.due_date).days
        else:
            days_overdue = (self.return_date - self.due_date).days
        return max(0, days_overdue * 1.0)  # $1 per day overdue

class Library:
    def __init__(self, name: str, location: str):
        if not name:
            raise ValueError("Library name cannot be empty")
        if not location:
            raise ValueError("Library location cannot be empty")
        self.name = name
        self.location = location
        self.loan_duration = timedelta(days=14)  # Default loan period is 14 days

# Repository implementations
class BookRepository:
    def __init__(self):
        self._books: Dict[str, Book] = {}  # ISBN -> Book mapping

    def add(self, book: Book) -> None:
        if book.isbn in self._books:
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self._books[book.isbn] = book

    def get(self, isbn: str) -> Optional[Book]:
        return self._books.get(isbn)

    def get_all(self) -> List[Book]:
        return list(self._books.values())

    def update(self, book: Book) -> None:
        if book.isbn not in self._books:
            raise ValueError(f"Book with ISBN {book.isbn} not found")
        self._books[book.isbn] = book

    def delete(self, isbn: str) -> None:
        if isbn not in self._books:
            raise ValueError(f"Book with ISBN {isbn} not found")
        del self._books[isbn]

class UserRepository:
    def __init__(self):
        self._users: Dict[str, User] = {}  # user_id -> User mapping

    def add(self, user: User) -> None:
        if user.user_id in self._users:
            raise ValueError(f"User with ID {user.user_id} already exists")
        self._users[user.user_id] = user

    def get(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_all(self) -> List[User]:
        return list(self._users.values())

    def update(self, user: User) -> None:
        if user.user_id not in self._users:
            raise ValueError(f"User with ID {user.user_id} not found")
        self._users[user.user_id] = user

    def delete(self, user_id: str) -> None:
        if user_id not in self._users:
            raise ValueError(f"User with ID {user_id} not found")
        del self._users[user_id]

class FineRepository:
    def __init__(self):
        self._fines: List[Fine] = []

    def add(self, fine: Fine) -> None:
        self._fines.append(fine)

    def get_by_user(self, user_id: str) -> List[Fine]:
        return [fine for fine in self._fines if fine.user_id == user_id]

    def get_by_book(self, book_isbn: str) -> List[Fine]:
        return [fine for fine in self._fines if fine.book_isbn == book_isbn]

    def get_unpaid(self) -> List[Fine]:
        return [fine for fine in self._fines if not fine.is_paid]

    def update(self, fine: Fine) -> None:
        for i, existing_fine in enumerate(self._fines):
            if (existing_fine.user_id == fine.user_id and 
                existing_fine.book_isbn == fine.book_isbn and 
                existing_fine.due_date == fine.due_date):
                self._fines[i] = fine
                return
        raise ValueError("Fine not found")

class LibraryRepository:
    def __init__(self):
        self._libraries: Dict[str, Library] = {}  # name -> Library mapping

    def add(self, library: Library) -> None:
        if library.name in self._libraries:
            raise ValueError(f"Library with name {library.name} already exists")
        self._libraries[library.name] = library

    def get(self, name: str) -> Optional[Library]:
        return self._libraries.get(name)

    def get_all(self) -> List[Library]:
        return list(self._libraries.values())

    def update(self, library: Library) -> None:
        if library.name not in self._libraries:
            raise ValueError(f"Library with name {library.name} not found")
        self._libraries[library.name] = library

    def delete(self, name: str) -> None:
        if name not in self._libraries:
            raise ValueError(f"Library with name {name} not found")
        del self._libraries[name]

# Entity Managers
class BookManager:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    def add_book(self, isbn: str, title: str, author: str) -> Book:
        book = Book(isbn=isbn, title=title, author=author)
        self.book_repository.add(book)
        return book

    def get_book(self, isbn: str) -> Optional[Book]:
        return self.book_repository.get(isbn)

    def get_all_books(self) -> List[Book]:
        return self.book_repository.get_all()

    def mark_book_as_borrowed(self, isbn: str) -> None:
        book = self.get_book(isbn)
        if not book:
            raise ValueError(f"Book with ISBN {isbn} not found")
        book.mark_as_borrowed()
        self.book_repository.update(book)

    def mark_book_as_returned(self, isbn: str) -> None:
        book = self.get_book(isbn)
        if not book:
            raise ValueError(f"Book with ISBN {isbn} not found")
        book.mark_as_returned()
        self.book_repository.update(book)

class UserManager:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, user_id: str, name: str, email: str) -> User:
        user = User(user_id=user_id, name=name, email=email)
        self.user_repository.add(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repository.get(user_id)

    def add_borrowed_book(self, user_id: str, book_isbn: str) -> None:
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        if book_isbn not in user.borrowed_books:
            user.borrowed_books.append(book_isbn)
            self.user_repository.update(user)

    def remove_borrowed_book(self, user_id: str, book_isbn: str) -> None:
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        if book_isbn in user.borrowed_books:
            user.borrowed_books.remove(book_isbn)
            self.user_repository.update(user)

class FineManager:
    def __init__(self, fine_repository: FineRepository):
        self.fine_repository = fine_repository

    def create_fine(self, user_id: str, book_isbn: str, due_date: datetime) -> Fine:
        fine = Fine(user_id=user_id, book_isbn=book_isbn, amount=0.0, due_date=due_date)
        self.fine_repository.add(fine)
        return fine

    def get_user_fines(self, user_id: str) -> List[Fine]:
        return self.fine_repository.get_by_user(user_id)

    def mark_fine_as_paid(self, fine: Fine) -> None:
        fine.is_paid = True
        self.fine_repository.update(fine)

    def calculate_fine_amount(self, fine: Fine, return_date: datetime) -> float:
        fine.return_date = return_date
        amount = fine.calculate_fine()
        fine.amount = amount
        self.fine_repository.update(fine)
        return amount

class LibraryManager:
    def __init__(self, 
                 library_repository: LibraryRepository,
                 book_manager: BookManager,
                 user_manager: UserManager,
                 fine_manager: FineManager):
        self.library_repository = library_repository
        self.book_manager = book_manager
        self.user_manager = user_manager
        self.fine_manager = fine_manager

    def borrow_book(self, user_id: str, book_isbn: str) -> Tuple[datetime, datetime]:
        # Check if book and user exist
        book = self.book_manager.get_book(book_isbn)
        user = self.user_manager.get_user(user_id)
        if not book or not user:
            raise ValueError("Book or user not found")

        # Check if book is available
        if not book.is_available:
            raise ValueError("Book is not available")

        # Get library settings (using first library for simplicity)
        library = self.library_repository.get_all()[0]
        borrow_date = datetime.now()
        due_date = borrow_date + library.loan_duration

        # Update book and user status
        self.book_manager.mark_book_as_borrowed(book_isbn)
        self.user_manager.add_borrowed_book(user_id, book_isbn)

        # Create a fine record
        self.fine_manager.create_fine(user_id, book_isbn, due_date)

        return borrow_date, due_date

    def return_book(self, user_id: str, book_isbn: str) -> float:
        # Check if book and user exist
        book = self.book_manager.get_book(book_isbn)
        user = self.user_manager.get_user(user_id)
        if not book or not user:
            raise ValueError("Book or user not found")

        # Check if user has borrowed this book
        if book_isbn not in user.borrowed_books:
            raise ValueError("User has not borrowed this book")

        return_date = datetime.now()

        # Update book and user status
        self.book_manager.mark_book_as_returned(book_isbn)
        self.user_manager.remove_borrowed_book(user_id, book_isbn)

        # Calculate and update fine if any
        fines = self.fine_manager.get_user_fines(user_id)
        relevant_fines = [f for f in fines if f.book_isbn == book_isbn and not f.return_date]
        
        if relevant_fines:
            fine = relevant_fines[0]  # Get the most recent fine
            return self.fine_manager.calculate_fine_amount(fine, return_date)
        
        return 0.0

# External Services
class PaymentService:
    def process_payment(self, user_id: str, amount: float) -> bool:
        """
        Process a fine payment for a user.
        In a real system, this would integrate with a payment gateway.
        """
        # Simplified implementation for demo purposes
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        # Assume payment is always successful
        return True

# System Orchestrator
class LibrarySystem:
    def __init__(self):
        # Initialize repositories
        self.book_repository = BookRepository()
        self.user_repository = UserRepository()
        self.library_repository = LibraryRepository()
        self.fine_repository = FineRepository()

        # Initialize managers
        self.book_manager = BookManager(self.book_repository)
        self.user_manager = UserManager(self.user_repository)
        self.fine_manager = FineManager(self.fine_repository)
        self.library_manager = LibraryManager(
            self.library_repository,
            self.book_manager,
            self.user_manager,
            self.fine_manager
        )

        # Initialize external services
        self.payment_service = PaymentService()

        # Initialize a default library
        self._setup_default_library()

    def _setup_default_library(self) -> None:
        """Set up a default library if none exists."""
        if not self.library_repository.get_all():
            default_library = Library("Main Library", "123 Library Street")
            self.library_repository.add(default_library)

    # Book Management
    def add_book(self, isbn: str, title: str, author: str) -> Book:
        """Add a new book to the library."""
        return self.book_manager.add_book(isbn, title, author)

    def get_all_books(self) -> List[Book]:
        """Get all books in the library."""
        return self.book_manager.get_all_books()

    def get_book(self, isbn: str) -> Optional[Book]:
        """Get a specific book by ISBN."""
        return self.book_manager.get_book(isbn)

    # User Management
    def register_user(self, user_id: str, name: str, email: str) -> User:
        """Register a new user."""
        return self.user_manager.register_user(user_id, name, email)

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.user_manager.get_user(user_id)

    # Loan Management
    def borrow_book(self, user_id: str, book_isbn: str) -> Tuple[datetime, datetime]:
        """
        Borrow a book from the library.
        Returns the borrow date and due date.
        """
        return self.library_manager.borrow_book(user_id, book_isbn)

    def return_book(self, user_id: str, book_isbn: str) -> float:
        """
        Return a book to the library.
        Returns the fine amount if any.
        """
        fine_amount = self.library_manager.return_book(user_id, book_isbn)
        return fine_amount

    # Fine Management
    def get_user_fines(self, user_id: str) -> List[Fine]:
        """Get all fines for a user."""
        return self.fine_manager.get_user_fines(user_id)

    def calculate_fine(self, user_id: str, book_isbn: str, check_date: datetime = None) -> float:
        """
        Calculate the fine amount for a specific book borrowed by a user.
        
        Args:
            user_id: The ID of the user
            book_isbn: The ISBN of the book
            check_date: Optional date to calculate fines up to (defaults to current date)
            
        Returns:
            The fine amount in dollars
            
        Raises:
            ValueError: If the user hasn't borrowed the book or if user/book doesn't exist
        """
        # Verify user and book exist
        user = self.get_user(user_id)
        book = self.get_book(book_isbn)
        if not user or not book:
            raise ValueError("User or book not found")
            
        # Get the relevant fine record
        fines = self.fine_manager.get_user_fines(user_id)
        relevant_fines = [f for f in fines if f.book_isbn == book_isbn and not f.return_date]
        
        if not relevant_fines:
            raise ValueError("No active loan found for this book")
            
        fine = relevant_fines[0]  # Get the most recent fine
        return fine.calculate_fine(check_date)

    def pay_fine(self, user_id: str, fine: Fine) -> bool:
        """
        Pay a fine for a user.
        Returns True if payment was successful.
        """
        if fine.is_paid:
            raise ValueError("Fine is already paid")

        # Process payment
        payment_success = self.payment_service.process_payment(user_id, fine.amount)
        if payment_success:
            self.fine_manager.mark_fine_as_paid(fine)
        return payment_success

# Example usage
def run_tests() -> None:
    """Run comprehensive tests for the Library Management System."""
    print("\n=== Running Library Management System Tests ===\n")
    
    # Initialize the system
    library_system = LibrarySystem()

    # Test 0: Fine Calculation with Actual Dates
    print("Test 0: Fine Calculation with Actual Dates")
    try:
        # Register a user and add a book
        test_user = library_system.register_user("test_user", "Test User", "test@example.com")
        test_book = library_system.add_book("9876543210123", "Test Book", "Test Author")
        print("✓ Setup test user and book")

        # Borrow the book
        borrow_date, due_date = library_system.borrow_book(test_user.user_id, test_book.isbn)
        print("✓ Book borrowed successfully")
        
        # Calculate fine for a specific future date (6 days after due date)
        check_date = due_date + timedelta(days=6)
        fine_amount = library_system.calculate_fine(test_user.user_id, test_book.isbn, check_date)
        
        # We expect 6 days of fines
        expected_fine = 6.0  # $1 per day for 6 days
        assert abs(fine_amount - expected_fine) < 0.1, f"Expected fine of ${expected_fine}, got ${fine_amount}"
        print(f"✓ Fine calculation correct: ${fine_amount} for 6 days overdue")
        
        # Return the book
        actual_fine = library_system.return_book(test_user.user_id, test_book.isbn)
        print("✓ Book returned successfully")
        print("✓ Successfully completed fine calculation test")
        
    except Exception as e:
        print(f"✗ Fine Calculation test failed: {str(e)}")
    print()
    
    # Test 1: Book Management
    print("Test 1: Book Management")
    try:
        # Add books
        book1 = library_system.add_book("1234567890123", "The Great Gatsby", "F. Scott Fitzgerald")
        book2 = library_system.add_book("1234567890124", "To Kill a Mockingbird", "Harper Lee")
        print("✓ Successfully added books")
        
        # Try to add duplicate book
        try:
            library_system.add_book("1234567890123", "Duplicate Book", "Some Author")
            print("✗ Failed to catch duplicate ISBN")
        except ValueError as e:
            print("✓ Successfully caught duplicate ISBN")
        
        # Try to add invalid ISBN
        try:
            library_system.add_book("123", "Invalid ISBN", "Some Author")
            print("✗ Failed to catch invalid ISBN")
        except ValueError as e:
            print("✓ Successfully caught invalid ISBN")
            
        # Get all books
        all_books = library_system.get_all_books()
        assert len(all_books) == 2, "Expected 2 books in the library"
        print("✓ Successfully retrieved all books")
        
    except Exception as e:
        print(f"✗ Book Management test failed: {str(e)}")
    print()

    # Test 2: User Management
    print("Test 2: User Management")
    try:
        # Register users
        user1 = library_system.register_user("user123", "John Doe", "john@example.com")
        user2 = library_system.register_user("user124", "Jane Smith", "jane@example.com")
        print("✓ Successfully registered users")
        
        # Try to register duplicate user
        try:
            library_system.register_user("user123", "Duplicate User", "dup@example.com")
            print("✗ Failed to catch duplicate user ID")
        except ValueError as e:
            print("✓ Successfully caught duplicate user ID")
        
        # Try to register user with invalid email
        try:
            library_system.register_user("user125", "Invalid Email", "invalid-email")
            print("✗ Failed to catch invalid email")
        except ValueError as e:
            print("✓ Successfully caught invalid email")
            
    except Exception as e:
        print(f"✗ User Management test failed: {str(e)}")
    print()

    # Test 3: Book Borrowing and Returns
    print("Test 3: Book Borrowing and Returns")
    try:
        # Borrow a book
        library_system.borrow_book(user1.user_id, book1.isbn)
        print("✓ Successfully borrowed book")
        
        # Try to borrow same book again
        try:
            library_system.borrow_book(user2.user_id, book1.isbn)
            print("✗ Failed to catch already borrowed book")
        except ValueError as e:
            print("✓ Successfully caught already borrowed book")
        
        # Try to borrow non-existent book
        try:
            library_system.borrow_book(user1.user_id, "nonexistent")
            print("✗ Failed to catch non-existent book")
        except ValueError as e:
            print("✓ Successfully caught non-existent book")
        
        # Return book
        fine_amount = library_system.return_book(user1.user_id, book1.isbn)
        print("✓ Successfully returned book")
        print(f"✓ Fine amount calculated: ${fine_amount}")
        
        # Try to return already returned book
        try:
            library_system.return_book(user1.user_id, book1.isbn)
            print("✗ Failed to catch already returned book")
        except ValueError as e:
            print("✓ Successfully caught already returned book")
            
    except Exception as e:
        print(f"✗ Book Borrowing and Returns test failed: {str(e)}")
    print()

    # Test 4: Fine Management
    print("Test 4: Fine Management")
    try:
        # Borrow and return a book (simulating late return)
        library_system.borrow_book(user2.user_id, book2.isbn)
        fine_amount = library_system.return_book(user2.user_id, book2.isbn)
        
        if fine_amount > 0:
            fines = library_system.get_user_fines(user2.user_id)
            assert len(fines) > 0, "Expected fines for late return"
            
            # Pay fine
            payment_success = library_system.pay_fine(user2.user_id, fines[0])
            assert payment_success, "Expected successful payment"
            print("✓ Successfully handled fine payment")
            
            # Try to pay same fine again
            try:
                library_system.pay_fine(user2.user_id, fines[0])
                print("✗ Failed to catch already paid fine")
            except ValueError as e:
                print("✓ Successfully caught already paid fine")
        
        # Check unpaid fines
        fines = library_system.get_user_fines(user2.user_id)
        print("✓ Successfully retrieved user fines")
            
    except Exception as e:
        print(f"✗ Fine Management test failed: {str(e)}")
    print()

    # Test 5: Edge Cases
    print("Test 5: Edge Cases")
    try:
        # Try to get non-existent user
        assert library_system.get_user("nonexistent") is None
        print("✓ Successfully handled non-existent user")
        
        # Try to get non-existent book
        assert library_system.get_book("nonexistent") is None
        print("✓ Successfully handled non-existent book")
        
        # Try to borrow book with non-existent user
        try:
            library_system.borrow_book("nonexistent", book1.isbn)
            print("✗ Failed to catch non-existent user borrowing")
        except ValueError as e:
            print("✓ Successfully caught non-existent user borrowing")
            
        # Try to create user with empty values
        try:
            library_system.register_user("", "", "")
            print("✗ Failed to catch empty user details")
        except ValueError as e:
            print("✓ Successfully caught empty user details")
            
    except Exception as e:
        print(f"✗ Edge Cases test failed: {str(e)}")
    print()

    print("=== Test Suite Completed ===\n")

def run_example() -> None:
    """Run example usage of the Library Management System."""
    # Initialize the library system
    library_system = LibrarySystem()

    # Add some books
    book1 = library_system.add_book("1234567890123", "The Great Gatsby", "F. Scott Fitzgerald")
    book2 = library_system.add_book("1234567890124", "To Kill a Mockingbird", "Harper Lee")

    # Register a user
    user = library_system.register_user("user123", "John Doe", "john@example.com")

    # Borrow a book
    borrow_date, due_date = library_system.borrow_book(user.user_id, book1.isbn)
    print(f"Borrowed book until {due_date}")

    # Return the book (assuming it's late)
    fine_amount = library_system.return_book(user.user_id, book1.isbn)
    if fine_amount > 0:
        print(f"Fine amount: ${fine_amount}")
        # Get user's fines
        fines = library_system.get_user_fines(user.user_id)
        # Pay the fine
        if fines:
            payment_success = library_system.pay_fine(user.user_id, fines[0])
            print(f"Fine payment {'successful' if payment_success else 'failed'}")

def main() -> None:
    """Run example usage or tests based on command line arguments."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        run_example()

if __name__ == "__main__":
    main()