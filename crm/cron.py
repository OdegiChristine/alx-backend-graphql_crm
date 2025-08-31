import requests
from datetime import datetime

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/low_stock_updates_log.txt"

def log_crm_heartbeat():
    log_path = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Append to the file
    with open(log_path, "a") as log_file:
        log_file.write(message)

    # Verify GraphQL hello endpoint
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            hello_msg = data.get("data", {}).get("hello", "No response")
            with open(log_path, "a") as log_file:
                log_file.write(f"{timestamp} GraphQL hello response: {hello_msg}\n")
    except Exception as e:
        with open(log_path, "a") as log_file:
            log_file.write(f"{timestamp} ERROR querying GraphQL: {e}\n")


def update_low_stock():
    query = """
    mutation {
        updateLowStockProducts {
            success
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        response.raise_for_status()
        data = response.json()

        updates = data["data"]["updatedlowStockProducts"]["updatedProducts"]
        success_msg = data["data"]["updateLowStockProducts"]["success"]

        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

        with open(LOG_FILE, "a") as f:
            f.write(f"\n[{timestamp}] {success_msg}\n")
            for product in updates:
                f.write(f"  - {product['name']}: new stock = {product['stock']}\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"\n[{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')}")
