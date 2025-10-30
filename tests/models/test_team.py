from typing import cast

import pytest
from flask.sessions import SessionMixin

from mavis.reporting.models.team import Team


class TestTeam:
    def test_init_with_valid_data(self):
        team_data = {"name": "Test team", "workgroup": "r1l"}

        team = Team(team_data)

        assert team.name == "Test team"
        assert team.workgroup == "r1l"

    def test_get_from_session_with_valid_data(self):
        session = {
            "cis2_info": {
                "team_workgroup": "r1l",
                "team": {"name": "SAIS team"},
            }
        }

        team = Team.get_from_session(cast(SessionMixin, session))

        assert team.name == "SAIS team"
        assert team.workgroup == "r1l"

    def test_get_from_session_without_team_name_uses_default(self):
        session = {"cis2_info": {"team_workgroup": "r1l"}}

        team = Team.get_from_session(cast(SessionMixin, session))

        assert team.name == "R1L"
        assert team.workgroup == "r1l"

    def test_get_from_session_missing_cis2_info_key(self):
        session = {}

        with pytest.raises(ValueError, match="Team workgroup not present in session"):
            Team.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_missing_team_workgroup_key(self):
        session = {"cis2_info": {}}

        with pytest.raises(ValueError, match="Team workgroup not present in session"):
            Team.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_empty_team_workgroup(self):
        session = {"cis2_info": {"team_workgroup": ""}}

        with pytest.raises(
            ValueError, match="Empty value received for team workgroup"
        ):
            Team.get_from_session(cast(SessionMixin, session))

    def test_get_from_session_with_whitespace_team_workgroup(self):
        session = {"cis2_info": {"team_workgroup": "   "}}

        with pytest.raises(
            ValueError, match="Empty value received for team workgroup"
        ):
            Team.get_from_session(cast(SessionMixin, session))
