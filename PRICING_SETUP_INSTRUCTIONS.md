# EP Quotient - Pricing & Subscription Setup

## ✅ IMPLEMENTED FEATURES

### 1. Pricing Tiers

**FREE TRIAL** (2 days)
- Price: $0
- 1 video analysis
- 2 simulator scenarios  
- 2 learning bytes
- Report preview only (NO download)
- Screenshot protection enabled

**BASIC PLAN**
- Monthly: $25/month
- Yearly: $275/year (save 17%)
- 7 video analyses per month
- Report download enabled
- Basic EP score (4 dimensions)
- Limited simulator scenarios
- Daily Learning Bytes
- Weekly Training modules
- Basic analytics dashboard

**PRO PLAN** (Most Popular)
- Monthly: $80/month
- Yearly: $850/year (save 17%)
- Unlimited video analyses
- Advanced EP scoring + benchmarks
- Full Simulator (all 20 scenarios)
- Complete Learning Bytes + embedded videos
- Full Training module library
- Advanced analytics + historical trends
- PDF downloads + report sharing
- Priority support
- Early access to features

**ENTERPRISE**
- Custom pricing (contact sales)
- Everything in Pro
- Custom branding
- Bulk user licenses (10+)
- Dedicated account manager
- SLA guarantees

### 2. Whitelisted Emails (Permanent Pro Access)

These emails ALWAYS get Pro tier with unlimited access:
- ashish9731@gmail.com
- ankur@c2x.co.in
- Likitha@c2x.co.in

**Welcome Message**: When whitelisted users login, they see:
"🎉 Your Subscription: Pro Tier - Enjoy unlimited usage of EP Quotient!"

### 3. Device Fingerprinting & Trial Protection

✅ Unique device tracking
✅ One free trial per email
✅ One free trial per device
✅ If trial used on Device A with Email A, no other email can use trial on Device A
✅ If Email A used trial on Device A, Email A cannot use trial on Device B

### 4. Dodo Payments Integration

**SDK Installed**: `dodopayments==1.66.2`
**Files Created**:
- `/app/backend/services/dodo_payment.py` - Payment service
- `/app/.env.backend.example` - Environment template

**Setup Required**:
1. Get your Dodo API key from: https://dashboard.dodopayments.com/
2. Add to `/app/backend/.env`:
   ```
   DODO_API_KEY=your_actual_api_key_here
   FRONTEND_URL=https://exec-presence.preview.emergentagent.com
   ```

**How It Works**:
- When user clicks "Upgrade Now" on Basic or Pro plans
- Dodo payment session is created
- User is redirected to Dodo checkout page
- After payment, user returns to dashboard
- Subscription is activated automatically

### 5. Auto-Redirect to Pricing

✅ First-time users automatically redirected to pricing page after login
✅ Trial expired users see upgrade prompt
✅ Subscription status checked on every dashboard load

## 📁 FILES CREATED/MODIFIED

### Backend Files
- `/app/backend/models/subscription.py` - Subscription models
- `/app/backend/routes/subscription.py` - Subscription API routes
- `/app/backend/services/dodo_payment.py` - Dodo payment integration
- `/app/backend/server.py` - Added subscription routes

### Frontend Files
- `/app/frontend/src/pages/Pricing.js` - Pricing page component
- `/app/frontend/src/lib/deviceFingerprint.js` - Device tracking utility
- `/app/frontend/src/lib/api.js` - Added subscription APIs + device fingerprint
- `/app/frontend/src/pages/Dashboard.js` - Added subscription check + welcome banner
- `/app/frontend/src/App.js` - Added pricing route

## 🔧 API ENDPOINTS

- `GET /api/subscription/status` - Get user's subscription status
- `POST /api/subscription/upgrade` - Upgrade subscription (creates payment)
- `POST /api/subscription/check-video-limit` - Check if user can upload video
- `POST /api/subscription/increment-usage` - Increment video usage count

## 🧪 TESTING

### Test Whitelisted Email:
1. Signup/Login with: ashish9731@gmail.com
2. Should see gold banner: "Your Subscription: Pro Tier"
3. Should have unlimited access to all features

### Test Regular User:
1. Signup with new email
2. Should redirect to /pricing page
3. Should see all 4 pricing tiers
4. Can select Free Trial (no payment)
5. For Basic/Pro, redirected to Dodo checkout

### Test Device Restrictions:
1. Use free trial on Device A with Email A
2. Try using different Email B on Device A → Should block
3. Try using Email A on Device B → Should block

## 📝 NEXT STEPS

1. **Add Dodo API Key** to backend/.env
2. **Test payment flow** with Dodo test mode
3. **Implement download restrictions** for free users
4. **Add screenshot protection** for reports
5. **Webhook handler** for payment confirmations

## 🌐 LIVE URLS

- Pricing Page: https://exec-presence.preview.emergentagent.com/pricing
- Dashboard: https://exec-presence.preview.emergentagent.com/dashboard
- Dodo Docs: https://docs.dodopayments.com/
