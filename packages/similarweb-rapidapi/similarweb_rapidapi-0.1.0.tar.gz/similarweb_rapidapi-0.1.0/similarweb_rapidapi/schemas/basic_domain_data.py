from typing import List
from typing import Optional

from pydantic.fields import Field

from .base import BaseModelORM

class Country(BaseModelORM):
    name: str
    continent: str
    numeric_code: str
    alpha_2_code: str

class CategoryRank(BaseModelORM):
    rank: int
    category: str

class CountryRank(BaseModelORM):
    country: Country
    rank: int

class Engagements(BaseModelORM):
    bounce_rate: float
    month: int
    year: int
    page_per_visit: float
    visits: float
    time_on_site: float

class TopCountryShare(BaseModelORM):
    value: float
    country: Country

class TrafficSources(BaseModelORM):
    social: float
    paid_referrals: float
    mail: float
    referrals: float
    search: float
    direct: float

class SimilarWebBasicDomainDataModel(BaseModelORM):

    class Data(BaseModelORM):
        site_name: str
        description: Optional[str]
        is_small_site: bool
        category: str
        top_country_shares: List[TopCountryShare]
        title:  Optional[str]
        estimated_monthly_visits: Optional[dict[str, int]]
        global_rank: int
        engagements:  Optional[Engagements]
        country_rank:  Optional[CountryRank]
        category_rank:  Optional[CategoryRank]
        traffic_sources:  Optional[TrafficSources]
        screenshot:  Optional[str]

    status: int
    description: str
    data: Data

