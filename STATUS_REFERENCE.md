# Status Reference Guide

Quick reference for understanding status values in your Google Sheet.

## Status Mappings by Webhook Event

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STRIPE WEBHOOK → SHEET STATUS                       │
└─────────────────────────────────────────────────────────────────────────┘

EVENT: checkout.session.completed
├─ WHEN: Customer completes checkout
├─ STATUS: Active
└─ ACTION: Create new row OR update existing

EVENT: customer.subscription.created
├─ WHEN: New subscription created
├─ STATUS: Active
└─ ACTION: Create new row OR update existing

EVENT: customer.subscription.updated
├─ WHEN: Subscription modified
├─ STATUS: [Dynamic - see table below]
└─ ACTION: Update existing row (Status + Timestamp)

EVENT: customer.subscription.deleted
├─ WHEN: Subscription cancelled
├─ STATUS: Cancelled
└─ ACTION: Update existing row (Status + Timestamp)

EVENT: invoice.payment_succeeded
├─ WHEN: Payment successful (renewal)
├─ STATUS: Active
└─ ACTION: Update existing row (Status + Timestamp)

EVENT: invoice.payment_failed
├─ WHEN: Payment failed
├─ STATUS: Past Due
└─ ACTION: Update existing row (Status + Timestamp)
```

---

## Stripe Subscription Status → Sheet Status

| Stripe Status | Sheet Status | Meaning | Customer Access |
|--------------|-------------|---------|----------------|
| `active` | **Active** | Subscription is current and paid | ✅ Full Access |
| `trialing` | **Trial** | In trial period | ✅ Full Access |
| `past_due` | **Past Due** | Payment failed, retrying | ⚠️ May have access |
| `canceled` | **Cancelled** | Subscription terminated | ❌ No Access |
| `unpaid` | **Unpaid** | Payment failed, no more retries | ❌ No Access |
| `incomplete` | **Incomplete** | Payment requires action | ⚠️ No Access Yet |
| `incomplete_expired` | **Expired** | Incomplete subscription expired | ❌ No Access |
| `paused` | **Paused** | Temporarily paused | ⏸️ Paused Access |

---

## Status Lifecycle Example

```
New Customer Checkout
     ↓
┌─────────────┐
│   Active    │ ← checkout.session.completed
└─────────────┘
     ↓
     │  Monthly renewal successful
     ↓
┌─────────────┐
│   Active    │ ← invoice.payment_succeeded
└─────────────┘
     ↓
     │  Payment method expired
     ↓
┌─────────────┐
│  Past Due   │ ← invoice.payment_failed
└─────────────┘
     ↓
     │  Customer updates payment method
     ↓
┌─────────────┐
│   Active    │ ← invoice.payment_succeeded
└─────────────┘
     ↓
     │  Customer cancels
     ↓
┌─────────────┐
│  Cancelled  │ ← customer.subscription.deleted
└─────────────┘
```

---

## Action Priorities

### Immediate Action Required
- **Past Due** - Payment failed, customer needs to update payment method
- **Unpaid** - All retries failed, subscription will be cancelled
- **Incomplete** - Customer needs to complete authentication (3D Secure)

### Review Recommended
- **Cancelled** - Customer churned, may want to reach out
- **Paused** - Customer temporarily stopped, may resume

### No Action Needed
- **Active** - Everything working normally
- **Trial** - Customer evaluating service

---

## Filtering in Google Sheets

### Show customers needing attention:
```
=FILTER(A:H, E:E="Past Due")
=FILTER(A:H, E:E="Unpaid")
=FILTER(A:H, E:E="Incomplete")
```

### Show active paying customers:
```
=FILTER(A:H, OR(E:E="Active", E:E="Trial"))
```

### Show churned customers:
```
=FILTER(A:H, E:E="Cancelled")
```

### Show all subscriptions updated in last 24 hours:
```
=FILTER(A:H, H:H>NOW()-1)
```

---

## Color Coding (Optional)

Apply conditional formatting in Google Sheets for visual status tracking:

| Status | Suggested Color | Hex Code |
|--------|----------------|----------|
| Active | Green | `#00FF00` |
| Trial | Light Blue | `#ADD8E6` |
| Past Due | Yellow | `#FFFF00` |
| Cancelled | Red | `#FF0000` |
| Unpaid | Dark Red | `#8B0000` |
| Incomplete | Orange | `#FFA500` |
| Expired | Gray | `#808080` |
| Paused | Light Gray | `#D3D3D3` |

### How to Apply:
1. Select Column E (Status)
2. Format > Conditional formatting
3. Add rules for each status value
4. Set background color

---

## Reporting Queries

### Monthly Recurring Revenue (MRR)
```
=SUMIF(E:E, "Active", F:F)
```

### Active Customer Count
```
=COUNTIF(E:E, "Active")
```

### Churn Rate (Cancelled / Total)
```
=COUNTIF(E:E, "Cancelled") / COUNTA(E:E)
```

### Customers with Payment Issues
```
=COUNTIFS(E:E, "Past Due") + COUNTIFS(E:E, "Unpaid")
```

---

## Troubleshooting Status Issues

### Status not updating?
1. Check Render logs for webhook errors
2. Verify Customer ID in Column A matches Stripe
3. Check Timestamp (Column H) - should be recent

### Wrong status showing?
1. Check Stripe Dashboard for actual subscription status
2. Verify webhook events are being sent
3. Review webhook delivery logs in Stripe

### Duplicate rows with different statuses?
1. Should not happen with idempotency logic
2. Check if Customer ID format is consistent
3. Verify search logic in `sheets_service.py`

---

## Quick Status Lookup

**What does each status mean for your business?**

| Status | Business Meaning | Recommended Action |
|--------|-----------------|-------------------|
| **Active** | Paying customer | Deliver service |
| **Trial** | Evaluating service | Nurture, convert to paid |
| **Past Due** | Payment issue | Contact to update payment |
| **Cancelled** | Lost customer | Exit survey, win-back campaign |
| **Unpaid** | Serious payment issue | Suspend access, contact urgently |
| **Incomplete** | Checkout incomplete | Remind to complete signup |
| **Expired** | Abandoned signup | Re-engagement campaign |
| **Paused** | Temporary hold | Monitor for resume |

---

## Integration with Other Tools

### Export to CRM
Filter by status and export relevant columns to CSV for import into your CRM.

### Email Automation
Use Google Sheets API or Apps Script to trigger emails based on status changes.

### Dashboard
Connect to Google Data Studio or Tableau for visual dashboards.

### Alerts
Set up Apps Script triggers to send Slack/email alerts for specific statuses.

---

Need help? Refer to [WEBHOOK_EVENTS.md](WEBHOOK_EVENTS.md) for technical details.
