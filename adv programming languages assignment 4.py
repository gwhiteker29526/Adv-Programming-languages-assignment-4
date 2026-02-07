#include <algorithm>
#include <cctype>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

static const std::vector<std::string> DAYS = {"Mon","Tue","Wed","Thu","Fri","Sat","Sun"};
static const std::vector<std::string> SHIFTS = {"M","A","E"}; // Morning, Afternoon, Evening

static std::string shiftName(const std::string& s) {
    if (s == "M") return "Morning";
    if (s == "A") return "Afternoon";
    return "Evening";
}

static std::string upperTrim(std::string x) {
    // trim
    auto notSpace = [](unsigned char ch){ return !std::isspace(ch); };
    x.erase(x.begin(), std::find_if(x.begin(), x.end(), notSpace));
    x.erase(std::find_if(x.rbegin(), x.rend(), notSpace).base(), x.end());
    // upper
    for (char& c : x) c = (char)std::toupper((unsigned char)c);
    return x;
}

static std::vector<std::string> splitPrefs(const std::string& line) {
    std::vector<std::string> parts;
    std::string cur;
    for (char c : line) {
        if (c == ',') {
            parts.push_back(upperTrim(cur));
            cur.clear();
        } else cur.push_back(c);
    }
    parts.push_back(upperTrim(cur));
    // filter valid shifts
    std::vector<std::string> ranked;
    for (auto &p : parts) {
        if (p == "M" || p == "A" || p == "E") ranked.push_back(p);
    }
    // If only one valid shift given, add other shifts as fallback
    if (ranked.size() == 1) {
        for (auto &s : SHIFTS) {
            if (s != ranked[0]) ranked.push_back(s);
        }
    }
    if (ranked.empty()) ranked = SHIFTS;

    // remove duplicates preserve order
    std::vector<std::string> out;
    std::unordered_map<std::string, bool> seen;
    for (auto &s : ranked) {
        if (!seen[s]) {
            seen[s] = true;
            out.push_back(s);
        }
    }
    return out;
}

struct Employee {
    std::string name;
    std::unordered_map<std::string, std::vector<std::string>> prefs; // day -> ranked shifts
    int days_worked = 0;
    std::unordered_map<std::string, std::string> assignedByDay; // day -> shift or "" if none
};

static bool canWorkMore(const Employee& e) { return e.days_worked < 5; }
static bool isFree(const Employee& e, const std::string& day) {
    auto it = e.assignedByDay.find(day);
    return it == e.assignedByDay.end() || it->second.empty();
}

// schedule[day][shift] = vector of employee names
using Schedule = std::unordered_map<std::string, std::unordered_map<std::string, std::vector<std::string>>>;

static bool tryAssign(
    Schedule& schedule,
    Employee& emp,
    int startDayIdx,
    bool preferredOnlyUntilFull
) {
    if (!canWorkMore(emp)) return false;

    for (int di = startDayIdx; di < (int)DAYS.size(); ++di) {
        const std::string& day = DAYS[di];
        if (!isFree(emp, day)) continue;

        auto pit = emp.prefs.find(day);
        std::vector<std::string> ranked = (pit != emp.prefs.end()) ? pit->second : SHIFTS;

        // 1) ranked
        for (auto &s : ranked) {
            if (preferredOnlyUntilFull && schedule[day][s].size() >= 2) continue;
            schedule[day][s].push_back(emp.name);
            emp.assignedByDay[day] = s;
            emp.days_worked++;
            return true;
        }

        // 2) any shift
        for (auto &s : SHIFTS) {
            if (preferredOnlyUntilFull && schedule[day][s].size() >= 2) continue;
            schedule[day][s].push_back(emp.name);
            emp.assignedByDay[day] = s;
            emp.days_worked++;
            return true;
        }

        // 3) else next day (continue)
    }
    return false;
}

static void fillMinimums(
    std::mt19937_64& rng,
    Schedule& schedule,
    std::vector<Employee>& employees
) {
    for (auto &day : DAYS) {
        for (auto &shift : SHIFTS) {
            while (schedule[day][shift].size() < 2) {
                std::vector<int> eligibleIdx;
                for (int i = 0; i < (int)employees.size(); ++i) {
                    if (canWorkMore(employees[i]) && isFree(employees[i], day)) {
                        eligibleIdx.push_back(i);
                    }
                }
                if (eligibleIdx.empty()) break;

                std::uniform_int_distribution<int> dist(0, (int)eligibleIdx.size() - 1);
                int pick = eligibleIdx[dist(rng)];
                schedule[day][shift].push_back(employees[pick].name);
                employees[pick].assignedByDay[day] = shift;
                employees[pick].days_worked++;
            }
        }
    }
}

static Schedule buildSchedule(std::vector<Employee>& employees, uint64_t seed = 42) {
    std::mt19937_64 rng(seed);

    Schedule schedule;
    for (auto &d : DAYS) {
        for (auto &s : SHIFTS) {
            schedule[d][s] = {};
        }
    }

    // Preference pass
    for (int dayIdx = 0; dayIdx < (int)DAYS.size(); ++dayIdx) {
        std::vector<int> order(employees.size());
        for (int i = 0; i < (int)employees.size(); ++i) order[i] = i;
        std::shuffle(order.begin(), order.end(), rng);

        const std::string& day = DAYS[dayIdx];
        for (int idx : order) {
            if (!canWorkMore(employees[idx])) continue;
            if (!isFree(employees[idx], day)) continue;
            tryAssign(schedule, employees[idx], dayIdx, true);
        }
    }

    // Ensure >= 2 per shift/day
    fillMinimums(rng, schedule, employees);

    return schedule;
}

static void printSchedule(const Schedule& schedule) {
    std::cout << "\nFINAL WEEK SCHEDULE\n"
              << "============================================================\n";
    for (auto &d : DAYS) {
        std::cout << "\n" << d << ":\n";
        for (auto &s : SHIFTS) {
            std::cout << "  " << shiftName(s) << ": ";
            const auto &names = schedule.at(d).at(s);
            if (names.empty()) {
                std::cout << "(none)\n";
            } else {
                for (size_t i = 0; i < names.size(); ++i) {
                    std::cout << names[i] << (i + 1 < names.size() ? ", " : "");
                }
                std::cout << "\n";
            }
        }
    }
}

static void printEmployeeSummary(const std::vector<Employee>& employees) {
    std::cout << "\nEMPLOYEE SUMMARY\n"
              << "============================================================\n";
    for (auto &e : employees) {
        std::cout << e.name << ": " << e.days_worked << " day(s) -> ";
        bool first = true;
        for (auto &d : DAYS) {
            auto it = e.assignedByDay.find(d);
            if (it != e.assignedByDay.end() && !it->second.empty()) {
                if (!first) std::cout << ", ";
                std::cout << d;
                first = false;
            }
        }
        std::cout << "\n";
    }
}

int main() {
    int n;
    std::cout << "Number of employees: ";
    std::cin >> n;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    std::vector<Employee> employees;
    employees.reserve(n);

    for (int i = 0; i < n; ++i) {
        Employee e;
        std::cout << "Employee " << (i + 1) << " name: ";
        std::getline(std::cin, e.name);

        std::cout << "Enter preferences for each day as ranked shifts (comma-separated). Example: M,E,A\n";
        for (auto &d : DAYS) {
            std::cout << "  " << d << ": ";
            std::string line;
            std::getline(std::cin, line);
            e.prefs[d] = splitPrefs(line);
            e.assignedByDay[d] = ""; // none
        }
        employees.push_back(e);
    }

    Schedule schedule = buildSchedule(employees, 42);
    printSchedule(schedule);
    printEmployeeSummary(employees);
    return 0;
}
