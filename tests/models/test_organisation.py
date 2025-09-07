from typing import cast

import pytest
from flask.sessions import SessionMixin

from mavis.reporting.models.organisation import Organisation


class TestOrganisation:
    def test_init_with_valid_data(self):
        organisation_data = {"name": "Test team", "code": "AB1"}

        org = Organisation(organisation_data)

        assert org.name == "Test team"
        assert org.code == "AB1"
        assert org.type == "Provider"

    def test_get_from_session_with_valid_data(self):
        session = {
            "cis2_info": {"organisation_code": "R1L", "organisation_name": "SAIS team"}
        }

        org = Organisation.get_from_session(cast(SessionMixin, session))

        assert org.name == "SAIS team"
        assert org.code == "R1L"
        assert org.type == "Provider"

    def test_get_from_session_with_whitespace_name_uses_default(self):
        session = {"cis2_info": {"organisation_code": "R1L", "organisation_name": "  "}}

        org = Organisation.get_from_session(cast(SessionMixin, session))

        assert org.name == "Test organisation"
        assert org.code == "R1L"
        assert org.type == "Provider"

    def test_get_from_session_missing_organisation_code_key(self):
        """
        Test get_from_session raises ValueError when organisation_code key is missing.
        """
        session = {"cis2_info": {"organisation_name": "Test team"}}

        with pytest.raises(
            ValueError, match="Organisation code not present in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_missing_cis2_info_key(self):
        """Test get_from_session raises ValueError when cis2_info key is missing."""
        session = {}

        with pytest.raises(
            ValueError, match="Organisation code not present in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_none_organisation_code(self):
        """Test get_from_session raises ValueError when organisation_code is None."""
        session = {
            "cis2_info": {"organisation_code": None, "organisation_name": "Test team"}
        }

        with pytest.raises(
            ValueError, match="Empty value received for organisation code in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_missing_organisation_name_key(self):
        """
        Test get_from_session raises ValueError when organisation_name key is missing.
        """
        session = {"cis2_info": {"organisation_code": "AB1"}}

        with pytest.raises(
            ValueError, match="Organisation name not present in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_empty_organisation_code(self):
        """
        Test get_from_session raises ValueError when organisation_code is empty string.
        """
        session = {
            "cis2_info": {"organisation_code": "", "organisation_name": "Test team"}
        }

        with pytest.raises(
            ValueError, match="Empty value received for organisation code in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_with_whitespace_organisation_code(self):
        """
        Test get_from_session raises ValueError with whitespace-only organisation_code.
        """
        session = {
            "cis2_info": {
                "organisation_code": "   ",
                "organisation_name": "Test team",
            }
        }

        with pytest.raises(
            ValueError, match="Empty value received for organisation code in session"
        ):
            Organisation.get_from_session(cast(SessionMixin, session))
