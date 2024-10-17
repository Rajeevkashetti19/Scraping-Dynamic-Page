import pandas as pd
from collections import defaultdict
import random

class Employee:
    def __init__(self, name, direct_manager, middle_manager, top_manager, city):
        self.name = name
        self.direct_manager = direct_manager
        self.middle_manager = middle_manager
        self.top_manager = top_manager
        self.managers = {direct_manager, middle_manager, top_manager}
        self.city = city
        self.time_zone = get_time_zone(city)

def get_time_zone(city):
    # Placeholder function, replace with actual implementation
    time_zones = {
        'New York': 'ET', 'Chicago': 'CT', 'Denver': 'MT', 'Los Angeles': 'PT',
        'London': 'GMT', 'Paris': 'CET', 'Tokyo': 'JST', 'Sydney': 'AEST'
    }
    return time_zones.get(city, 'Unknown')

def load_data(file_path):
    df = pd.read_excel(file_path)
    employees = {}
    for _, row in df.iterrows():
        emp = Employee(row['Employee'], row['Direct Manager'], row['Middle Manager'], 
                       row['Top Manager'], row['City'])
        employees[emp.name] = emp
    return employees

def create_groups(employees, min_group_size=3, max_group_size=5):
    groups = []
    city_employees = defaultdict(list)
    time_zone_employees = defaultdict(list)
    
    # O(n) - Partition employees by city and time zone
    for emp in employees.values():
        city_employees[emp.city].append(emp)
        time_zone_employees[emp.time_zone].append(emp)
    
    def try_add_to_group(emp, group):
        if (emp.direct_manager not in {e.direct_manager for e in group} and
            not any(emp.name in e.managers or e.name in emp.managers for e in group)):
            group.append(emp)
            return True
        return False
    
    def create_group_from_pool(pool):
        group = []
        random.shuffle(pool)  # Randomize to avoid bias towards certain employees
        for emp in pool[:]:
            if try_add_to_group(emp, group):
                pool.remove(emp)
                if len(group) == max_group_size:
                    break
        return group if len(group) >= min_group_size else []
    
    # O(n) - Try to create groups from each city
    for city_pool in city_employees.values():
        while len(city_pool) >= min_group_size:
            group = create_group_from_pool(city_pool)
            if group:
                groups.append(group)
            else:
                break
    
    # O(n) - Try to create groups from each time zone with remaining employees
    for tz_pool in time_zone_employees.values():
        tz_pool = [emp for emp in tz_pool if not any(emp in group for group in groups)]
        while len(tz_pool) >= min_group_size:
            group = create_group_from_pool(tz_pool)
            if group:
                groups.append(group)
            else:
                break
    
    return groups

def main():
    file_path = 'employees.xlsx'  # Replace with your Excel file path
    employees = load_data(file_path)
    groups = create_groups(employees)
    
    print("Employee Groups:")
    for i, group in enumerate(groups, 1):
        print(f"Group {i} (City: {group[0].city}, Manager: {group[0].direct_manager}):")
        for emp in group:
            print(f"  - {emp.name} (Manager: {emp.direct_manager})")
        print()

if __name__ == "__main__":
    main()