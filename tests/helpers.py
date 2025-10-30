from os import urandom


def create_random_token():
    return urandom(16).hex()


def mock_user_info():
    return {
        "jwt_data": {
            "user": {
                "id": 1,
                "email": "nurse.joy@example.com",
                "created_at": "2025-06-16T11:09:24.289+01:00",
                "updated_at": "2025-07-04T10:11:36.100+01:00",
                "provider": None,
                "uid": None,
                "given_name": "Nurse",
                "family_name": "Joy",
                "fallback_role": "nurse",
                "show_in_suppliers": True,
                "session_token": create_random_token(),
                "reporting_api_session_token": create_random_token(),
            },
            "cis2_info": {
                "activity_codes": "",
                "has_other_roles": "",
                "organisation_code": "R1L",
                "organisation_name": "SAIS Organisation 1",
                "role_code": "S8000:G8000:R8001",
                "role_name": "",
                "team_workgroup": "r1l",
                "team": {"name": "SAIS Team 1"},
                "workgroups": ["r1l"],
            },
        },
        "user_nav": {
            "items": [
                {"text": "Test User", "icon": True},
                {"href": "/logout", "text": "Log out"},
            ]
        },
    }
