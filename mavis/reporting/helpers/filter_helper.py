from flask import request


def build_report_filters(team, api_client):
    filters = {"team_workgroup": team.workgroup}
    filters["programme"] = request.args.get("programme") or "flu"

    if gender_values := request.args.getlist("gender"):
        filters["gender"] = gender_values

    year_groups = api_client.get_year_groups_for_programme(filters["programme"])
    valid = {yg["value"] for yg in year_groups}

    if year_group_values := [
        v for v in request.args.getlist("year-group") if v in valid
    ]:
        filters["year_group"] = year_group_values

    return filters, year_groups
