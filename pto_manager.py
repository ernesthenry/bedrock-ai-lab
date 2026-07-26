"""
PTO (Paid Time Off) Management Module
Handles employee PTO balance queries and time off requests
"""

from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class PTOManager:
    """Manages employee PTO balances and requests."""
    
    def __init__(self):
        # In production, this would connect to a database
        # For now, using in-memory storage with sample data
        self.pto_database = {
            '123': 35,
            '456': 25,
            '789': 20,
        }
        self.employee_names = {
            '123': 'John Doe',
            '456': 'Jane Smith', 
            '789': 'Bob Johnson',
        }
    
    def get_pto_balance(self, employee_id: str) -> Dict:
        """
        Get PTO balance for an employee.
        
        Args:
            employee_id: Unique employee identifier
            
        Returns:
            Dict with employee_id, pto_balance, and employee_name
        """
        balance = self.pto_database.get(employee_id, -1)
        employee_name = self.employee_names.get(employee_id, "Unknown")
        
        if balance == -1:
            return {
                "error": "Invalid employee ID",
                "employee_id": employee_id,
                "pto_balance": None
            }
        
        return {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "pto_balance": balance
        }
    
    def request_pto(self, employee_id: str, pto_days: int) -> Dict:
        """
        Process a PTO request for an employee.
        
        Args:
            employee_id: Unique employee identifier
            pto_days: Number of PTO days to request
            
        Returns:
            Dict with updated balance and status
        """
        current_balance = self.get_pto_balance(employee_id)
        
        if "error" in current_balance:
            return current_balance
        
        if pto_days <= 0:
            return {
                "error": "PTO days must be greater than 0",
                "employee_id": employee_id,
                "pto_balance": current_balance["pto_balance"]
            }
        
        if pto_days > current_balance["pto_balance"]:
            return {
                "error": f"Insufficient PTO balance. Requested: {pto_days}, Available: {current_balance['pto_balance']}",
                "employee_id": employee_id,
                "pto_balance": current_balance["pto_balance"]
            }
        
        # Update the balance
        new_balance = current_balance["pto_balance"] - pto_days
        self.pto_database[employee_id] = new_balance
        
        return {
            "employee_id": employee_id,
            "employee_name": current_balance["employee_name"],
            "pto_requested": pto_days,
            "pto_remaining": new_balance,
            "status": "approved"
        }
    
    def add_employee(self, employee_id: str, name: str, initial_pto: int) -> Dict:
        """
        Add a new employee to the PTO system.
        
        Args:
            employee_id: Unique employee identifier
            name: Employee name
            initial_pto: Initial PTO balance
            
        Returns:
            Dict with status
        """
        if employee_id in self.pto_database:
            return {
                "error": "Employee ID already exists",
                "employee_id": employee_id
            }
        
        self.pto_database[employee_id] = initial_pto
        self.employee_names[employee_id] = name
        
        return {
            "employee_id": employee_id,
            "employee_name": name,
            "initial_pto": initial_pto,
            "status": "created"
        }
    
    def list_employees(self) -> Dict:
        """
        List all employees with their PTO balances.
        
        Returns:
            Dict with list of employees
        """
        employees = []
        for emp_id, balance in self.pto_database.items():
            employees.append({
                "employee_id": emp_id,
                "employee_name": self.employee_names.get(emp_id, "Unknown"),
                "pto_balance": balance
            })
        
        return {
            "employees": employees,
            "total_count": len(employees)
        }


# Global instance
pto_manager = PTOManager()
