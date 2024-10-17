import pandas as pd
from collections import defaultdict
from typing import List, Dict, Set

class Employee:
    def __init__(self, id: str, grade: str, manager: str, business: str, city: str):
        self.id = id
        self.grade = grade
        self.manager = manager
        self.business = business
        self.city = city

def create_groups(df: pd.DataFrame) -> List[List[str]]:
    employees = [Employee(row['EmployeeID'], row['Grade'], row['Manager'], row['Business'], row['City']) 
                 for _, row in df.iterrows()]
    
    # Sort employees by grade (C15/C16 first, then others)
    employees.sort(key=lambda e: (e.grade not in ['C15', 'C16'], e.grade))
    
    # Create indexes for fast lookup
    city_index = defaultdict(list)
    for emp in employees:
        city_index[emp.city].append(emp)
    
    groups = []
    used = set()

    def is_compatible(group: List[Employee], candidate: Employee) -> bool:
        return all(
            candidate.manager != emp.manager and
            candidate.business != emp.business and
            candidate.city == emp.city
            for emp in group
        )

    def find_matches(leader: Employee, num_needed: int) -> List[Employee]:
        candidates = city_index[leader.city]
        matches = []
        for candidate in candidates:
            if (candidate.id not in used and 
                candidate.id != leader.id and
                candidate.grade <= 'C14' and
                is_compatible([leader] + matches, candidate)):
                matches.append(candidate)
                if len(matches) == num_needed:
                    break
        return matches

    # Create initial groups
    for emp in employees:
        if emp.id not in used and emp.grade in ['C15', 'C16']:
            group = [emp]
            matches = find_matches(emp, 2)
            group.extend(matches)
            if len(group) >= 3:
                groups.append([e.id for e in group])
                used.update(e.id for e in group)

    # Handle remaining employees
    remaining = [emp for emp in employees if emp.id not in used]
    for emp in remaining:
        added = False
        for group in groups:
            group_employees = [next(e for e in employees if e.id == id) for id in group]
            if len(group) < 4 and is_compatible(group_employees, emp):
                group.append(emp.id)
                used.add(emp.id)
                added = True
                break
        if not added:
            groups.append([emp.id])
            used.add(emp.id)

    # Attempt to merge small groups
    small_groups = [g for g in groups if len(g) < 3]
    for group in small_groups:
        groups.remove(group)
        group_employees = [next(e for e in employees if e.id == id) for id in group]
        for other_group in groups:
            other_employees = [next(e for e in employees if e.id == id) for id in other_group]
            if all(is_compatible(other_employees, emp) for emp in group_employees):
                other_group.extend(group)
                break
        else:
            groups.append(group)  # If no merge possible, add back to groups

    return groups

# Example usage:
# df = pd.read_excel('employee_data.xlsx')
# groups = create_groups(df)
# for i, group in enumerate(groups, 1):
#     print(f"Group {i}: {group}")