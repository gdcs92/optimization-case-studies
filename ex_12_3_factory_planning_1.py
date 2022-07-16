"""Exercise 12.3 Factory Planning 1

Solution for problem 12.3 in the book "Model Building in
Mathematical Programming" by H. Paul Williams.

In brief, given a set of production capability, market, and stocking
constraints, the objective is to find the number of units of each of 7 products
the should be produced each month in a 6 month period so that profit is
maximized.
"""
from pulp import *

prob = LpProblem("Factory Planning 1", LpMaximize)

num_products = 7
num_months = 6
num_steps = 5

profit_per_unit = [10, 6, 8, 4, 11, 9, 3]

stock_cost_per_unit = 0.5

production_hours = [  # product x step
    [0.5, 0.1, 0.2, 0.05, 0],
    [0.7, 0.2, 0, 0.03, 0],
    [0, 0, 0.8, 0, 0.01],
    [0, 0.3, 0, 0.07, 0],
    [0.3, 0, 0, 0.1, 0.05],
    [0.2, 0.6, 0, 0, 0],
    [0.5, 0, 0.6, 0.08, 0.05]
]

machines_available = [  # step x month
    [3, 4, 4, 4, 3, 4],  # grinders
    [2, 2, 2, 1, 1, 2],  # vertical drills
    [3, 1, 3, 3, 3, 2],  # horizontal drills
    [1, 1, 0, 1, 1, 1],  # borer
    [1, 1, 1, 1, 1, 0]   # planer
]

hours_available = [  # step x month
    [machines_available[k][j]*16*24 for j in range(num_months)]
    for k in range(num_steps)
]

market_limit = [  # product x month
    [500, 600, 300, 200, 0, 500],
    [1000, 500, 600, 300, 100, 500],
    [300, 200, 0, 400, 500, 100],
    [300, 0, 0, 500, 100, 300],
    [800, 400, 500, 200, 1000, 1100],
    [200, 300, 400, 0, 300, 500],
    [100, 150, 100, 100, 0, 60]
]

production = [
    [LpVariable(f'p_{i}_{j}', 0, cat=const.LpInteger) for j in range(num_months)]
    for i in range(num_products)
]
sales = [
    [LpVariable(f'v_{i}_{j}', 0, market_limit[i][j], cat=const.LpInteger) for j in range(num_months)]
    for i in range(num_products)
]
stock = [
    [LpVariable(f's_{i}_{j}', 0, 100, cat=const.LpInteger) for j in range(num_months)]
    for i in range(num_products)
]

# Objective
prob += lpSum(
    [
        [
            profit_per_unit[i]*sales[i][j] - stock_cost_per_unit*stock[i][j]
            for j in range(num_months)
        ]
        for i in range(num_products)
    ]
)

# conservation of material constraints
for i in range(num_products):
    prob += (
        stock[i][0] + sales[i][0] == production[i][0]
    )
    for j in range(1, num_months):
        prob += (
            stock[i][j] + sales[i][j] == stock[i][j-1] + production[i][j]
        )

# final stock constraint
for i in range(num_products):
    prob += (
        stock[i][num_months-1] == 50
    )

# production hours constraint
for k in range(num_steps):
    for j in range(num_months):
        prob += (
            lpSum(
                [
                    production_hours[i][k]*production[i][j]
                    for i in range(num_products)
                ]
            ) <= hours_available[k][j]
        )

# # Optionally write model to a .lp file
# prob.writeLP("FactoryPlanning1Model.lp")

# The problem is solved using PuLP's choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print()
print("Status:", LpStatus[prob.status])

# Display attained objective value and other quantities of interest
print("Objective value (total profit) = ", value(prob.objective))

print()
print("Production per month")
for i in range(num_products):
    print(f"PROD{i+1}: ", [production[i][j].varValue for j in range(num_months)])

print()
print("Stock per month")
for i in range(num_products):
    print(f"PROD{i+1}: ", [stock[i][j].varValue for j in range(num_months)])

print()
print("Unfulfilled demand per month")
for i in range(num_products):
    print(
        f"PROD{i+1}: ",
        [(market_limit[i][j] - sales[i][j].varValue) for j in range(num_months)]
    )
