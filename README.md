Employee Shift Scheduling Application
Overview

This project implements a weekly employee scheduling system for a company that operates 7 days a week with three daily shifts:

Morning

Afternoon

Evening

The application allows employees to specify preferred shifts for each day, optionally with priority rankings, and automatically generates a valid weekly schedule while enforcing company and labor constraints.

The system is implemented in two languages:

Python (CLI-based)

C++ (C++17) (CLI-based)

This project demonstrates the use of control structures, data structures, conflict resolution, and randomized decision-making in multiple programming languages.

Features
Core Functionality

Collects employee names and shift preferences for each day of the week

Automatically generates a weekly schedule

Outputs a readable final schedule

Enforces all scheduling constraints

Scheduling Rules

✔ No employee works more than one shift per day
✔ No employee works more than 5 days per week
✔ Each shift must have at least 2 employees per day
✔ Shift conflicts are detected and resolved automatically
✔ Employees are reassigned fairly when shortages occur

Bonus Features (Implemented)

⭐ Ranked shift preferences (e.g., Morning → Evening → Afternoon)
⭐ Conflict resolution across same day or next available day
⭐ Randomized assignment when minimum staffing is not met

Shift Definitions
Code	Shift Name
M	Morning
A	Afternoon
E	Evening
Input Format
Employee Data

For each employee, the program collects:

Employee name

Shift preferences for each day of the week

Preferences are entered as comma-separated ranked choices:

Example:

M,E,A


Meaning:

Morning (highest priority)

Evening

Afternoon

If only one shift is entered (e.g., M), the system treats it as the top preference but allows fallback shifts if needed.

If no valid input is provided, the system defaults to:

M,A,E

Scheduling Logic (How It Works)
1. Preference Assignment Phase

Employees are processed day by day

For each day:

Employees are shuffled to avoid bias

Each employee attempts to get their highest-ranked available shift

A shift is treated as “full” once it reaches 2 employees

If a preferred shift is full:

The system tries another shift on the same day

If unavailable, it attempts assignment on the next day

2. Minimum Staffing Enforcement

After preference assignment:

The system checks every day and shift

If a shift has fewer than 2 employees:

Randomly assigns eligible employees who:

Have not worked that day

Have worked fewer than 5 days total

3. Conflict Resolution

Conflicts occur when:

An employee’s preferred shift is already full

The employee has reached 5 working days

The employee already has a shift that day

Resolution strategy:

Try alternate shifts on the same day

Try the next available day

Skip employee if no valid placement exists

Output Format
Weekly Schedule

The final schedule is printed in a readable format:

FINAL WEEK SCHEDULE
============================================================

Mon:
  Morning   : Alice, Bob
  Afternoon : Carol, Dave
  Evening   : Eve, Frank

Tue:
  Morning   : Bob, Carol
  Afternoon : Alice, Eve
  Evening   : Dave, Frank

Employee Summary

A per-employee breakdown is also printed:

EMPLOYEE SUMMARY
============================================================
Alice: 5 day(s) -> Mon, Tue, Wed, Thu, Fri
Bob: 4 day(s) -> Mon, Tue, Thu, Sat


This confirms:

Days worked

Weekly workload limits are respected

Python Implementation
Requirements

Python 3.9+

No external libraries required

Running the Program
python schedule.py

File
schedule.py

Key Python Concepts Used

Dictionaries and lists

dataclass

Control structures (if, while, for)

Randomized selection (random)

Functions and modular design

C++ Implementation
Requirements

C++ 17 or newer

Standard library only

Compile & Run
g++ -std=c++17 schedule.cpp -o schedule
./schedule

File
schedule.cpp

Key C++ Concepts Used

Structs and vectors

Maps and hash tables

Random number generation (<random>)

Input/output streams

Control flow and modular functions

Assumptions & Limitations

The system assumes enough employees exist to reasonably satisfy staffing requirements
(7 days × 3 shifts × 2 employees = 42 total assignments)

If staffing is insufficient, the program fills as many shifts as possible

No maximum shift capacity is enforced (only minimum)

Scheduling is non-persistent (no file storage)

Possible Extensions

Graphical User Interface (GUI)

Python: Tkinter / PyQt

C++: Qt

Export schedule to CSV or JSON

Maximum employees per shift

Shift fairness metrics

Overtime tracking

Vacation or unavailable days

Educational Objectives

This project demonstrates:

Practical use of control structures

Real-world constraint-based scheduling

Cross-language problem solving

Data structure design

Conflict detection and resolution

Randomized algorithms

Author / Usage

This project is suitable for:

Programming assignments

Demonstrations of scheduling algorithms

Comparing Python and C++ implementations

Control-structure coursework

You are free to modify or extend this project for educational purposes.
