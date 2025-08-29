"""
Demo script to showcase the Ride Sharing Application functionality
"""

from orchestrator import RideSharingAppSystem


def main() -> None:
    """Main demo function"""
    print("=" * 60)
    print("RIDE SHARING APPLICATION DEMO")
    print("=" * 60)

    # Initialize the system
    system = RideSharingAppSystem()

    print("\n1. REGISTERING USERS AND DRIVERS")
    print("-" * 40)

    # Register users
    user1 = system.register_user("John Doe", "john@example.com", "123-456-7890")
    user2 = system.register_user("Jane Smith", "jane@example.com", "098-765-4321")
    print(f"✓ User registered: {user1.name} (ID: {user1.user_id})")
    print(f"✓ User registered: {user2.name} (ID: {user2.user_id})")

    # Register drivers
    driver1 = system.register_driver("Bob Wilson", "bob@example.com", "555-123-4567", "DL123456")
    driver2 = system.register_driver("Alice Brown", "alice@example.com", "555-987-6543", "DL789012")
    print(f"✓ Driver registered: {driver1.name} (ID: {driver1.driver_id})")
    print(f"✓ Driver registered: {driver2.name} (ID: {driver2.driver_id})")

    # Register vehicles for drivers
    vehicle1 = system.register_vehicle_for_driver(driver1.driver_id, "Toyota", "Camry", 2020, "ABC-123")
    vehicle2 = system.register_vehicle_for_driver(driver2.driver_id, "Honda", "Civic", 2019, "XYZ-789")
    print(f"✓ Vehicle registered for {driver1.name}: {vehicle1.make} {vehicle1.model}")
    print(f"✓ Vehicle registered for {driver2.name}: {vehicle2.make} {vehicle2.model}")

    print("\n2. REQUESTING RIDES")
    print("-" * 40)

    # User 1 requests a ride
    ride1 = system.request_ride(
        user1.user_id,
        pickup_lat=37.7749, pickup_lon=-122.4194,  # San Francisco
        dropoff_lat=37.7849, dropoff_lon=-122.4094  # Nearby location
    )
    print(f"✓ Ride requested by {user1.name} (Trip ID: {ride1.trip_id})")
    print(f"  Status: {ride1.status.value}")
    print(f"  Distance: {ride1.pickup_location.calculate_distance(ride1.dropoff_location):.2f} km")

    # User 2 requests a ride
    ride2 = system.request_ride(
        user2.user_id,
        pickup_lat=37.7849, pickup_lon=-122.4094,  # Different location
        dropoff_lat=37.7649, dropoff_lon=-122.4294  # Another location
    )
    print(f"✓ Ride requested by {user2.name} (Trip ID: {ride2.trip_id})")
    print(f"  Status: {ride2.status.value}")

    print("\n3. CHECKING AVAILABLE RIDES")
    print("-" * 40)

    available_rides = system.get_requested_rides()
    print(f"✓ Available rides: {len(available_rides)}")
    for ride in available_rides:
        user = system.get_user(ride.user_id)
        if user:
            print(f"  - Trip {ride.trip_id} by {user.name}")

    print("\n4. DRIVERS ACCEPTING RIDES")
    print("-" * 40)

    # Driver 1 accepts ride 1
    accepted = system.accept_ride(ride1.trip_id, driver1.driver_id)
    print(f"✓ Driver {driver1.name} accepted ride {ride1.trip_id}: {accepted}")

    # Driver 2 accepts ride 2
    accepted = system.accept_ride(ride2.trip_id, driver2.driver_id)
    print(f"✓ Driver {driver2.name} accepted ride {ride2.trip_id}: {accepted}")

    print("\n5. STARTING RIDES")
    print("-" * 40)

    # Start both rides
    started1 = system.start_ride(ride1.trip_id)
    started2 = system.start_ride(ride2.trip_id)
    print(f"✓ Ride {ride1.trip_id} started: {started1}")
    print(f"✓ Ride {ride2.trip_id} started: {started2}")

    print("\n6. COMPLETING RIDES")
    print("-" * 40)

    # Complete ride 1 (10 km distance)
    completed1 = system.complete_ride(ride1.trip_id, 10.0)
    print(f"✓ Ride {ride1.trip_id} completed: {completed1}")

    # Complete ride 2 (15 km distance)
    completed2 = system.complete_ride(ride2.trip_id, 15.0)
    print(f"✓ Ride {ride2.trip_id} completed: {completed2}")

    print("\n6b. CREATING ADDITIONAL TRIP FOR PAYMENT DEMO")
    print("-" * 50)

    # Create a third trip to demonstrate different payment methods
    print("Creating a third trip to showcase different payment methods...")
    ride3 = system.request_ride(
        user1.user_id,
        pickup_lat=37.7649, pickup_lon=-122.4294,  # Different location
        dropoff_lat=37.7949, dropoff_lon=-122.3994  # Another location
    )
    print(f"✓ Additional ride requested by {user1.name} (Trip ID: {ride3.trip_id})")

    # Driver 1 accepts the third ride
    system.accept_ride(ride3.trip_id, driver1.driver_id)
    system.start_ride(ride3.trip_id)
    completed3 = system.complete_ride(ride3.trip_id, 8.0)  # Just complete, payment separate
    print(f"✓ Additional ride {ride3.trip_id} completed: {completed3}")

    print("\n8. VIEWING TRIP BILLS")
    print("-" * 40)
    print("📋 SUMMARY: We have 3 completed rides that generated 3 bills")
    print("   - Ride 1: John Doe's first ride (10 km)")
    print("   - Ride 2: Jane Smith's ride (15 km)")
    print("   - Ride 3: John Doe's additional ride (8 km) - created for payment demo")
    print("💡 This demonstrates how the same user can have multiple rides with different payment methods\n")

    # Get bills for all trips
    bill1 = system.get_trip_bill(ride1.trip_id)
    bill2 = system.get_trip_bill(ride2.trip_id)
    bill3 = system.get_trip_bill(ride3.trip_id)

    if bill1:
        print(f"✓ Bill for trip {ride1.trip_id}:")
        print(f"  Base fare: ${bill1.base_fare:.2f}")
        print(f"  Distance fare: ${bill1.distance_fare:.2f}")
        print(f"  Tax: ${bill1.tax_amount:.2f}")
        print(f"  Total: ${bill1.total_amount:.2f}")

    if bill2:
        print(f"✓ Bill for trip {ride2.trip_id}:")
        print(f"  Base fare: ${bill2.base_fare:.2f}")
        print(f"  Distance fare: ${bill2.distance_fare:.2f}")
        print(f"  Tax: ${bill2.tax_amount:.2f}")
        print(f"  Total: ${bill2.total_amount:.2f}")

    if bill3:
        print(f"✓ Bill for trip {ride3.trip_id}:")
        print(f"  Base fare: ${bill3.base_fare:.2f}")
        print(f"  Distance fare: ${bill3.distance_fare:.2f}")
        print(f"  Tax: ${bill3.tax_amount:.2f}")
        print(f"  Total: ${bill3.total_amount:.2f}")

    print("\n9. USER PAYMENT METHOD SELECTION")
    print("-" * 40)

    # User 1 chooses cash payment for ride 1
    print(f"User {user1.name} chooses to pay with cash for trip {ride1.trip_id}")
    cash_payment1 = system.pay_with_cash(ride1.trip_id)
    print(f"✓ Cash payment processed: {cash_payment1}")

    # User 2 chooses credit card payment for ride 2
    print(f"User {user2.name} chooses to pay with credit card for trip {ride2.trip_id}")
    card_payment2 = system.pay_with_credit_card(
        ride2.trip_id,
        card_number="4111111111111111",  # Valid test card number
        expiry_date="12/26",
        cvv="123",
        card_holder_name=user2.name
    )
    print(f"✓ Credit card payment processed: {card_payment2}")

    # User 1 chooses UPI payment for ride 3
    print(f"User {user1.name} chooses to pay with UPI for trip {ride3.trip_id}")
    upi_payment3 = system.pay_with_upi(
        ride3.trip_id,
        upi_id="john.doe@paytm",
        upi_app="gpay"
    )
    print(f"✓ UPI payment processed: {upi_payment3}")

    print("\n10. PAYMENT METHOD ANALYSIS")
    print("-" * 40)

    # Get payments by method
    cash_payments = system.get_payments_by_method("cash")
    credit_card_payments = system.get_payments_by_method("credit_card")
    upi_payments = system.get_payments_by_method("upi")

    print(f"✓ Cash payments: {len(cash_payments)}")
    print(f"✓ Credit card payments: {len(credit_card_payments)}")
    print(f"✓ UPI payments: {len(upi_payments)}")

    # Show payment details
    if cash_payments:
        cash_payment = cash_payments[0]
        print(f"  Cash payment {cash_payment.payment_id}: ${cash_payment.amount:.2f} ({cash_payment.status})")

    if credit_card_payments:
        card_payment = credit_card_payments[0]
        print(f"  Credit card payment {card_payment.payment_id}: ${card_payment.amount:.2f} ({card_payment.status})")
        if hasattr(card_payment, 'card_holder_name'):
            print(f"    Card holder: {card_payment.card_holder_name}")

    if upi_payments:
        upi_payment = upi_payments[0]
        print(f"  UPI payment {upi_payment.payment_id}: ${upi_payment.amount:.2f} ({upi_payment.status})")
        if hasattr(upi_payment, 'upi_id'):
            print(f"    UPI ID: {upi_payment.upi_id}")

    print("\n10. RATING DRIVERS")
    print("-" * 40)

    # Users rate drivers
    system.rate_driver(driver1.driver_id, 4.5)
    system.rate_driver(driver2.driver_id, 5.0)
    print(f"✓ {user1.name} rated {driver1.name}: 4.5 stars")
    print(f"✓ {user2.name} rated {driver2.name}: 5.0 stars")

    # Check updated driver ratings
    updated_driver1 = system.driver_manager.get_driver(driver1.driver_id)
    updated_driver2 = system.driver_manager.get_driver(driver2.driver_id)

    if updated_driver1:
        print(f"✓ Updated rating for {driver1.name}: {updated_driver1.rating:.2f} stars")
    if updated_driver2:
        print(f"✓ Updated rating for {driver2.name}: {updated_driver2.rating:.2f} stars")

    print("\n11. VIEWING TRIP HISTORY")
    print("-" * 40)

    # Get trip history for users
    user1_trips = system.get_user_trip_history(user1.user_id)
    user2_trips = system.get_user_trip_history(user2.user_id)

    print(f"✓ {user1.name}'s trip history: {len(user1_trips)} trips")
    for trip in user1_trips:
        print(f"  - Trip {trip.trip_id}: {trip.status.value}")

    print(f"✓ {user2.name}'s trip history: {len(user2_trips)} trips")
    for trip in user2_trips:
        print(f"  - Trip {trip.trip_id}: {trip.status.value}")

    # Get trip history for drivers
    driver1_trips = system.get_driver_trip_history(driver1.driver_id)
    driver2_trips = system.get_driver_trip_history(driver2.driver_id)

    print(f"✓ {driver1.name}'s trip history: {len(driver1_trips)} trips")
    print(f"✓ {driver2.name}'s trip history: {len(driver2_trips)} trips")

    print("\n12. SYSTEM SUMMARY")
    print("-" * 40)

    all_users = system.get_all_users()
    available_drivers = system.get_available_drivers()
    requested_rides = system.get_requested_rides()

    print(f"✓ Total users: {len(all_users)}")
    print(f"✓ Available drivers: {len(available_drivers)}")
    print(f"✓ Requested rides: {len(requested_rides)}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
