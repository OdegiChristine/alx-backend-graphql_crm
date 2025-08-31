#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Calculate date range (last 7 days)
today = datetime.now()
one_week_ago = today - timedelta(days=7)
today_str = today.strftime("%Y-%m-%d")
week_ago_str = one_week_ago.strftime("%Y-%m-%d")

# GraphQL query
query = """
query GetRecentOrders($start: Date!, $end: Date!) {
  orders(orderDate_Gte: $start, orderDate_Lte: $end) {
    id
    customer {
      email
    }
  }
}
"""

variables = {"start": week_ago_str, "end": today_str}

try:
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
except Exception as e:
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        log_file.write(f"[{datetime.now()}] ERROR: {e}\n")
    exit(1)

orders = data.get("data", {}).get("orders", [])

with open("/tmp/order_reminders_log.txt", "a") as log_file:
    for order in orders:
        log_file.write(
            f"[{datetime.now()}] Reminder: Order {order['id']} for customer {order['customer']['email']}\n"
        )

print("Order reminders processed!")
