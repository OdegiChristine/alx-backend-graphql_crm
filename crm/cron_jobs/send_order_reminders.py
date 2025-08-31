#!/usr/bin/env python3
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Calculate date range (last 7 days)
today = datetime.now()
one_week_ago = today - timedelta(days=7)
today_str = today.strftime("%Y-%m-%d")
week_ago_str = one_week_ago.strftime("%Y-%m-%d")

# GraphQL query
query = gql("""
query GetRecentOrders($start: Date!, $end: Date!) {
  orders(orderDate_Gte: $start, orderDate_Lte: $end) {
    id
    customer {
      email
    }
  }
}
""")

# GraphQL transport & client
transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=True)

try:
    result = client.execute(query, variable_values={"start": week_ago_str, "end": today_str})
    orders = result.get("orders", [])
except Exception as e:
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        log_file.write(f"[{datetime.now()}] ERROR: {e}\n")
    exit(1)

with open("/tmp/order_reminders_log.txt", "a") as log_file:
    for order in orders:
        log_file.write(
            f"[{datetime.now()}] Reminder: Order {order['id']} for customer {order['customer']['email']}\n"
        )

print("Order reminders processed!")
