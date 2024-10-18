import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
from collections import defaultdict
import time

class Employee:
    def __init__(self, id: str, grade: str, manager: str, business: str, city: str):
        self.id = id
        self.grade = grade
        self.manager = manager
        self.business = business
        self.city = city
        self.team = set()

def build_team_hierarchy(employees: List[Employee]) -> None:
    emp_dict = {emp.id: emp for emp in employees}
    for emp in employees:
        current = emp
        while current.manager and current.manager in emp_dict:
            emp_dict[current.manager].team.add(emp.id)
            current = emp_dict[current.manager]

def group_by_business_and_grade(df: pd.DataFrame, min_group: int, max_group: int) -> List[List[str]]:
    groups = []
    for business in df['Business'].unique():
        business_df = df[df['Business'] == business]
        for grade in business_df['Grade'].unique():
            grade_df = business_df[business_df['Grade'] == grade]
            employee_ids = grade_df['EmployeeID'].tolist()
            while len(employee_ids) >= min_group:
                group = employee_ids[:max_group]
                groups.append(group)
                employee_ids = employee_ids[max_group:]
    return groups

def group_by_city_and_grade(df: pd.DataFrame, min_group: int, max_group: int) -> List[List[str]]:
    groups = []
    for city in df['City'].unique():
        city_df = df[df['City'] == city]
        for grade in city_df['Grade'].unique():
            grade_df = city_df[city_df['Grade'] == grade]
            employee_ids = grade_df['EmployeeID'].tolist()
            while len(employee_ids) >= min_group:
                group = employee_ids[:max_group]
                groups.append(group)
                employee_ids = employee_ids[max_group:]
    return groups

def group_employees_complex(df: pd.DataFrame, min_group: int, max_group: int) -> Tuple[List[List[str]], Dict[str, str]]:
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

    def find_compatible_employees(leader: Employee) -> Tuple[List[Employee], str]:
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
                            if len(compatible) == max_group - 1:
                                return compatible, ""
                        else:
                            same_team_count += 1
            else:
                same_business_count += len(emps)
        
        reason = ""
        if len(compatible) < min_group - 1:
            if same_city_count == 0:
                reason = f"No other employees in the same city ({leader.city})"
            elif same_business_count == same_city_count:
                reason = f"All potential matches in the same business ({leader.business})"
            elif same_team_count == same_city_count - same_business_count:
                reason = "All potential matches in the same team hierarchy"
            else:
                reason = f"Not enough compatible employees (found {len(compatible)}, need at least {min_group - 1})"
        
        return compatible, reason

    for leader in high_grade:
        matches, reason = find_compatible_employees(leader)
        if len(matches) >= min_group - 1:
            group = [leader] + matches[:max_group - 1]
            groups.append([emp.id for emp in group])
            used.update(emp.id for emp in group)
        else:
            ungrouped_reasons[leader.id] = reason

    return groups, ungrouped_reasons

def main():
    st.title("Employee Grouping Application")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        progress_text = st.empty()
        progress_bar = st.progress(0)

        progress_text.text("Loading data...")
        progress_bar.progress(10)
        time.sleep(0.5)

        df = pd.read_excel(uploaded_file)
        
        progress_text.text("Data loaded successfully!")
        progress_bar.progress(30)
        time.sleep(0.5)

        st.write("Data Preview:")
        st.dataframe(df.head())

        grouping_options = st.multiselect(
            "Select grouping method(s)",
            ["Group by Business and Grade", "Group by City and Grade", "Complex Grouping (C15/C16 leaders)"],
            default=["Group by Business and Grade"]
        )

        min_group = st.number_input("Minimum group size", min_value=2, max_value=10, value=3)
        max_group = st.number_input("Maximum group size", min_value=min_group, max_value=10, value=4)

        if st.button("Generate Groups"):
            for option in grouping_options:
                progress_text.text(f"Generating groups using {option}...")
                progress_bar.progress(50)
                time.sleep(0.5)

                if option == "Group by Business and Grade":
                    groups = group_by_business_and_grade(df, min_group, max_group)
                    st.subheader("Groups by Business and Grade")
                    for i, group in enumerate(groups, 1):
                        st.write(f"Group {i}: {', '.join(group)}")
                
                elif option == "Group by City and Grade":
                    groups = group_by_city_and_grade(df, min_group, max_group)
                    st.subheader("Groups by City and Grade")
                    for i, group in enumerate(groups, 1):
                        st.write(f"Group {i}: {', '.join(group)}")
                
                elif option == "Complex Grouping (C15/C16 leaders)":
                    groups, ungrouped_reasons = group_employees_complex(df, min_group, max_group)
                    st.subheader("Complex Grouping (C15/C16 leaders)")
                    for i, group in enumerate(groups, 1):
                        st.write(f"Group {i}: {', '.join(group)}")
                    
                    st.subheader("Ungrouped C15/C16 employees and reasons:")
                    for emp_id, reason in ungrouped_reasons.items():
                        emp = df[df['EmployeeID'] == emp_id].iloc[0]
                        st.text_area(f"Employee ID: {emp_id}", 
                                     f"Grade: {emp['Grade']}, Business: {emp['Business']}, City: {emp['City']}\nReason: {reason}",
                                     height=100)

                progress_bar.progress(90)
                time.sleep(0.5)

            progress_text.text("Grouping complete!")
            progress_bar.progress(100)

if __name__ == "__main__":
    main()