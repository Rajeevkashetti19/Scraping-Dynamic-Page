import pandas as pd
from collections import defaultdict
from typing import List, Dict, Set, Tuple

class Employee:
    def __init__(self, id: str, grade: str, manager: str, business: str, city: str):
        self.id = id
        self.grade = grade
        self.manager = manager
        self.business = business
        self.city = city
        self.team = set()  # Will store all team members (including those up the management chain)

def build_team_hierarchy(employees: List[Employee]) -> None:
    manager_map = {emp.id: emp for emp in employees}
    for emp in employees:
        current = emp
        while current.manager in manager_map:
            emp.team.add(current.manager)
            current = manager_map[current.manager]

def group_employees(df: pd.DataFrame) -> List[List[str]]:
    employees = [Employee(row['EmployeeID'], row['Grade'], row['Manager'], row['Business'], row['City']) 
                 for _, row in df.iterrows()]
    
    build_team_hierarchy(employees)
    
    # Separate C15/C16 employees and others
    high_grade = [emp for emp in employees if emp.grade in ['C15', 'C16']]
    others = [emp for emp in employees if emp.grade not in ['C15', 'C16']]
    
    # Create indexes for fast lookup
    city_business_index = defaultdict(lambda: defaultdict(list))
    for emp in others:
        city_business_index[emp.city][emp.business].append(emp)
    
    groups = []
    used = set()

    def find_compatible_employees(leader: Employee, num_needed: int) -> List[Employee]:
        compatible = []
        for business, emps in city_business_index[leader.city].items():
            if business != leader.business:
                for emp in emps:
                    if emp.id not in used and emp.id not in leader.team and leader.id not in emp.team:
                        compatible.append(emp)
                        if len(compatible) == num_needed:
                            return compatible
        return compatible

    # Create groups
    for leader in high_grade:
        group = [leader]
        matches = find_compatible_employees(leader, 3)  # Try to find 3 compatible employees
        if len(matches) >= 2:  # Ensure we have at least 2 matches
            group.extend(matches[:3])  # Take up to 3 matches
            groups.append([emp.id for emp in group])
            used.update(emp.id for emp in group)
    
    return groups

# Example usage:
# df = pd.read_excel('employee_data.xlsx')
# groups = group_employees(df)
# for i, group in enumerate(groups, 1):
#     print(f"Group {i}: {group}")




def group_employees(df: pd.DataFrame) -> Tuple[List[List[str]], Dict[str, str]]:
    employees = [Employee(row['EmployeeID'], row['Grade'], row['Manager'], row['Business'], row['City']) 
                 for _, row in df.iterrows()]
    
    build_team_hierarchy(employees)
    
    high_grade = [emp for emp in employees if emp.grade in ['C15', 'C16']]
    others = [emp for emp in employees if emp.grade not in ['C15', 'C16']]
    
    city_business_index = defaultdict(lambda: defaultdict(list))
    for emp in others:
        city_business_index[emp.city][emp.business].append(emp)
    
    groups = []
    used = set()
    ungrouped_reasons = {}

    def find_compatible_employees(leader: Employee) -> List[Employee]:
        compatible = []
        same_city_count = 0
        same_business_count = 0
        same_team_count = 0
        for business, emps in city_business_index[leader.city].items():
            same_city_count += len(emps)
            if business != leader.business:
                for emp in emps:
                    if emp.id not in used:
                        if emp.id not in leader.team and leader.id not in emp.team:
                            compatible.append(emp)
                            if len(compatible) == 3:
                                return compatible, ""
                        else:
                            same_team_count += 1
            else:
                same_business_count += len(emps)
        
        reason = ""
        if len(compatible) < 2:
            if same_city_count == 0:
                reason = f"No other employees in the same city ({leader.city})"
            elif same_business_count == same_city_count:
                reason = f"All potential matches in the same business ({leader.business})"
            elif same_team_count == same_city_count - same_business_count:
                reason = "All potential matches in the same team hierarchy"
            else:
                reason = f"Not enough compatible employees (found {len(compatible)}, need at least 2)"
        
        return compatible, reason

    for leader in high_grade:
        matches, reason = find_compatible_employees(leader)
        if len(matches) >= 2:
            group = [leader] + matches[:3]  # Take up to 3 matches
            groups.append([emp.id for emp in group])
            used.update(emp.id for emp in group)
        else:
            ungrouped_reasons[leader.id] = reason

    return groups, ungrouped_reasons

# Usage:
df = pd.read_excel('employee_data.xlsx')
groups, ungrouped_reasons = group_employees(df)

print(f"Total C15/C16 employees: {len([emp for emp in df[df['Grade'].isin(['C15', 'C16'])]['EmployeeID'].unique()])}")
print(f"Number of groups formed: {len(groups)}")
print(f"Number of ungrouped C15/C16 employees: {len(ungrouped_reasons)}")
print("\nUngrouped C15/C16 employees and reasons:")
for emp_id, reason in ungrouped_reasons.items():
    emp = df[df['EmployeeID'] == emp_id].iloc[0]
    print(f"ID: {emp_id}, Grade: {emp['Grade']}, Business: {emp['Business']}, City: {emp['City']}")
    print(f"Reason: {reason}\n")