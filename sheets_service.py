import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


class SheetsService:
    """Service for managing Google Sheets operations with idempotency"""

    def __init__(self):
        """Initialize Google Sheets client"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        # Authenticate using service account
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json',
            self.scope
        )
        self.client = gspread.authorize(creds)

        # Open the target sheet
        sheet_name = os.getenv('TARGET_SHEET_NAME', 'Trucking Automation Client Tracker')
        sheet_id = os.getenv('GOOGLE_SHEET_ID')

        if sheet_id:
            self.spreadsheet = self.client.open_by_key(sheet_id)
        else:
            self.spreadsheet = self.client.open(sheet_name)

        self.worksheet = self.spreadsheet.sheet1

    def find_customer_row(self, customer_id):
        """
        Find row number for existing customer by searching Column A

        Args:
            customer_id: Stripe Customer ID to search for

        Returns:
            Row number if found, None otherwise
        """
        try:
            # Get all values in Column A (Customer ID column)
            customer_ids = self.worksheet.col_values(1)

            # Search for customer_id (case-insensitive)
            for idx, cell_value in enumerate(customer_ids):
                if cell_value.strip().lower() == customer_id.lower():
                    return idx + 1  # gspread uses 1-based indexing

            return None
        except Exception as e:
            print(f"Error finding customer row: {e}")
            return None

    def update_existing_customer(self, row_number, customer_data):
        """
        Update existing customer row (Column E = Status, Column H = Timestamp)

        Args:
            row_number: Row number to update
            customer_data: Dictionary with customer data
        """
        try:
            # Update Column E (Status) - assuming E is column 5
            self.worksheet.update_cell(row_number, 5, customer_data['status'])

            # Update Column H (Timestamp) - assuming H is column 8
            self.worksheet.update_cell(row_number, 8, customer_data['timestamp'])

            print(f"Updated existing customer at row {row_number}")
            return 'updated'
        except Exception as e:
            print(f"Error updating customer: {e}")
            raise

    def append_new_customer(self, customer_data):
        """
        Append new customer row with all data points

        Args:
            customer_data: Dictionary with customer data

        Sheet columns mapping (Actual Sheet Structure):
        A: Stripe Customer ID
        B: Company Name
        C: Contact Name
        D: Contact Email
        E: Subscription Status
        F: Plan Tier
        G: Setup Completed
        H: Last Updated
        I: Currency
        J: Country
        """
        try:
            # Extract contact name from email (before @)
            contact_name = customer_data.get('email', '').split('@')[0] if customer_data.get('email') else ''

            new_row = [
                customer_data['customer_id'],      # Column A: Stripe Customer ID
                customer_data['company_name'],     # Column B: Company Name
                contact_name,                      # Column C: Contact Name (extracted from email)
                customer_data['email'],            # Column D: Contact Email
                customer_data['status'],           # Column E: Subscription Status
                f"${customer_data['amount']:.2f}", # Column F: Plan Tier (formatted as price)
                'FALSE',                           # Column G: Setup Completed (default FALSE)
                customer_data['timestamp'],        # Column H: Last Updated
                customer_data['currency'],         # Column I: Currency
                ''                                 # Column J: Country (empty for now)
            ]

            self.worksheet.append_row(new_row)
            print(f"Appended new customer: {customer_data['customer_id']}")
            return 'created'
        except Exception as e:
            print(f"Error appending customer: {e}")
            raise

    def upsert_customer(self, customer_data):
        """
        Update existing customer or create new one (idempotent operation)

        Args:
            customer_data: Dictionary with customer data containing:
                - customer_id
                - company_name
                - email
                - subscription_id
                - status
                - amount
                - currency
                - timestamp

        Returns:
            'updated' if customer was updated, 'created' if new customer was added
        """
        customer_id = customer_data['customer_id']

        # Check if customer already exists
        existing_row = self.find_customer_row(customer_id)

        if existing_row:
            # Update existing customer
            return self.update_existing_customer(existing_row, customer_data)
        else:
            # Append new customer
            return self.append_new_customer(customer_data)
