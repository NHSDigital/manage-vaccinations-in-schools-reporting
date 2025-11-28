from flask import url_for


class FilterForm:
    def __init__(self, request_args, workgroup, api_client):
        self.request_args = request_args
        self.workgroup = workgroup
        self.api_client = api_client

    def get_filters(self, valid_year_groups):
        filters = {}
        filters["team_workgroup"] = self.workgroup

        filters["programme"] = self.request_args.get("programme") or "flu"

        gender_values = self.request_args.getlist("gender")
        if gender_values:
            filters["gender"] = gender_values

        valid_year_group_values = {yg["value"] for yg in valid_year_groups}

        year_group_values = [
            v
            for v in self.request_args.getlist("year-group")
            if v in valid_year_group_values
        ]
        if year_group_values:
            filters["year_group"] = year_group_values

        return filters

    def get_form_params(self):
        valid_year_groups = self.api_client.get_year_groups_for_programme(
            self.request_args.get("programme") or "flu"
        )

        filters = self.get_filters(valid_year_groups)

        self.programmes = self.api_client.get_programmes()
        self.genders = self.api_client.get_genders()
        self.year_groups = valid_year_groups
        self.filters = filters
        self.action = url_for("main.vaccinations", workgroup=self.workgroup)

        return self
