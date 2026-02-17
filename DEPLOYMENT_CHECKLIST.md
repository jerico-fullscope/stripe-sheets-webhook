# Deployment Checklist

Use this checklist to ensure your Stripe → Google Sheets webhook integration is properly configured and deployed.

## ✅ Pre-Deployment Setup

### 1. Google Sheets Setup
- [ ] Google Sheet created: "Trucking Automation Client Tracker"
- [ ] Sheet structure verified with columns:
  - Column A: Customer ID
  - Column B: Company Name
  - Column C: Email
  - Column D: Subscription ID
  - Column E: Status
  - Column F: Amount
  - Column G: Currency
  - Column H: Timestamp
- [ ] Service account email added as Editor: `dispatch-bot@trucking-bot-production.iam.gserviceaccount.com`
- [ ] Google Sheet ID copied from URL

### 2. Stripe Configuration
- [ ] Stripe API key obtained from Dashboard > Developers > API Keys
- [ ] Test mode or Live mode key selected (use test mode for development)
- [ ] Customer metadata field `company_name` documented for team

### 3. Environment Variables
- [ ] `.env` file created (copied from `.env.example`)
- [ ] `STRIPE_API_KEY` set
- [ ] `STRIPE_WEBHOOK_SECRET` set (placeholder for now, will update after webhook creation)
- [ ] `TARGET_SHEET_NAME` set to: `Trucking Automation Client Tracker`
- [ ] `GOOGLE_SHEET_ID` set with your sheet ID

### 4. Dependencies
- [ ] Python 3.11+ installed
- [ ] Run: `pip install -r requirements.txt`
- [ ] All dependencies installed successfully

### 5. Credentials
- [ ] `credentials.json` file present in project root
- [ ] Service account credentials valid and not expired

---

## ✅ Local Testing

### 1. Basic Tests
- [ ] Run: `python test_basic.py`
- [ ] All tests pass (Imports, File Structure, Environment, App Structure)

### 2. Start Local Server
- [ ] Run: `python run_local.py`
- [ ] Server starts without errors
- [ ] Health endpoint accessible: `http://localhost:5000/health`

### 3. Test with Stripe CLI (Optional but Recommended)
- [ ] Stripe CLI installed: https://stripe.com/docs/stripe-cli
- [ ] Run: `stripe login`
- [ ] Run: `stripe listen --forward-to localhost:5000/webhook`
- [ ] Copy the webhook signing secret to `.env` as `STRIPE_WEBHOOK_SECRET`
- [ ] Trigger test event: `stripe trigger checkout.session.completed`
- [ ] Verify webhook received and processed
- [ ] Check Google Sheet for new row or updated status

### 4. Manual Webhook Test (Alternative)
- [ ] Update `test_webhook.py` with your webhook secret
- [ ] Server running on localhost:5000
- [ ] Run: `python test_webhook.py`
- [ ] Verify all tests pass (health check, new customer, existing customer, invalid signature)

---

## ✅ Render Deployment

### 1. Create Render Account
- [ ] Sign up at https://render.com
- [ ] Connect GitHub account (if using Git)

### 2. Create Web Service
- [ ] Create new "Web Service"
- [ ] Connect repository or use "Deploy from CLI"
- [ ] Select Python environment
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn app:app` (auto-detected from Procfile)

### 3. Configure Environment Variables in Render
- [ ] Add `STRIPE_API_KEY`
- [ ] Add `STRIPE_WEBHOOK_SECRET` (placeholder for now)
- [ ] Add `TARGET_SHEET_NAME`
- [ ] Add `GOOGLE_SHEET_ID`

### 4. Add Service Account Credentials
**Option A: Secret File (Recommended)**
- [ ] Go to Render Dashboard > Environment > Secret Files
- [ ] Add file: `credentials.json`
- [ ] Paste contents of your local `credentials.json`

**Option B: Environment Variable**
- [ ] Convert `credentials.json` to single-line JSON
- [ ] Add as environment variable: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- [ ] Update `sheets_service.py` to read from env var if needed

### 5. Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete
- [ ] Check logs for any errors
- [ ] Test health endpoint: `https://your-app-name.onrender.com/health`

---

## ✅ Stripe Webhook Configuration

### 1. Create Webhook Endpoint
- [ ] Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
- [ ] Click "Add endpoint"
- [ ] Enter URL: `https://your-app-name.onrender.com/webhook`
- [ ] Select API version: Latest

### 2. Select Events to Listen
- [ ] `checkout.session.completed`
- [ ] `customer.subscription.created`
- [ ] `customer.subscription.updated`
- [ ] `customer.subscription.deleted`
- [ ] `invoice.payment_succeeded`
- [ ] `invoice.payment_failed`

### 3. Update Webhook Secret
- [ ] Copy webhook signing secret from Stripe
- [ ] Update `STRIPE_WEBHOOK_SECRET` in Render environment variables
- [ ] Restart Render service to apply changes

---

## ✅ Post-Deployment Testing

### 1. Webhook Connectivity
- [ ] Stripe Dashboard shows webhook as "Enabled"
- [ ] Send test webhook from Stripe Dashboard
- [ ] Check Render logs for received event
- [ ] Verify Google Sheet updates correctly

### 2. Real Transaction Test
- [ ] Create test customer in Stripe with `company_name` metadata
- [ ] Complete test checkout session
- [ ] Verify new row appears in Google Sheet
- [ ] Complete another checkout for same customer
- [ ] Verify status and timestamp updated (no duplicate row)

### 3. Status Change Tests
- [ ] Cancel a subscription in Stripe Dashboard
- [ ] Verify status changes to "Cancelled" in sheet
- [ ] Mark invoice as paid
- [ ] Verify status changes to "Active"
- [ ] Fail a payment
- [ ] Verify status changes to "Past Due"

### 4. Error Handling
- [ ] Send webhook with invalid signature → Should return 400
- [ ] Send webhook without customer metadata → Should handle gracefully
- [ ] Temporarily revoke sheet access → Should log error

---

## ✅ Monitoring & Maintenance

### 1. Stripe Webhook Dashboard
- [ ] Monitor webhook delivery success rate
- [ ] Check for failed deliveries
- [ ] Review webhook logs for errors

### 2. Render Dashboard
- [ ] Monitor application logs
- [ ] Check for error spikes
- [ ] Verify uptime and response times

### 3. Google Sheets
- [ ] Periodically verify data accuracy
- [ ] Check for duplicate rows (shouldn't happen with idempotency)
- [ ] Monitor sheet size (Google Sheets has 10 million cell limit)

### 4. Alerts (Optional)
- [ ] Set up Render alerts for high error rates
- [ ] Configure Stripe webhook failure notifications
- [ ] Create Google Sheets Apps Script for data validation

---

## ✅ Production Readiness

### 1. Security
- [ ] Using live Stripe API keys (not test mode)
- [ ] All secrets stored in environment variables (not hardcoded)
- [ ] `.env` and `credentials.json` in `.gitignore`
- [ ] HTTPS enabled (Render provides this automatically)

### 2. Documentation
- [ ] Team knows how to add `company_name` metadata to Stripe customers
- [ ] [README.md](README.md) reviewed by team
- [ ] [WEBHOOK_EVENTS.md](WEBHOOK_EVENTS.md) understood by team
- [ ] Support contact identified for troubleshooting

### 3. Backup & Recovery
- [ ] Google Sheet has backup copy or version history enabled
- [ ] Stripe webhook can be re-sent if needed
- [ ] Know how to manually add/update rows in sheet

### 4. Scaling Considerations
- [ ] Current Render plan supports expected traffic
- [ ] Google Sheets API quota sufficient (default: 300 requests/minute)
- [ ] Consider database migration if > 50,000 customers

---

## 🚨 Common Issues & Solutions

### "Invalid signature" error
- **Cause**: Webhook secret doesn't match
- **Fix**: Copy correct secret from Stripe webhook settings

### "Permission denied" on Google Sheets
- **Cause**: Service account doesn't have access
- **Fix**: Share sheet with service account email as Editor

### Customer appears as "Unknown Company"
- **Cause**: Missing `company_name` in Stripe customer metadata
- **Fix**: Add metadata to customer in Stripe Dashboard

### Webhook times out
- **Cause**: Render free tier cold start or sheet API slow
- **Fix**: Upgrade Render plan or optimize sheet operations

### Duplicate rows appearing
- **Cause**: Idempotency logic not working
- **Fix**: Check Column A has Customer IDs, verify search logic

---

## 📞 Support Resources

- **Stripe Webhook Docs**: https://stripe.com/docs/webhooks
- **Render Docs**: https://render.com/docs
- **Google Sheets API**: https://developers.google.com/sheets/api
- **gspread Library**: https://docs.gspread.org/

---

## ✅ Final Sign-off

- [ ] All tests pass in production
- [ ] Webhooks delivering successfully
- [ ] Google Sheet updating correctly
- [ ] Team trained on system
- [ ] Documentation complete
- [ ] Monitoring in place

**Date Deployed**: _______________

**Deployed By**: _______________

**Render URL**: _______________

**Stripe Webhook ID**: _______________
