import requests
import json

# Calculate commission for a new shipment using the Express tier
commission_data = {
    'shipment_id': 2001,
    'shipment_number': 'SHP-EXPRESS-001',
    'client_invoice_amount': 8000.0,
    'carrier_cost': 5500.0,
    'commission_tier_id': 14
}

response = requests.post('http://127.0.0.1:8000/api/v1/broker/calculate-commission', json=commission_data)
print('Status:', response.status_code)
result = response.json()
print('\n=== Commission Calculation Results ===')
print(f'Shipment: {result["shipment_number"]}')
print(f'Client Invoice: ${result["client_invoice_amount"]:,.2f}')
print(f'Carrier Cost: ${result["carrier_cost"]:,.2f}')
print(f'Gross Profit: ${result["gross_profit"]:,.2f}')
print(f'Commission Rate: {result["commission_percentage"]}%')
print(f'Commission Amount: ${result["commission_amount"]:,.2f}')
print(f'Net Profit: ${result["net_profit"]:,.2f}')
print(f'Profit Margin: {result["profit_margin_percentage"]:.2f}%')
print(f'Status: {result["status"]}')
print(f'Commission ID: {result["id"]}')
