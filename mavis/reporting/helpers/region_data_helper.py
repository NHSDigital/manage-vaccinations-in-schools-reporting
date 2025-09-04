from mavis.reporting.models.region import Region
from mavis.reporting.models.provider import Provider
from mavis.reporting.models.school import School


def process_region_data(data: dict) -> Region:
    """
    Process the region data from the API data file and convert it into model instances
    with proper relationships where a region has many providers and a provider has many
    schools. Also establishes back-references from schools to their parent provider and
    from providers to their parent region.

    Returns:
        Region: A Region instance with its associated providers and schools
    """
    region = Region(data)

    region.providers = []
    region.schools = []

    for provider_data in data["providers"]:
        provider = Provider(provider_data, region=region)
        provider.schools = []

        for school_data in provider_data["schools"]:
            school_data["code"] = school_data["urn"]
            school = School(school_data, provider, region=region)
            provider.schools.append(school)
            region.schools.append(school)

        region.providers.append(provider)

    return region
