# Stripe Webhook Events & Status Mapping

## Supported Webhook Events

The integration handles the following Stripe webhook events and updates the Google Sheet accordingly:

### 1. `checkout.session.completed`
**When triggered**: Customer completes checkout and creates a new subscription

**Status set**: `Active`

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount (from checkout session)
- Currency
- Timestamp

**Use case**: Initial subscription purchase via Stripe Checkout

---

### 2. `customer.subscription.created`
**When triggered**: New subscription is created (alternative to checkout flow)

**Status set**: `Active`

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount (from subscription plan)
- Currency
- Timestamp

**Use case**: Subscription created via API or dashboard

---

### 3. `customer.subscription.updated`
**When triggered**: Subscription is modified (plan change, status change, etc.)

**Status set**: Based on Stripe subscription status (see mapping below)

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount (from updated plan)
- Currency
- Timestamp

**Use case**: Plan upgrades/downgrades, subscription pauses, status changes

---

### 4. `customer.subscription.deleted`
**When triggered**: Subscription is cancelled or deleted

**Status set**: `Cancelled`

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount
- Currency
- Timestamp

**Use case**: Customer cancels subscription

---

### 5. `invoice.payment_succeeded`
**When triggered**: Invoice payment succeeds (monthly renewal, etc.)

**Status set**: `Active`

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount (amount paid)
- Currency
- Timestamp

**Use case**: Successful monthly/annual payment, keeps subscription active

---

### 6. `invoice.payment_failed`
**When triggered**: Invoice payment fails (card declined, insufficient funds, etc.)

**Status set**: `Past Due`

**Data captured**:
- Customer ID
- Company Name (from metadata)
- Email
- Subscription ID
- Amount (attempted amount)
- Currency
- Timestamp

**Use case**: Failed payment, customer needs to update payment method

---

## Stripe Subscription Status Mapping

When `customer.subscription.updated` event is received, the Stripe subscription status is mapped as follows:

| Stripe Status | Google Sheet Status |
|--------------|---------------------|
| `active` | `Active` |
| `trialing` | `Trial` |
| `past_due` | `Past Due` |
| `canceled` | `Cancelled` |
| `unpaid` | `Unpaid` |
| `incomplete` | `Incomplete` |
| `incomplete_expired` | `Expired` |
| `paused` | `Paused` |

---

## Status Definitions

### Active
- Subscription is active and paid up
- Customer has full access
- Triggered by: successful checkout, subscription creation, successful payment

### Trial
- Customer is in trial period
- May or may not have entered payment information
- Triggered by: subscription with trial period

### Past Due
- Payment failed, but subscription hasn't been cancelled yet
- Stripe will retry payment based on retry settings
- Triggered by: failed invoice payment

### Cancelled
- Subscription has been terminated
- Customer no longer has access
- Triggered by: subscription deletion/cancellation

### Unpaid
- Payment failed and all retry attempts exhausted
- Subscription still exists but is inactive
- Triggered by: subscription status change after failed retries

### Incomplete
- Subscription creation started but payment not completed
- Usually requires 3D Secure or additional authentication
- Triggered by: subscription requiring payment confirmation

### Expired
- Incomplete subscription that wasn't completed in time
- Triggered by: subscription with incomplete_expired status

### Paused
- Subscription is temporarily paused (if using Stripe's pause feature)
- Triggered by: subscription pause action

---

## Configuring Webhooks in Stripe

### Recommended Events to Listen For:

1. **checkout.session.completed** - New subscriptions via Checkout
2. **customer.subscription.created** - New subscriptions
3. **customer.subscription.updated** - Status changes, plan changes
4. **customer.subscription.deleted** - Cancellations
5. **invoice.payment_succeeded** - Successful renewals
6. **invoice.payment_failed** - Failed payments

### Setup Steps:

1. Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your endpoint URL: `https://your-app.onrender.com/webhook`
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook signing secret
6. Add it to your `.env` file as `STRIPE_WEBHOOK_SECRET`

---

## Idempotency Behavior

The webhook integration ensures idempotency by:

1. Searching Column A for existing Customer ID
2. If found: Updates Status (Column E) and Timestamp (Column H) only
3. If not found: Creates new row with all data

This prevents duplicate rows for the same customer, even if multiple webhook events are received.

---

## Testing Webhook Events

You can test webhook events locally using Stripe CLI:

```bash
# Listen for webhooks
stripe listen --forward-to localhost:5000/webhook

# Trigger specific events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

**Note**: Test events may not have all metadata (like `company_name`). Add metadata manually in Stripe Dashboard for realistic testing.

---

## Unhandled Events

Events not listed above are logged but ignored. The webhook will return a 200 OK response with:

```json
{
  "success": true,
  "event": "event.type.name",
  "action": "ignored"
}
```

This prevents Stripe from marking the webhook as failing for events you don't need to handle.
