import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SHIFTS = ["M", "A", "E"]  # Morning, Afternoon, Evening

SHIFT_NAME = {"M": "Morning", "A": "Afternoon", "E": "Evening"}


@dataclass
class Employee:
    name: str
    # prefs[day] = ranked list like ["M","E","A"]
    prefs: Dict[str, List[str]]
    days_worked: int = 0
    assigned_by_day: Dict[str, Optional[str]] = field(default_factory=dict)  # day -> shift or None


def parse_pref_line(line: str) -> List[str]:
    """
    Input examples:
      M
      M,E,A
      A,M
    Returns cleaned ranked list subset of SHIFTS. If empty, returns default ["M","A","E"].
    """
    parts = [p.strip().upper() for p in line.split(",") if p.strip()]
    ranked = [p for p in parts if p in SHIFTS]
    # If user gave only 1 valid shift, keep it as first pref but allow others as fallback:
    if len(ranked) == 1:
        for s in SHIFTS:
            if s not in ranked:
                ranked.append(s)
    if not ranked:
        ranked = SHIFTS[:]  # default
    # remove duplicates while preserving order
    seen = set()
    out = []
    for s in ranked:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def collect_input() -> List[Employee]:
    employees: List[Employee] = []
    n = int(input("Number of employees: ").strip())
    for i in range(n):
        name = input(f"Employee {i+1} name: ").strip()
        prefs: Dict[str, List[str]] = {}
        print("Enter preferences for each day as ranked shifts (comma-separated). Example: M,E,A")
        for d in DAYS:
            line = input(f"  {d}: ").strip()
            prefs[d] = parse_pref_line(line)
        emp = Employee(name=name, prefs=prefs)
        emp.assigned_by_day = {d: None for d in DAYS}
        employees.append(emp)
    return employees


def is_employee_free(emp: Employee, day: str) -> bool:
    return emp.assigned_by_day.get(day) is None


def can_work_more(emp: Employee) -> bool:
    return emp.days_worked < 5


def try_assign(
    schedule: Dict[str, Dict[str, List[str]]],
    emp: Employee,
    day_idx: int,
    preferred_only_until_full: bool = True
) -> bool:
    """
    Try to assign employee starting at day_idx.
    Conflict resolution:
      - Try ranked shifts on same day (only if shift not "full" (2) while preference pass)
      - Else try any shift same day
      - Else try next day (recursive/iterative)
    Returns True if assigned somewhere.
    """
    if not can_work_more(emp):
        return False

    for di in range(day_idx, len(DAYS)):
        day = DAYS[di]
        if not is_employee_free(emp, day):
            continue

        ranked = emp.prefs.get(day, SHIFTS[:])
        # 1) Try ranked preferences
        for s in ranked:
            if preferred_only_until_full:
                # treat "full" as having met minimum requirement (2) during preference placement
                if len(schedule[day][s]) >= 2:
                    continue
            # ensure no more than one shift/day already satisfied by is_employee_free
            schedule[day][s].append(emp.name)
            emp.assigned_by_day[day] = s
            emp.days_worked += 1
            return True

        # 2) If conflict (all ranked full), try any shift same day that isn't full (or any shift)
        for s in SHIFTS:
            if preferred_only_until_full and len(schedule[day][s]) >= 2:
                continue
            schedule[day][s].append(emp.name)
            emp.assigned_by_day[day] = s
            emp.days_worked += 1
            return True

        # 3) Otherwise push to next day (loop continues)

    return False


def fill_minimums(
    rng: random.Random,
    schedule: Dict[str, Dict[str, List[str]]],
    employees: List[Employee]
) -> None:
    """
    Ensure >=2 employees per shift per day by randomly assigning eligible employees:
      - not assigned that day
      - days_worked < 5
    """
    for day in DAYS:
        for shift in SHIFTS:
            while len(schedule[day][shift]) < 2:
                eligible = [
                    e for e in employees
                    if can_work_more(e) and is_employee_free(e, day)
                ]
                if not eligible:
                    # Can't satisfy requirement if nobody eligible
                    break
                chosen = rng.choice(eligible)
                schedule[day][shift].append(chosen.name)
                chosen.assigned_by_day[day] = shift
                chosen.days_worked += 1


def build_schedule(employees: List[Employee], seed: int = 42) -> Dict[str, Dict[str, List[str]]]:
    rng = random.Random(seed)
    schedule: Dict[str, Dict[str, List[str]]] = {
        d: {s: [] for s in SHIFTS} for d in DAYS
    }

    # Preference pass: try to place everyone respecting ranked preferences,
    # while treating a shift as "full" once it hits 2 (so conflicts occur).
    # This helps distribute and triggers conflict resolution logic.
    for day_idx, day in enumerate(DAYS):
        # shuffle to reduce bias each day
        day_emps = employees[:]
        rng.shuffle(day_emps)
        for emp in day_emps:
            if not can_work_more(emp):
                continue
            if not is_employee_free(emp, day):
                continue
            # Try assign today; if conflicts, it may push to next day
            try_assign(schedule, emp, day_idx, preferred_only_until_full=True)

    # Fill shortages to ensure >=2 per shift/day (random eligible employees)
    fill_minimums(rng, schedule, employees)

    return schedule


def print_schedule(schedule: Dict[str, Dict[str, List[str]]]) -> None:
    print("\nFINAL WEEK SCHEDULE\n" + "=" * 60)
    for d in DAYS:
        print(f"\n{d}:")
        for s in SHIFTS:
            names = schedule[d][s]
            pretty_shift = SHIFT_NAME[s]
            if names:
                print(f"  {pretty_shift:<10}: {', '.join(names)}")
            else:
                print(f"  {pretty_shift:<10}: (none)")


def print_employee_summary(employees: List[Employee]) -> None:
    print("\nEMPLOYEE SUMMARY\n" + "=" * 60)
    for e in employees:
        worked_days = [d for d in DAYS if e.assigned_by_day[d] is not None]
        print(f"{e.name}: {e.days_worked} day(s) -> {worked_days}")


def main():
    employees = collect_input()
    schedule = build_schedule(employees, seed=42)
    print_schedule(schedule)
    print_employee_summary(employees)


if __name__ == "__main__":
    main()
