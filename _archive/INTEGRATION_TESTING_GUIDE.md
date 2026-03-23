# 📘 EN - GTS Platform Integration Testing Guide

## 📋 EN | Overview

EN GTS EN ERP).

This guide explains how to test GTS platform integration with external systems (Email, Payment, ERP).

---

## 🎯 EN | Integration Testing Goals

### EN:
1. ✅ EN
2. ✅ EN
3. ✅ EN
4. ✅ EN
5. ✅ EN

### Main Goals:
1. ✅ Verify connection to external systems
2. ✅ Test data flow and synchronization
3. ✅ Test error handling and exceptions
4. ✅ Ensure data integrity
5. ✅ Test performance and speed

---

## 📧 EN | Email Integration Tests

### EN | Test File
```
tests/test_email_integration.py
```

### EN | Required Configuration

```python
EMAIL_CONFIG = {
    "smtp_host": "smtp.gmail.com",  # SMTP server
    "smtp_port": 587,                # Port (587 for TLS)
    "username": "your-email@example.com",
    "password": "your-app-password",
    "from_email": "noreply@gts.com",
    "use_tls": True
}
```

### EN | Available Tests

#### 1. EN (SMTP Connection Tests)
```bash
# Test 1: Successful SMTP connection
pytest tests/test_email_integration.py::test_smtp_connection -v

# Test 2: Connection failure handling
pytest tests/test_email_integration.py::test_smtp_connection_failure -v
```

#### 2. EN (Email Sending Tests)
```bash
# Test 3: Plain text email
pytest tests/test_email_integration.py::test_send_plain_text_email -v

# Test 4: HTML email
pytest tests/test_email_integration.py::test_send_html_email -v

# Test 5: Send failure handling
pytest tests/test_email_integration.py::test_send_email_failure -v
```

#### 3. EN (Template Tests)
```bash
# Test 6: Welcome email
pytest tests/test_email_integration.py::test_send_welcome_email -v

# Test 7: Password reset email
pytest tests/test_email_integration.py::test_send_password_reset_email -v

# Test 8: Order confirmation
pytest tests/test_email_integration.py::test_send_order_confirmation_email -v
```

#### 4. EN (Additional Tests)
```bash
# Test 9: Bulk emails
pytest tests/test_email_integration.py::test_send_bulk_emails -v

# Test 10: Email validation
pytest tests/test_email_integration.py::test_email_validation -v

# Test 11: Retry logic
pytest tests/test_email_integration.py::test_email_retry_on_failure -v

# Test 12: Configuration validation
pytest tests/test_email_integration.py::test_email_config_validation -v

# Test 13: Rate limiting
pytest tests/test_email_integration.py::test_email_rate_limiting -v
```

### EN | Run All Email Tests
```bash
pytest tests/test_email_integration.py -v
```

**EN | Expected Result:** 13/13 tests pass ✅

---

## 💳 EN (Stripe) | Payment Integration Tests

### EN | Test File
```
tests/test_payment_integration.py
```

### EN | Required Configuration

```python
STRIPE_CONFIG = {
    "api_key": "sk_test_51234567890",           # Secret key
    "publishable_key": "pk_test_51234567890",    # Publishable key
    "webhook_secret": "whsec_test_secret",       # Webhook secret
    "currency": "usd",
    "api_version": "2023-10-16"
}
```

### EN | Available Tests

#### 1. EN (Payment Intent Tests)
```bash
# Test 1: Create payment intent
pytest tests/test_payment_integration.py::test_create_payment_intent -v

# Test 2: Different amounts
pytest tests/test_payment_integration.py::test_create_payment_intent_different_amounts -v
```

#### 2. EN (Payment Confirmation Tests)
```bash
# Test 3: Confirm payment
pytest tests/test_payment_integration.py::test_confirm_payment -v

# Test 4: End-to-end payment flow
pytest tests/test_payment_integration.py::test_payment_flow_end_to_end -v
```

#### 3. EN (Refund Tests)
```bash
# Test 5: Full refund
pytest tests/test_payment_integration.py::test_create_full_refund -v

# Test 6: Partial refund
pytest tests/test_payment_integration.py::test_create_partial_refund -v
```

#### 4. EN (Customer Management Tests)
```bash
# Test 7: Retrieve customer
pytest tests/test_payment_integration.py::test_retrieve_customer -v
```

#### 5. EN (Subscription Tests)
```bash
# Test 8: Create subscription
pytest tests/test_payment_integration.py::test_create_subscription -v

# Test 9: Subscription with trial
pytest tests/test_payment_integration.py::test_create_subscription_with_trial -v
```

#### 6. EN Webhooks
```bash
# Test 10: Webhook signature verification
pytest tests/test_payment_integration.py::test_webhook_signature_verification -v

# Test 11: Payment succeeded webhook
pytest tests/test_payment_integration.py::test_handle_payment_succeeded_webhook -v

# Test 12: Payment failed webhook
pytest tests/test_payment_integration.py::test_handle_payment_failed_webhook -v
```

#### 7. EN (Error Handling Tests)
```bash
# Test 13: Insufficient funds
pytest tests/test_payment_integration.py::test_insufficient_funds_error -v

# Test 14: Invalid card
pytest tests/test_payment_integration.py::test_invalid_card_error -v
```

#### 8. EN (Validation Tests)
```bash
# Test 15: Amount validation
pytest tests/test_payment_integration.py::test_amount_validation -v

# Test 16: Multi-currency support
pytest tests/test_payment_integration.py::test_multi_currency_support -v
```

#### 9. EN Idempotency
```bash
# Test 17: Idempotent payment creation
pytest tests/test_payment_integration.py::test_idempotent_payment_creation -v
```

#### 10. EN Rate Limiting
```bash
# Test 18: Stripe rate limiting
pytest tests/test_payment_integration.py::test_stripe_rate_limiting -v
```

### EN | Run All Payment Tests
```bash
pytest tests/test_payment_integration.py -v
```

**EN | Expected Result:** 18/18 tests pass ✅

---

## 🏢 EN ERP | ERP Integration Tests

### EN | Test File
```
tests/test_erp_integration.py
```

### EN | Required Configuration

```python
ERP_CONFIG = {
    "api_url": "https://erp.example.com/api/v1",
    "api_key": "erp_api_key_12345",
    "company_id": "COMP-001",
    "timeout": 30
}
```

### EN | Available Tests

#### 1. EN (Authentication Tests)
```bash
# Test 1: ERP authentication
pytest tests/test_erp_integration.py::test_erp_authentication -v

# Test 2: Authentication failure
pytest tests/test_erp_integration.py::test_erp_authentication_failure -v
```

#### 2. EN (Order Sync Tests)
```bash
# Test 3: Sync single order
pytest tests/test_erp_integration.py::test_sync_single_order -v

# Test 4: Sync with invalid data
pytest tests/test_erp_integration.py::test_sync_order_with_invalid_data -v
```

#### 3. EN (Customer Sync Tests)
```bash
# Test 5: Sync customer
pytest tests/test_erp_integration.py::test_sync_customer -v
```

#### 4. EN (Inventory Tests)
```bash
# Test 6: Get inventory
pytest tests/test_erp_integration.py::test_get_inventory -v

# Test 7: Update inventory
pytest tests/test_erp_integration.py::test_update_inventory -v

# Test 8: Low stock alert
pytest tests/test_erp_integration.py::test_inventory_low_stock_alert -v
```

#### 5. EN (Bulk Operations Tests)
```bash
# Test 9: Bulk sync orders
pytest tests/test_erp_integration.py::test_bulk_sync_orders -v

# Test 10: Bulk sync with failures
pytest tests/test_erp_integration.py::test_bulk_sync_with_failures -v
```

#### 6. EN (Real-time Updates Tests)
```bash
# Test 11: Order status tracking
pytest tests/test_erp_integration.py::test_order_status_tracking -v

# Test 12: Status updates
pytest tests/test_erp_integration.py::test_order_status_updates -v
```

#### 7. EN (Error Handling Tests)
```bash
# Test 13: Network timeout
pytest tests/test_erp_integration.py::test_network_timeout_handling -v

# Test 14: API error handling
pytest tests/test_erp_integration.py::test_api_error_handling -v
```

#### 8. EN (Retry Logic Tests)
```bash
# Test 15: Sync with retry
pytest tests/test_erp_integration.py::test_sync_with_retry -v
```

#### 9. EN (Validation Tests)
```bash
# Test 16: Order data validation
pytest tests/test_erp_integration.py::test_order_data_validation -v
```

#### 10. EN Rate Limiting
```bash
# Test 17: ERP rate limiting
pytest tests/test_erp_integration.py::test_erp_rate_limiting -v
```

#### 11. EN (Data Transformation Tests)
```bash
# Test 18: GTS to ERP transformation
pytest tests/test_erp_integration.py::test_gts_to_erp_data_transformation -v
```

#### 12. EN (Batch Processing Tests)
```bash
# Test 19: Batch processing performance
pytest tests/test_erp_integration.py::test_batch_processing_performance -v
```

### EN ERP | Run All ERP Tests
```bash
pytest tests/test_erp_integration.py -v
```

**EN | Expected Result:** 20/20 tests pass ✅

---

## 🚀 EN | Run All Integration Tests

### EN
```bash
# Run all integration tests
pytest tests/test_email_integration.py tests/test_payment_integration.py tests/test_erp_integration.py -v
```

### EN | Run with Coverage Report
```bash
pytest tests/test_*_integration.py --cov=backend --cov-report=html -v
```

### EN XML | Run with XML Report
```bash
pytest tests/test_*_integration.py --junitxml=integration-test-report.xml -v
```

---

## 🔧 EN | Environment Setup

### 1. EN | Environment Variables

EN `.env.integration` EN `backend/`:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@gts.com
SMTP_USE_TLS=true

# Stripe Configuration
STRIPE_API_KEY=sk_test_51234567890
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890
STRIPE_WEBHOOK_SECRET=whsec_test_secret
STRIPE_CURRENCY=usd

# ERP Configuration
ERP_API_URL=https://erp.example.com/api/v1
ERP_API_KEY=erp_api_key_12345
ERP_COMPANY_ID=COMP-001
ERP_TIMEOUT=30
```

### 2. EN | Install Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

---

## 🧪 EN Mocking

### EN Mock | When to Use Mocks

#### ✅ EN Mock EN:
1. EN CI/CD (EN)
2. EN
3. EN (Unit Tests)
4. EN

#### ✅ Use Mocks For:
1. CI/CD tests (avoid real connections)
2. Local development tests
3. Unit tests
4. Error scenario testing

### EN | When to Use Real Tests

#### ✅ EN:
1. EN
2. EN
3. EN
4. EN

#### ✅ Use Real Tests For:
1. Pre-production testing
2. Full integration tests
3. Performance testing
4. Acceptance testing

### EN Mocking | Mocking Examples

#### EN: Mock SMTP
```python
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_email_sending():
    with patch('smtplib.SMTP') as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value = mock_instance
        
        # Your test code here
        service = EmailService(EMAIL_CONFIG)
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test body"
        )
        
        assert result is True
        mock_instance.send_message.assert_called_once()
```

#### EN: Mock Stripe API
```python
@pytest.mark.asyncio
async def test_payment():
    service = StripeService(STRIPE_CONFIG)
    
    # Mock payment intent
    payment_intent = await service.create_payment_intent(
        amount=5000,
        currency="usd"
    )
    
    assert payment_intent["amount"] == 5000
```

---

## 📊 EN | Test Reports

### EN HTML
```bash
pytest tests/test_*_integration.py --html=integration-report.html --self-contained-html
```

### EN JSON
```bash
pytest tests/test_*_integration.py --json-report --json-report-file=integration-report.json
```

### EN | Coverage Report
```bash
pytest tests/test_*_integration.py --cov=backend --cov-report=term-missing
```

---

## 🐛 EN | Troubleshooting

### EN 1: EN SMTP | SMTP Tests Failing

**EN | Solution:**
```bash
# Check SMTP configuration
python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com', 587); s.ehlo(); s.starttls(); print('OK')"
```

### EN 2: EN Stripe | Stripe Tests Failing

**EN | Solution:**
```bash
# Verify Stripe API key
python -c "import stripe; stripe.api_key='sk_test_...'; print(stripe.Balance.retrieve())"
```

### EN 3: EN ERP | ERP Tests Failing

**EN | Solution:**
```bash
# Test ERP API connectivity
curl -H "Authorization: Bearer YOUR_API_KEY" https://erp.example.com/api/v1/health
```

### EN 4: Timeout Errors

**EN | Solution:**
```python
# Increase timeout in pytest.ini
[pytest]
asyncio_mode = auto
timeout = 60
```

---

## 📈 EN | Success Criteria

### EN | Tests Must Achieve:

| EN | Criterion | EN | Target |
|-------|-----------|--------|---------|
| EN | Pass Rate | ≥ 95% | ✅ |
| EN | Coverage | ≥ 80% | ✅ |
| EN | Execution Time | < 2 EN | < 2 min | ✅ |
| EN | Result Stability | 100% | ✅ |

---

## 🔐 EN | Best Practices

### 1. EN | Test Isolation
- EN

### 2. EN Fixtures
```python
@pytest.fixture
async def email_service():
    service = EmailService(EMAIL_CONFIG)
    await service.connect()
    yield service
    await service.disconnect()
```

### 3. EN | Boundary Testing
```python
# Test minimum amount
test_payment(amount=50)  # Minimum $0.50

# Test maximum amount
test_payment(amount=99999999)  # Maximum ~$1M
```

### 4. EN | Performance Testing
```python
import time

start = time.time()
# Run operation
duration = time.time() - start

assert duration < 5.0  # Should complete within 5 seconds
```

---

## 📝 EN | Changelog

### Version 1.0.0 (Current)
- ✅ 13 EN
- ✅ 18 EN (Stripe)
- ✅ 20 EN ERP
- ✅ **EN: 51 EN**

---

## 🆘 EN | Support

EN:
- **EN | Email:** support@gts.com
- **EN | Documentation:** `docs/`
- **GitHub Issues:** `https://github.com/gts/platform/issues`

---

## 📚 EN | Additional References

1. [pytest Documentation](https://docs.pytest.org/)
2. [Stripe API Testing](https://stripe.com/docs/testing)
3. [SMTP Testing Guide](https://www.ietf.org/rfc/rfc5321.txt)
4. [ERP Integration Best Practices](https://www.erp.com/integration-guide)

---

**EN | Last Updated:** 2025-01-12  
**EN | Version:** 1.0.0  
**EN | Status:** ✅ **EN | Production Ready**
