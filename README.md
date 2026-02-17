# Stripe to Google Sheets Webhook Integration

Automatically track B2B subscriptions from Stripe in a Google Sheet without a full database backend.

## Architecture

- **Trigger**: Stripe sends `checkout.session.completed` events to `/webhook` endpoint
- **Process**: Flask app validates signature, extracts customer data, checks for existing customers
- **Action**: Updates Google Sheet with idempotent operations (no duplicates)

## Features

- ✅ **Idempotency**: Searches Column A for existing Customer ID before creating new rows
- ✅ **Update Existing**: Updates Status (Column E) and Timestamp (Column H) for returning customers
- ✅ **New Customers**: Appends complete row with all subscription data
- ✅ **Signature Validation**: Secure webhook verification using Stripe signatures
- ✅ **Health Check**: `/health` endpoint for Render monitoring

## Prerequisites

1. **Google Service Account**:
   - Place `credentials.json` in project root
   - Share your Google Sheet with the service account email: `dispatch-bot@trucking-bot-production.iam.gserviceaccount.com`

2. **Stripe Account**:
   - API Key (from Stripe Dashboard)
   - Webhook Secret (after setting up webhook endpoint)
   - Customer metadata field: `company_name` (required for each customer)

3. **Google Sheet Structure**:
   ```
   Column A: Customer ID (Stripe)
   Column B: Company Name
   Column C: Email
   Column D: Subscription ID
   Column E: Status
   Column F: Amount
   Column G: Currency
   Column H: Timestamp
   ```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
```env
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
TARGET_SHEET_NAME=Trucking Automation Client Tracker
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

**Getting your Google Sheet ID:**
- Open your Google Sheet
- Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/[THIS_IS_THE_SHEET_ID]/edit`

### 3. Share Google Sheet with Service Account

1. Open your Google Sheet
2. Click "Share" button
3. Add email: `dispatch-bot@trucking-bot-production.iam.gserviceaccount.com`
4. Grant "Editor" permissions

### 4. Local Testing

Run the Flask app locally:

```bash
# Option 1: Flask development server
python app.py

# Option 2: Gunicorn (production-like)
gunicorn app:app --bind 0.0.0.0:5000
```

The app will be available at `http://localhost:5000`

### 5. Test with Stripe CLI

Install Stripe CLI: https://stripe.com/docs/stripe-cli

Forward webhooks to local endpoint:
```bash
stripe listen --forward-to localhost:5000/webhook
```

Trigger a test event:
```bash
stripe trigger checkout.session.completed
```

**Note**: You'll need to manually add `company_name` metadata to test customers in Stripe Dashboard for realistic testing.

### 6. Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure environment variables in Render dashboard:
   - `STRIPE_API_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `TARGET_SHEET_NAME`
   - `GOOGLE_SHEET_ID`
4. Add `credentials.json` as a secret file in Render (or use environment variable)
5. Deploy!

Your webhook URL will be: `https://your-app-name.onrender.com/webhook`

### 7. Configure Stripe Webhook

1. Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your Render URL: `https://your-app-name.onrender.com/webhook`
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook signing secret to your `.env` file as `STRIPE_WEBHOOK_SECRET`

See [WEBHOOK_EVENTS.md](WEBHOOK_EVENTS.md) for details on what each event does.

## Endpoints

### `GET /health`
Health check endpoint for Render monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /webhook`
Receives Stripe webhook events.

**Supported Events:**
- `checkout.session.completed` → Status: **Active**
- `customer.subscription.created` → Status: **Active**
- `customer.subscription.updated` → Status: **Dynamic** (based on Stripe status)
- `customer.subscription.deleted` → Status: **Cancelled**
- `invoice.payment_succeeded` → Status: **Active**
- `invoice.payment_failed` → Status: **Past Due**

**Status Values:**
- Active, Trial, Past Due, Cancelled, Unpaid, Incomplete, Expired, Paused

**Behavior:**
- Searches Column A for existing Customer ID
- If found: Updates Status (Column E) and Timestamp (Column H)
- If not found: Appends new row with all customer data

📄 **See [WEBHOOK_EVENTS.md](WEBHOOK_EVENTS.md) for detailed event documentation**

## Testing Checklist

- [ ] Local Flask app runs without errors
- [ ] Health endpoint returns 200 OK
- [ ] Stripe CLI can forward events to local endpoint
- [ ] New customer creates new row in Google Sheet
- [ ] Existing customer updates Status and Timestamp (no duplicate row)
- [ ] Webhook signature validation works
- [ ] Invalid signatures are rejected
- [ ] Deploy to Render succeeds
- [ ] Render health checks pass
- [ ] Stripe production webhook delivers events

## Troubleshooting

**Issue**: "Permission denied" error when accessing Google Sheet
- **Fix**: Ensure service account email has Editor access to the sheet

**Issue**: "Invalid signature" error
- **Fix**: Verify `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe Dashboard

**Issue**: Customer ID not found in Column A
- **Fix**: Check that Column A contains Stripe Customer IDs (format: `cus_...`)

**Issue**: Missing `company_name` metadata
- **Fix**: Add `company_name` to customer metadata in Stripe Dashboard for each customer

## Customer Metadata Setup

In Stripe, each customer should have this metadata:

```json
{
  "company_name": "FullScope Services Inc."
}
```

Add this in:
- Stripe Dashboard > Customers > [Select Customer] > Metadata section
- Or programmatically when creating customers via API

## Support

For issues, check:
1. Application logs in Render dashboard
2. Stripe webhook delivery logs
3. Google Sheets API quota limits
