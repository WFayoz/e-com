from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from app.models.user import User


class AdminAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        user = await User.get_by_phone(username)
        if user is None or not user.is_admin or not user.check_password(password):
            raise LoginFailed("Invalid admin credentials")

        request.session.update(
            {
                "admin_user_id": str(user.id),
                "admin_remember_me": remember_me,
            }
        )
        request.state.user = user
        return response

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def is_authenticated(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        user = await User.get(user_id)
        if user is None or not user.is_admin:
            request.session.clear()
            return False

        request.state.user = user
        return True

    def get_admin_user(self, request: Request) -> AdminUser | None:
        user = getattr(request.state, "user", None)
        if user is None:
            return None

        full_name = f"{user.firstname} {user.lastname}".strip()
        return AdminUser(username=full_name or user.phone_number)
