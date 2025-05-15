# 🚒 Optimization of Ontario Fire Rangers Crew Assignment

## 📌 Problem Statement

Each year, Fire Management Headquarters (FMH) across Ontario organize Fire Rangers into crews in preparation for the wildfire season. Crew assignment, however, is a complex process and must respect several constraints:

- **Balanced experience** among crews  
- **Sufficient nationally-deployable crews**, based on mandatory fitness certification  
- **Availability coverage**, ensuring crews are not left understaffed due to early leaves or late starts  
- **Crew composition rules**, e.g., sometimes a male Ranger cannot be placed with female Rangers  
- **Personal or managers' preferences**, such as working alongside certain teammates or ensuring two rangers are not in the same crew (e.g., rangers who are in relationships)

To optimize crew assignment, this project applies a **Simulated Annealing (SA)** algorithm. SA is chosen over Genetic Algorithms due to the **computational cost of evaluating solutions**.

---

## 🔢 Fire Ranger Data Schema
The Fire Rangers data is stored in a CSV file, where each row corresponds to a single Ranger and each column represents an attribute, such as name, role, or years of experience.

The crew assignment algorithm expects input data from the CSV file with the following headers.
**Note:** All fields are stored as **text**, even if they represent numbers, dates, or lists.

| Column                   | Description                                                                 | Accepted Values / Format                           |
|--------------------------|-----------------------------------------------------------------------------|----------------------------------------------------|
| `Name`                   | Full name of the Fire Ranger                                                | Text                                               |
| `Role`                   | Position of the Ranger in the crew                                          | `Leader`, `Boss`, or `Member`                      |
| `Years of Experience`    | Number of seasons years the Ranger has worked                               | Integer (e.g., `3`, `7`)                           |
| `Fitness Certification`  | Standard of fitness certification achieved                                  | `National` or `Ontario`                            |
| `Start Date`             | Optional start date for availability                                        | Format: `Month Day` (e.g., `May 9`) or blank       |
| `End Date`               | Optional end date for availability                                          | Format: `Month Day` (e.g., `August 18`) or blank   |
| `Gender`                 | Gender identity used for assignment rules                                   | `M`, `F`, or `O`                                   |
| `Mixed Crew Restrictions`| Indicates whether the Ranger must be placed in a same-gender crew           | `Yes` or blank                                     |
| `Same Crew Preferences`  | Names of preferred teammates to be in the **same** crew                     | Comma-separated list of names or blank             |
| `Different Crew Preferences` | Names of Rangers the individual prefers to **avoid** in crew assignments | Comma-separated list of names or blank             |

> All columns must be present in the CSV, though optional fields (like preferences or availability dates) can be left blank.

---

## 🧾 Problem Representation

Each solution is represented as a list of integers:

- The **index** of each integer corresponds to a Fire Ranger  
- The **value** at that index represents the crew assignment (e.g., crew 1, 2, ..., N)

**Example**:  
`[1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3]`

In this example:
- Fire Ranger at index 0 is assigned to crew 1
- Fire Rangers are divided into 3 crews (two of 4 members, one of 5)

**Valid solutions must ensure**:
- Each crew has exactly **1 Crew Leader** and **1 Crew Boss**

---

## ✅ Constraints

- **Preferences**: Respect pairings or avoidances (e.g., Josh prefers to work with Alice)  
- **Experience Balance**: Minimize variance between crews’ average experience and the overall base average  
- **Availability**: Crews must have at least 3 members available at all times, and at least one Crew Leader or Crew Boss
- **Gender Restrictions**: Some Rangers cannot be assigned to mixed-gender crews
- **National Deployment Readiness**: At least 3 certified members per crew  

---

## 🧮 Cost Function

The objective function penalizes solutions based on constraint violations.

### **Total Cost**
$$
Cost = Unsatisfied Preferences Penalty
+ Understaffing Penalty
+ Mixed Crew Penalty
+ National Exchange Penalty
+ Experience Variance Penalty 
$$

### **Penalty Breakdown**

1. **Unsatisfied Personal Preferences**  
$ \text{Penalty} = (S + D) \times 10 $
- S: Number of Fire Rangers with unmet same crew preferences  
- D: Number of unmet different crew preferences

A heavier penalty is applied for unmet *different crew* preferences, with each instance counted. In contrast, *same crew* preferences incur a penalty only once per Ranger, regardless of how many such preferences are unmet.

2. **Understaffing**  
- Leadership Gap: 500 per day, per crew without a leader  
- If Crew Size < 3: 100 per missing member, per day

3. **Mixed-Gender Restriction Violation**  
- 500 for each Ranger with a gender restriction placed in a mixed-gender crew  

4. **National Certification**  
- If no certified leader: `penalty = 100`  
- If < 3 certified members: `penalty = (3 - certified_count) * 50`  

5. **Experience Variance**  
$ V = {\sum(C_i - \overline{C})^2 \over N} $
$ \text{Penalty} = V \times 100 $

- $ C_i $: Average experience in crew i  
- $ \overline{C} $: Average experience across all Rangers  
- N: Number of crews

---

## 🔁 Perturbation Function

Randomly swap two Rangers of the same role (Leader ↔ Leader, Boss ↔ Boss, Member ↔ Member) in order to maintain a valid structure.

---

## 🔧 Algorithm Overview (Simulated Annealing)

1. Load data from `.csv` file  
2. Initialize a valid solution  
3. Calculate initial cost  
4. While `temperature > threshold`:
- a. Generate neighbor solution via perturbation  
- b. Calculate neighbor cost  
- c. Accept neighbor if:
  - Cost is lower, or
  - Random threshold is met: `r < exp(-Δcost / T)`  
- d. Decrease temperature  
5. Return best solution 

---

## 📤 Export Final Solution
After execution, the algorithm exports the final solution as a CSV file that mirrors the original Fire Rangers data structure, with one additional column indicating each Ranger's assigned crew.

## ✅ Example Result
Below is the optimized crew assignment for the Fire Rangers from fire-rangers-data.csv (also saved as solution.csv). This mock data was generated using random names and attributes and is not intended to represent or identify any real person.

**Cost of solution**: `1` (due to minimal unavoidable experience variance)
| Name             | Crew | Role   | Years of Experience | Fitness Certification | Start Date | End Date  | Gender | Mixed Crew Restrictions | Same crew preferences                 | Different crew preferences |
|------------------|------|--------|---------------------|------------------------|------------|-----------|--------|--------------------------|----------------------------------------|-----------------------------|
| Legend Nash      | 1    | Leader | 7                   | National               |            |           | M      |                          | []                                     | ['Mack Small']              |
| Edward Norton    | 1    | Boss   | 5                   | National               |            |           | M      | Yes                      | []                                     | []                          |
| Rowan Murillo    | 1    | Member | 1                   | National               |            |           | M      |                          | []                                     | []                          |
| Charlie Juarez   | 1    | Member | 2                   | National               | May 9      | August 1  | M      |                          | []                                     | []                          |
| Jackson Melendez | 1    | Member | 1                   | National               |            |           | M      |                          | []                                     | []                          |
| John Smith       | 2    | Leader | 9                   | National               |            |           | M      |                          | []                                     | []                          |
| Briggs Macdonald | 2    | Boss   | 3                   | National               |            |           | M      |                          | []                                     | []                          |
| Gracie Monroe    | 2    | Member | 1                   | National               |            |           | F      |                          | ['John Smith', 'Charlie Juarez']       | []                          |
| Rudy Gates       | 2    | Member | 1                   | Ontario                |            |           | O      |                          | []                                     | []                          |
| Anna Hebert      | 2    | Member | 1                   | Ontario                |            |           | F      |                          | []                                     | []                          |
| Jane Doe         | 3    | Leader | 6                   | National               |            |           | F      |                          | []                                     | []                          |
| Gemma Trevino    | 3    | Boss   | 2                   | National               |            | August 25 | F      |                          | []                                     | []                          |
| Jocelyn Jarvis   | 3    | Member | 2                   | National               |            |           | F      |                          | []                                     | []                          |
| Rohan Wilkinson  | 3    | Member | 3                   | National               |            |           | M      |                          | []                                     | []                          |
| Jovanni O’Neal   | 4    | Leader | 4                   | National               |            |           | M      |                          | []                                     | []                          |
| Skyler Wilkerson | 4    | Boss   | 3                   | Ontario                |            |           | F      |                          | []                                     | []                          |
| Ahmir Vo         | 4    | Member | 2                   | National               |            |           | M      |                          | []                                     | []                          |
| Mack Small       | 4    | Member | 4                   | National               |            |           | F      |                          | []                                     | []                          |
| Finnley Hart     | 5    | Leader | 4                   | Ontario                |            | August 18 | M      |                          | []                                     | []                          |
| Adriel Coleman   | 5    | Boss   | 4                   | National               |            |           | F      |                          | ['Jeffrey Coleman']                   | []                          |
| Jeffrey Coleman  | 5    | Member | 2                   | National               |            |           | M      |                          | ['Adriel Coleman']                    | []                          |
| Robin Hull       | 5    | Member | 3                   | National               |            |           | M      |                          | []                                     | []                          |
