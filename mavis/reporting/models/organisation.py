from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.sessions import SessionMixin


class Organisation:
    def __init__(self, organisation: dict):
        self.name: str = organisation["name"]
        self.code: str = organisation["code"]
        self.type: str = "Provider"  # Hard-coded for now

    @staticmethod
    def get_from_session(session: "SessionMixin") -> "Organisation":
        try:
            code = session["cis2_info"]["organisation_code"]
        except KeyError:
            raise ValueError("Organisation code not present in session")
        if code is None or code.strip() == "":
            raise ValueError("Empty value received for organisation code in session")

        try:
            name = session["cis2_info"]["organisation_name"]
        except KeyError:
            raise ValueError("Organisation name not present in session")

        # TODO: Add a name to our test org in Mavis Rails and then throw an error
        # if the name is not present
        if name is None or name.strip() == "":
            name = "Test organisation"

        return Organisation({"code": code, "name": name})
