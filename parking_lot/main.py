"""
Help me implement this:

Design a modular, extensible parking lot system in Python using OOP principles and appropriate design patterns (such as Factory). The system should be easy to understand, maintain, and extend. 

Requirements:
- Users can create a parking lot
- Users can park and unpark cars
- Users can get the status of the parking lot
- Users can get the status of a specific car
- Users can get the status of all cars
- Users can get the bill for a specific car

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
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


# ==================== ENTITIES ====================

class VehicleType(Enum):
    """Enum for different types of vehicles"""
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"


class Vehicle:
    """Entity representing a vehicle"""
    
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.parking_spot_id: Optional[str] = None
        self.entry_time: Optional[datetime] = None
        self.exit_time: Optional[datetime] = None
    
    def __str__(self):
        return f"{self.vehicle_type.value.upper()}({self.license_plate})"


class ParkingSpot:
    """Entity representing a parking spot"""
    
    def __init__(self, spot_id: str, vehicle_type: VehicleType, is_occupied: bool = False):
        self.spot_id = spot_id
        self.vehicle_type = vehicle_type
        self.is_occupied = is_occupied
        self.vehicle: Optional[Vehicle] = None
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Park a vehicle in this spot"""
        if self.is_occupied or vehicle.vehicle_type != self.vehicle_type:
            return False
        
        self.is_occupied = True
        self.vehicle = vehicle
        vehicle.parking_spot_id = self.spot_id
        vehicle.entry_time = datetime.now()
        return True
    
    def unpark_vehicle(self) -> Optional[Vehicle]:
        """Unpark vehicle from this spot"""
        if not self.is_occupied:
            return None
        
        vehicle = self.vehicle
        vehicle.exit_time = datetime.now()
        vehicle.parking_spot_id = None
        
        self.is_occupied = False
        self.vehicle = None
        return vehicle
    
    def __str__(self):
        status = "OCCUPIED" if self.is_occupied else "AVAILABLE"
        return f"Spot {self.spot_id} ({self.vehicle_type.value}) - {status}"


class ParkingLot:
    """Entity representing a parking lot"""
    
    def __init__(self, lot_id: str, name: str):
        self.lot_id = lot_id
        self.name = name
        self.spots: Dict[str, ParkingSpot] = {}
        self.vehicles: Dict[str, Vehicle] = {}
    
    def add_spot(self, spot: ParkingSpot):
        """Add a parking spot to the lot"""
        self.spots[spot.spot_id] = spot
    
    def get_available_spots(self, vehicle_type: VehicleType) -> List[ParkingSpot]:
        """Get all available spots for a vehicle type"""
        return [spot for spot in self.spots.values() 
                if not spot.is_occupied and spot.vehicle_type == vehicle_type]
    
    def get_occupied_spots(self) -> List[ParkingSpot]:
        """Get all occupied spots"""
        return [spot for spot in self.spots.values() if spot.is_occupied]
    
    def __str__(self):
        total_spots = len(self.spots)
        occupied_spots = len(self.get_occupied_spots())
        return f"Parking Lot: {self.name} ({occupied_spots}/{total_spots} occupied)"


# ==================== REPOSITORIES ====================

class ParkingLotRepository(ABC):
    """Abstract repository for parking lot entities"""
    
    @abstractmethod
    def save_parking_lot(self, lot_id: str, parking_lot: ParkingLot) -> None:
        """Save a parking lot to the repository"""
        pass
    
    @abstractmethod
    def find_parking_lot_by_id(self, lot_id: str) -> Optional[ParkingLot]:
        """Find a parking lot by its ID"""
        pass
    
    @abstractmethod
    def find_all_parking_lots(self) -> List[ParkingLot]:
        """Find all parking lots in the repository"""
        pass
    
    @abstractmethod
    def delete_parking_lot_by_id(self, lot_id: str) -> bool:
        """Delete a parking lot by its ID"""
        pass
    
    @abstractmethod
    def parking_lot_exists(self, lot_id: str) -> bool:
        """Check if a parking lot exists by its ID"""
        pass


class VehicleRepository(ABC):
    """Abstract repository for vehicle entities"""
    
    @abstractmethod
    def save_vehicle(self, license_plate: str, vehicle: Vehicle) -> None:
        """Save a vehicle to the repository"""
        pass
    
    @abstractmethod
    def find_vehicle_by_license_plate(self, license_plate: str) -> Optional[Vehicle]:
        """Find a vehicle by its license plate"""
        pass
    
    @abstractmethod
    def find_all_vehicles(self) -> List[Vehicle]:
        """Find all vehicles in the repository"""
        pass
    
    @abstractmethod
    def delete_vehicle_by_license_plate(self, license_plate: str) -> bool:
        """Delete a vehicle by its license plate"""
        pass
    
    @abstractmethod
    def vehicle_exists(self, license_plate: str) -> bool:
        """Check if a vehicle exists by its license plate"""
        pass


class InMemoryParkingLotRepository(ParkingLotRepository):
    """In-memory implementation of parking lot repository"""
    
    def __init__(self):
        self._parking_lots: Dict[str, ParkingLot] = {}
    
    def save_parking_lot(self, lot_id: str, parking_lot: ParkingLot) -> None:
        """Save a parking lot to in-memory storage"""
        self._parking_lots[lot_id] = parking_lot
    
    def find_parking_lot_by_id(self, lot_id: str) -> Optional[ParkingLot]:
        """Find a parking lot by its ID in memory"""
        return self._parking_lots.get(lot_id)
    
    def find_all_parking_lots(self) -> List[ParkingLot]:
        """Find all parking lots in memory"""
        return list(self._parking_lots.values())
    
    def delete_parking_lot_by_id(self, lot_id: str) -> bool:
        """Delete a parking lot by its ID from memory"""
        if lot_id in self._parking_lots:
            del self._parking_lots[lot_id]
            return True
        return False
    
    def parking_lot_exists(self, lot_id: str) -> bool:
        """Check if a parking lot exists by its ID in memory"""
        return lot_id in self._parking_lots
    
    def find_parking_lot_by_name(self, name: str) -> Optional[ParkingLot]:
        """Find a parking lot by its name"""
        for parking_lot in self._parking_lots.values():
            if parking_lot.name == name:
                return parking_lot
        return None
    
    def find_parking_lots_by_occupancy_rate(self, min_occupancy: float) -> List[ParkingLot]:
        """Find parking lots with occupancy rate above minimum"""
        result = []
        for parking_lot in self._parking_lots.values():
            total_spots = len(parking_lot.spots)
            if total_spots > 0:
                occupied_spots = len(parking_lot.get_occupied_spots())
                occupancy_rate = (occupied_spots / total_spots) * 100
                if occupancy_rate >= min_occupancy:
                    result.append(parking_lot)
        return result


class InMemoryVehicleRepository(VehicleRepository):
    """In-memory implementation of vehicle repository"""
    
    def __init__(self):
        self._vehicles: Dict[str, Vehicle] = {}
    
    def save_vehicle(self, license_plate: str, vehicle: Vehicle) -> None:
        """Save a vehicle to in-memory storage"""
        self._vehicles[license_plate] = vehicle
    
    def find_vehicle_by_license_plate(self, license_plate: str) -> Optional[Vehicle]:
        """Find a vehicle by its license plate in memory"""
        return self._vehicles.get(license_plate)
    
    def find_all_vehicles(self) -> List[Vehicle]:
        """Find all vehicles in memory"""
        return list(self._vehicles.values())
    
    def delete_vehicle_by_license_plate(self, license_plate: str) -> bool:
        """Delete a vehicle by its license plate from memory"""
        if license_plate in self._vehicles:
            del self._vehicles[license_plate]
            return True
        return False
    
    def vehicle_exists(self, license_plate: str) -> bool:
        """Check if a vehicle exists by its license plate in memory"""
        return license_plate in self._vehicles
    
    def find_parked_vehicles(self) -> List[Vehicle]:
        """Find all currently parked vehicles"""
        return [vehicle for vehicle in self._vehicles.values() 
                if vehicle.parking_spot_id is not None]
    
    def find_vehicles_by_type(self, vehicle_type: VehicleType) -> List[Vehicle]:
        """Find all vehicles of a specific type"""
        return [vehicle for vehicle in self._vehicles.values() 
                if vehicle.vehicle_type == vehicle_type]
    
    def find_vehicles_in_parking_lot(self, parking_lot_id: str) -> List[Vehicle]:
        """Find all vehicles parked in a specific parking lot"""
        return [vehicle for vehicle in self._vehicles.values() 
                if vehicle.parking_spot_id and vehicle.parking_spot_id.startswith(parking_lot_id)]


# ==================== FACTORY PATTERN ====================

class ParkingSpotFactory:
    """Factory for creating parking spots"""
    
    @staticmethod
    def create_parking_spots(vehicle_type: VehicleType, count: int, start_id: int = 1) -> List[ParkingSpot]:
        """Create multiple parking spots of the same type"""
        spots = []
        for i in range(count):
            spot_id = f"{vehicle_type.value}_{start_id + i:03d}"
            spots.append(ParkingSpot(spot_id, vehicle_type))
        return spots


# ==================== BILLING SERVICE ====================

class BillingService:
    """Service for calculating parking bills"""
    
    def __init__(self):
        self._hourly_rates = {
            VehicleType.CAR: 10.0,
            VehicleType.MOTORCYCLE: 5.0,
            VehicleType.TRUCK: 20.0
        }
    
    def calculate_parking_bill(self, vehicle: Vehicle) -> float:
        """Calculate bill for a parked vehicle"""
        if not vehicle.entry_time:
            return 0.0
        
        exit_time = vehicle.exit_time or datetime.now()
        duration = exit_time - vehicle.entry_time
        hours = max(1, duration.total_seconds() / 3600)  # Minimum 1 hour
        
        rate = self._hourly_rates.get(vehicle.vehicle_type, 10.0)
        return round(hours * rate, 2)
    
    def get_hourly_rate_for_vehicle_type(self, vehicle_type: VehicleType) -> float:
        """Get hourly rate for a specific vehicle type"""
        return self._hourly_rates.get(vehicle_type, 10.0)


# ==================== ENTITY MANAGERS ====================

class ParkingLotManager:
    """Manager for parking lot operations"""
    
    def __init__(self, repository: ParkingLotRepository):
        self.repository = repository
    
    def create_new_parking_lot(self, lot_id: str, name: str, 
                              car_spots: int = 10, motorcycle_spots: int = 5, 
                              truck_spots: int = 3) -> ParkingLot:
        """Create a new parking lot with specified number of spots"""
        parking_lot = ParkingLot(lot_id, name)
        
        # Create spots using factory
        car_spots_list = ParkingSpotFactory.create_parking_spots(VehicleType.CAR, car_spots, 1)
        motorcycle_spots_list = ParkingSpotFactory.create_parking_spots(VehicleType.MOTORCYCLE, motorcycle_spots, 1)
        truck_spots_list = ParkingSpotFactory.create_parking_spots(VehicleType.TRUCK, truck_spots, 1)
        
        # Add all spots to parking lot
        for spot in car_spots_list + motorcycle_spots_list + truck_spots_list:
            parking_lot.add_spot(spot)
        
        self.repository.save_parking_lot(lot_id, parking_lot)
        return parking_lot
    
    def get_parking_lot_by_id(self, lot_id: str) -> Optional[ParkingLot]:
        """Get parking lot by ID"""
        return self.repository.find_parking_lot_by_id(lot_id)
    
    def get_all_parking_lots(self) -> List[ParkingLot]:
        """Get all parking lots"""
        return self.repository.find_all_parking_lots()
    
    def get_parking_lot_by_name(self, name: str) -> Optional[ParkingLot]:
        """Get parking lot by name"""
        return self.repository.find_parking_lot_by_name(name)
    
    def get_parking_lots_by_occupancy(self, min_occupancy: float) -> List[ParkingLot]:
        """Get parking lots with occupancy rate above minimum"""
        return self.repository.find_parking_lots_by_occupancy_rate(min_occupancy)


class VehicleManager:
    """Manager for vehicle operations"""
    
    def __init__(self, repository: VehicleRepository):
        self.repository = repository
    
    def register_new_vehicle(self, license_plate: str, vehicle_type: VehicleType) -> Vehicle:
        """Register a new vehicle"""
        vehicle = Vehicle(license_plate, vehicle_type)
        self.repository.save_vehicle(license_plate, vehicle)
        return vehicle
    
    def get_vehicle_by_license_plate(self, license_plate: str) -> Optional[Vehicle]:
        """Get vehicle by license plate"""
        return self.repository.find_vehicle_by_license_plate(license_plate)
    
    def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        return self.repository.find_all_vehicles()
    
    def get_parked_vehicles(self) -> List[Vehicle]:
        """Get all currently parked vehicles"""
        return self.repository.find_parked_vehicles()
    
    def get_vehicles_by_type(self, vehicle_type: VehicleType) -> List[Vehicle]:
        """Get all vehicles of a specific type"""
        return self.repository.find_vehicles_by_type(vehicle_type)


# ==================== SYSTEM ORCHESTRATOR ====================

class ParkingLotSystem:
    """Main system orchestrator for parking lot operations"""
    
    def __init__(self):
        self.parking_lot_repo = InMemoryParkingLotRepository()
        self.vehicle_repo = InMemoryVehicleRepository()
        self.parking_lot_manager = ParkingLotManager(self.parking_lot_repo)
        self.vehicle_manager = VehicleManager(self.vehicle_repo)
        self.billing_service = BillingService()
    
    def create_parking_lot(self, lot_id: str, name: str, 
                          car_spots: int = 10, motorcycle_spots: int = 5, 
                          truck_spots: int = 3) -> ParkingLot:
        """Create a new parking lot"""
        return self.parking_lot_manager.create_new_parking_lot(lot_id, name, car_spots, motorcycle_spots, truck_spots)
    
    def park_vehicle(self, lot_id: str, license_plate: str, vehicle_type: VehicleType) -> bool:
        """Park a vehicle in the specified parking lot"""
        parking_lot = self.parking_lot_manager.get_parking_lot_by_id(lot_id)
        if not parking_lot:
            return False
        
        # Get or create vehicle
        vehicle = self.vehicle_manager.get_vehicle_by_license_plate(license_plate)
        if not vehicle:
            vehicle = self.vehicle_manager.register_new_vehicle(license_plate, vehicle_type)
        
        # Find available spot
        available_spots = parking_lot.get_available_spots(vehicle_type)
        if not available_spots:
            return False
        
        # Park in first available spot
        spot = available_spots[0]
        success = spot.park_vehicle(vehicle)
        
        if success:
            parking_lot.vehicles[license_plate] = vehicle
            self.parking_lot_repo.save_parking_lot(lot_id, parking_lot)
        
        return success
    
    def unpark_vehicle(self, lot_id: str, license_plate: str) -> bool:
        """Unpark a vehicle from the specified parking lot"""
        parking_lot = self.parking_lot_manager.get_parking_lot_by_id(lot_id)
        if not parking_lot:
            return False
        
        vehicle = parking_lot.vehicles.get(license_plate)
        if not vehicle or not vehicle.parking_spot_id:
            return False
        
        spot = parking_lot.spots.get(vehicle.parking_spot_id)
        if not spot:
            return False
        
        unparked_vehicle = spot.unpark_vehicle()
        if unparked_vehicle:
            del parking_lot.vehicles[license_plate]
            self.parking_lot_repo.save_parking_lot(lot_id, parking_lot)
            return True
        
        return False
    
    def get_parking_lot_status(self, lot_id: str) -> Optional[Dict]:
        """Get status of a parking lot"""
        parking_lot = self.parking_lot_manager.get_parking_lot_by_id(lot_id)
        if not parking_lot:
            return None
        
        total_spots = len(parking_lot.spots)
        occupied_spots = len(parking_lot.get_occupied_spots())
        
        return {
            "lot_id": lot_id,
            "name": parking_lot.name,
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "available_spots": total_spots - occupied_spots,
            "occupancy_rate": round((occupied_spots / total_spots) * 100, 2) if total_spots > 0 else 0
        }
    
    def get_vehicle_status(self, license_plate: str) -> Optional[Dict]:
        """Get status of a specific vehicle"""
        vehicle = self.vehicle_manager.get_vehicle_by_license_plate(license_plate)
        if not vehicle:
            return None
        
        return {
            "license_plate": vehicle.license_plate,
            "vehicle_type": vehicle.vehicle_type.value,
            "is_parked": vehicle.parking_spot_id is not None,
            "parking_spot_id": vehicle.parking_spot_id,
            "entry_time": vehicle.entry_time.isoformat() if vehicle.entry_time else None,
            "exit_time": vehicle.exit_time.isoformat() if vehicle.exit_time else None
        }
    
    def get_all_vehicles_status(self) -> List[Dict]:
        """Get status of all vehicles"""
        vehicles = self.vehicle_manager.get_all_vehicles()
        return [self.get_vehicle_status(vehicle.license_plate) for vehicle in vehicles]
    
    def get_vehicle_bill(self, license_plate: str) -> Optional[Dict]:
        """Get bill for a specific vehicle"""
        vehicle = self.vehicle_manager.get_vehicle_by_license_plate(license_plate)
        if not vehicle:
            return None
        
        bill_amount = self.billing_service.calculate_parking_bill(vehicle)
        
        return {
            "license_plate": vehicle.license_plate,
            "vehicle_type": vehicle.vehicle_type.value,
            "entry_time": vehicle.entry_time.isoformat() if vehicle.entry_time else None,
            "exit_time": vehicle.exit_time.isoformat() if vehicle.exit_time else None,
            "bill_amount": bill_amount,
            "is_parked": vehicle.parking_spot_id is not None
        }
    
    def get_parked_vehicles_status(self) -> List[Dict]:
        """Get status of all currently parked vehicles"""
        parked_vehicles = self.vehicle_manager.get_parked_vehicles()
        return [self.get_vehicle_status(vehicle.license_plate) for vehicle in parked_vehicles]


# ==================== USAGE EXAMPLE ====================

def main():
    """Example usage of the parking lot system"""
    # Create parking lot system
    system = ParkingLotSystem()
    
    # Create a parking lot
    parking_lot = system.create_parking_lot("PL001", "Downtown Parking", car_spots=5, motorcycle_spots=3, truck_spots=2)
    print(f"Created: {parking_lot}")
    
    # Park some vehicles
    print("\n--- Parking Vehicles ---")
    system.park_vehicle("PL001", "ABC123", VehicleType.CAR)
    system.park_vehicle("PL001", "XYZ789", VehicleType.MOTORCYCLE)
    system.park_vehicle("PL001", "TRUCK1", VehicleType.TRUCK)
    
    # Get parking lot status
    print("\n--- Parking Lot Status ---")
    status = system.get_parking_lot_status("PL001")
    print(f"Status: {status}")
    
    # Get vehicle status
    print("\n--- Vehicle Status ---")
    vehicle_status = system.get_vehicle_status("ABC123")
    print(f"Vehicle ABC123: {vehicle_status}")
    
    # Get all vehicles status
    print("\n--- All Vehicles Status ---")
    all_vehicles = system.get_all_vehicles_status()
    for vehicle in all_vehicles:
        print(f"Vehicle: {vehicle}")
    
    # Get parked vehicles status
    print("\n--- Parked Vehicles Status ---")
    parked_vehicles = system.get_parked_vehicles_status()
    for vehicle in parked_vehicles:
        print(f"Parked Vehicle: {vehicle}")
    
    # Get bill for a vehicle
    print("\n--- Vehicle Bill ---")
    bill = system.get_vehicle_bill("ABC123")
    print(f"Bill for ABC123: {bill}")
    
    # Unpark a vehicle
    print("\n--- Unparking Vehicle ---")
    system.unpark_vehicle("PL001", "ABC123")
    
    # Get updated status
    print("\n--- Updated Parking Lot Status ---")
    updated_status = system.get_parking_lot_status("PL001")
    print(f"Updated Status: {updated_status}")


if __name__ == "__main__":
    main()