import os
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from sheets_service import SheetsService
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Initialize Sheets Service
sheets_service = SheetsService()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        app.logger.error(f'Invalid payload: {e}')
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        app.logger.error(f'Invalid signature: {e}')
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event['type']
    app.logger.info(f'Received webhook event: {event_type}')

    # Handle different Stripe webhook events
    try:
        if event_type == 'checkout.session.completed':
            # New subscription created via Checkout
            return handle_checkout_completed(event['data']['object'])

        elif event_type == 'customer.subscription.created':
            # New subscription created (alternative to checkout)
            return handle_subscription_event(event['data']['object'], 'Active')

        elif event_type == 'customer.subscription.updated':
            # Subscription updated (plan change, etc.)
            subscription = event['data']['object']
            status = map_subscription_status(subscription['status'])
            return handle_subscription_event(subscription, status)

        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled/deleted
            return handle_subscription_event(event['data']['object'], 'Cancelled')

        elif event_type == 'invoice.payment_succeeded':
            # Payment succeeded - keep Active
            return handle_invoice_event(event['data']['object'], 'Active')

        elif event_type == 'invoice.payment_failed':
            # Payment failed - mark as Past Due
            return handle_invoice_event(event['data']['object'], 'Past Due')

        else:
            # Unhandled event type - log and return success
            app.logger.info(f'Unhandled event type: {event_type}')
            return jsonify({'success': True, 'event': event_type, 'action': 'ignored'}), 200

    except Exception as e:
        app.logger.error(f'Error processing webhook {event_type}: {e}')
        return jsonify({'error': str(e)}), 500


def map_subscription_status(stripe_status):
    """Map Stripe subscription status to our status labels"""
    status_mapping = {
        'active': 'Active',
        'trialing': 'Trial',
        'past_due': 'Past Due',
        'canceled': 'Cancelled',
        'unpaid': 'Unpaid',
        'incomplete': 'Incomplete',
        'incomplete_expired': 'Expired',
        'paused': 'Paused'
    }
    return status_mapping.get(stripe_status.lower(), stripe_status.title())


def handle_checkout_completed(session):
    """Handle checkout.session.completed event"""
    customer_id = session.get('customer')
    if not customer_id:
        app.logger.warning('No customer ID in session')
        return jsonify({'error': 'No customer ID'}), 400

    customer = stripe.Customer.retrieve(customer_id)
    company_name = customer.metadata.get('company_name', 'Unknown Company')
    country = customer.metadata.get('country', '')  # Get country from metadata
    subscription_id = session.get('subscription')

    customer_data = {
        'customer_id': customer_id,
        'company_name': company_name,
        'email': customer.email,
        'subscription_id': subscription_id,
        'status': 'Active',
        'amount': session.get('amount_total', 0) / 100,
        'currency': session.get('currency', 'usd').upper(),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'country': country
    }

    result = sheets_service.upsert_customer(customer_data)
    app.logger.info(f'Checkout completed - Customer: {customer_id} - {result}')
    return jsonify({'success': True, 'action': result, 'status': 'Active'}), 200


def handle_subscription_event(subscription, status):
    """Handle subscription-related events"""
    customer_id = subscription.get('customer')
    if not customer_id:
        app.logger.warning('No customer ID in subscription')
        return jsonify({'error': 'No customer ID'}), 400

    customer = stripe.Customer.retrieve(customer_id)
    company_name = customer.metadata.get('company_name', 'Unknown Company')
    country = customer.metadata.get('country', '')  # Get country from metadata

    # Get plan amount if available
    amount = 0
    currency = 'USD'
    if subscription.get('items') and subscription['items'].get('data'):
        first_item = subscription['items']['data'][0]
        if first_item.get('price'):
            amount = first_item['price'].get('unit_amount', 0) / 100
            currency = first_item['price'].get('currency', 'usd').upper()

    customer_data = {
        'customer_id': customer_id,
        'company_name': company_name,
        'email': customer.email,
        'subscription_id': subscription.get('id'),
        'status': status,
        'amount': amount,
        'currency': currency,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'country': country
    }

    result = sheets_service.upsert_customer(customer_data)
    app.logger.info(f'Subscription event - Customer: {customer_id} - Status: {status} - {result}')
    return jsonify({'success': True, 'action': result, 'status': status}), 200


def handle_invoice_event(invoice, status):
    """Handle invoice-related events"""
    customer_id = invoice.get('customer')
    if not customer_id:
        app.logger.warning('No customer ID in invoice')
        return jsonify({'error': 'No customer ID'}), 400

    customer = stripe.Customer.retrieve(customer_id)
    company_name = customer.metadata.get('company_name', 'Unknown Company')
    country = customer.metadata.get('country', '')  # Get country from metadata
    subscription_id = invoice.get('subscription')

    customer_data = {
        'customer_id': customer_id,
        'company_name': company_name,
        'email': customer.email,
        'subscription_id': subscription_id,
        'status': status,
        'amount': invoice.get('amount_paid', 0) / 100,
        'currency': invoice.get('currency', 'usd').upper(),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'country': country
    }

    result = sheets_service.upsert_customer(customer_data)
    app.logger.info(f'Invoice event - Customer: {customer_id} - Status: {status} - {result}')
    return jsonify({'success': True, 'action': result, 'status': status}), 200


if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=5000)
