# Complete Simple Ecommerce API Backend

## Summary
Finish this as a clean Django REST Framework ecommerce backend, not a custom frontend yet. The first complete version should support: user auth, vendor product management, product browsing, cart management, order creation, coupon discounts, fake/manual payments, Swagger docs, admin management, and a repeatable bug-fixing workflow.

## Implementation Plan

### 1. Stabilize The Project First
- Rebuild the local environment from `requirements.txt` and confirm `python core/manage.py check` passes.
- Fix the current environment issue: `django_redis` is missing from the active Python install even though `django-redis` is listed.
- Make `pytest` discover real tests by updating test discovery to include app test files or moving tests into the configured pattern.
- Confirm migrations run cleanly from an empty database.

### 2. Normalize API Structure
- Keep the project API-only for v1.
- Standardize route style so all main ecommerce APIs are predictable:
  - Auth: `/accounts/api/v1/...`
  - Products: either keep `/products/` or move to `/api/v1/products/`
  - Cart: add real cart endpoints
  - Orders: keep/create order endpoints
  - Payments: add fake/manual payment endpoints
- Update Swagger settings so documented paths match the real URL structure.

### 3. Finish Core Ecommerce Flow
- Products:
  - Keep published product listing public.
  - Require authenticated vendor users for product create/update/delete.
  - Add search/filter basics: category, price range, published status for owners/admins.
  - Add useful product/admin display fields and `__str__` methods.

- Cart:
  - Add cart serializer and cart item serializer.
  - Add endpoints for viewing the current user cart, adding items, updating quantity, removing items, and clearing the cart.
  - Move cart behavior out of only `ProductViewSet.add_to_cart` so cart can be managed directly.
  - Enforce quantity >= 1 and prevent duplicate cart items for the same product.

- Orders:
  - Order creation should use the authenticated user’s current cart.
  - Validate the cart is not empty.
  - Calculate `total_price` server-side only.
  - Validate city/address/zipcode consistently.
  - Lock order contents enough that later cart changes do not silently change old order totals. For the simple v1, either snapshot order items or prevent editing the cart after order creation; choose snapshot if implementing.
  - Restrict users to their own orders unless admin.

- Coupons:
  - Validate coupon existence, expiration date, discount percent, and max usage limit.
  - Apply coupon during order creation only if valid.
  - Return clear serializer errors for expired/invalid/overused coupons.

- Payments:
  - Implement fake/manual payment flow.
  - Add endpoint to create a payment for an unpaid order.
  - Add admin/manual success action or endpoint that marks payment successful and order paid.
  - Prevent double payment for already-paid orders.
  - Keep gateway integration out of v1.

### 4. Admin, Docs, And Developer Workflow
- Improve Django admin for products, carts, orders, payments, coupons, and users.
- Add Swagger examples/descriptions for main request/response flows.
- Add a short project checklist doc:
  - How to run server.
  - How to run tests.
  - How to create a user/vendor.
  - How to complete checkout with fake payment.

## Test Plan
- Environment:
  - `python core/manage.py check`
  - `python core/manage.py makemigrations --check`
  - `python core/manage.py migrate`
  - `pytest`

- API tests:
  - Register/login/session verification.
  - Vendor creates product; normal user cannot.
  - Public user can list published products.
  - Authenticated user can add/update/remove cart items.
  - Empty cart cannot create order.
  - Order total equals product price times quantity.
  - Valid coupon discounts order total.
  - Expired/invalid/overused coupon is rejected.
  - User cannot access another user’s cart/order/payment.
  - Fake payment marks order as paid.
  - Already-paid order cannot be paid again.

## Repeatable Bug And Feature Workflow
Use this checklist for every bug or feature:

1. Write the goal in one sentence.
2. Reproduce the current behavior manually or with a failing test.
3. Identify the layer: model, serializer, view, permission, URL, admin, settings, or test.
4. Make the smallest code change that fixes that layer.
5. Run the focused test.
6. Run the full test suite.
7. Check Swagger/admin if the API surface changed.
8. Commit with a clear message only after tests pass.

For new features, use this mini-template before coding:

- User story: “As a user/vendor/admin, I want...”
- Endpoint or admin action:
- Required permissions:
- Request fields:
- Response fields:
- Validation rules:
- Tests to add:
- Done when:

## Assumptions
- First complete version is an API backend, not a full storefront UI.
- Payments are fake/manual for v1.
- The priority is a simple, reliable ecommerce flow over advanced features.
- Existing user changes in `core/orders/models.py` should be preserved unless deliberately revised during implementation.
