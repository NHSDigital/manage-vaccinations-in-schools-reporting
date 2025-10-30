from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.sessions import SessionMixin


class Team:
    def __init__(self, team: dict):
        self.name: str = team["name"]
        self.workgroup: str = team["workgroup"]

    @staticmethod
    def get_from_session(session: "SessionMixin") -> "Team":
        try:
            workgroup = session["cis2_info"]["team_workgroup"]
        except KeyError:
            raise ValueError("Team workgroup not present in session")
        if workgroup is None or workgroup.strip() == "":
            raise ValueError("Empty value received for team workgroup in session")

        try:
            name = session["cis2_info"]["team"]["name"]
        except (KeyError, TypeError):
            name = workgroup.upper()

        return Team({"workgroup": workgroup, "name": name})
