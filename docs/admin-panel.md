# Admin Panel

This project now includes a Starlette Admin panel mounted at `/admin`.

## What was added

- `app/admin/__init__.py`
  - creates the Starlette Admin instance
  - mounts it into the FastAPI app
- `app/admin/auth.py`
  - adds session-based authentication for the admin panel
  - allows access only for users whose role is `ADMIN`
- `app/admin/views.py`
  - registers admin views for:
    - `Category`
    - `Product`
    - `User`
  - hashes user passwords when users are created or edited from the admin panel

## How auth works

The admin panel uses Starlette Admin's `AuthProvider`, not the API JWT flow.

Flow:

1. A user opens `/admin`.
2. Starlette Admin redirects unauthenticated users to `/admin/login`.
3. The login form uses:
   - `username` field -> your `phone_number`
   - `password` field -> your password
4. `app/admin/auth.py` checks:
   - user exists
   - password is valid
   - user role is `ADMIN`
5. If valid, the app stores `admin_user_id` in the session.
6. Every next admin request loads that user from the session and verifies the user is still an admin.

## Important setup detail

The FastAPI app now has `SessionMiddleware` in `main.py`.

That is required because Starlette Admin auth is session-based.

```python
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
```

## Registered admin views

### Categories

- basic CRUD view for `Category`

### Products

- basic CRUD view for `Product`

### Users

- CRUD view for `User`
- `password` is hidden from list/detail pages
- during create:
  - password is required
  - password is hashed before saving
- during edit:
  - leave password empty to keep the current password
  - if password is entered, it is hashed before saving

## Files changed

- `main.py`
- `app/admin/__init__.py`
- `app/admin/auth.py`
- `app/admin/views.py`

## How to use it

1. Make sure you have at least one user with role `ADMIN`.
2. Start the project.
3. Open `/admin`.
4. Log in with:
   - phone number in the `username` field
   - password in the `password` field

## Notes

- Admin panel auth is isolated from the public API auth.
- Only admin users can access the panel.
- Existing API endpoints were not changed for login behavior.
