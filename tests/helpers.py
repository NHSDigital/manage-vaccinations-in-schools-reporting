from os import urandom


def create_random_token():
    return urandom(16).hex()


def mock_user_info():
    jwt_data = {
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
        },
        "cis2_info": {
            "selected_org": {"code": "R1L", "name": "SAIS Organisation 1"},
            "selected_role": {
                "code": "S8000:G8000:R8001",
                "workgroups": ["schoolagedimmunisations"],
            },
        },
    }
    jwt_data["user"]["session_token"] = create_random_token()
    jwt_data["user"]["reporting_api_session_token"] = create_random_token()
    return {
        "jwt_data": jwt_data,
        "user_nav": {
            "items": [
                {"text": "Test User", "icon": True},
                {"href": "/logout", "text": "Log out"},
            ]
        },
    }
