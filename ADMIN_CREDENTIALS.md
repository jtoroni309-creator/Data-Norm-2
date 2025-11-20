# 🔐 Aura Audit AI - Admin Credentials

## Quick Reference

### Main Portal Admin

**Portal URL:** https://portal.auraai.toroniandcompany.com/login

```
📧 Email:    admin@auraai.com
🔑 Password: AdminAura2024!
👤 Name:     System Administrator
🏢 Org:      Toroni & Company
🔐 Role:     Partner (Full Access)
```

---

### CPA Portal Admin

**Portal URL:** https://cpa.auraai.toroniandcompany.com/login

```
📧 Email:    cpa.admin@auraai.com
🔑 Password: CpaAdmin2024!
👤 Name:     CPA Portal Administrator
🏢 Org:      Toroni & Company
🔐 Role:     Partner (Full Access)
```

---

## ⚠️ IMPORTANT SECURITY NOTICE

1. **Change these passwords immediately after first login**
2. Store credentials securely in a password manager
3. Enable 2FA if available
4. Rotate passwords regularly
5. Do NOT commit this file to public repositories

---

## 🚀 Quick Start

1. **Create Admin Users** (if not already created):
   ```bash
   python scripts/create_admin_user.py
   ```

2. **Login to Portal:**
   - Visit: https://portal.auraai.toroniandcompany.com/login
   - Enter credentials above
   - Change password on first login

3. **Test Engagement Creation:**
   - Navigate to "Engagements"
   - Click "New Engagement"
   - Select client, enter details
   - Verify creation works

---

## 📊 Admin Capabilities

With these credentials, you can:

- ✅ Create and manage engagements
- ✅ Manage team members
- ✅ Access all analytics
- ✅ Run quality control checks
- ✅ Generate reports
- ✅ Access admin portal
- ✅ Manage users and organizations
- ✅ View audit logs
- ✅ Configure system settings

---

## 🔧 Troubleshooting

### Can't Login?

1. **Verify services are running:**
   ```bash
   # Check identity service
   curl http://localhost:8001/health

   # Check gateway
   curl http://localhost:8000/health
   ```

2. **Reset password:**
   - Run `python scripts/create_admin_user.py` again
   - Or use password reset flow (if implemented)

3. **Check logs:**
   ```bash
   # Identity service logs
   docker logs aura-identity-service
   ```

### Database Not Initialized?

```bash
# Run migrations
alembic upgrade head

# Create admin user
python scripts/create_admin_user.py
```

---

*Last Updated: 2025-11-20*
*For detailed documentation, see PLATFORM_FIXES_COMPLETE.md*
