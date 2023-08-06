from typing import List
from typing import Optional
from datetime import datetime
from pydantic.fields import Field

from .base import BaseModelORM

class TopSite(BaseModelORM):
    domain: Optional[str]
    icon: Optional[str]
    visits_share: Optional[float]
    is_locked: Optional[bool]
    visitss_hare: Optional[float]

class AdsSource(BaseModelORM):
    ads_sites_total_count: Optional[int]
    top_ads_sites: Optional[List[TopSite]]

class TopSimilarityCompetitor(BaseModelORM):
    domain: Optional[str]
    is_small_site: None
    icon: Optional[str]
    visits_total_count: Optional[float]
    category: Optional[str]
    category_rank: Optional[int]
    affinity: Optional[float]


class Competitors(BaseModelORM):
    top_similarity_competitors: Optional[List[TopSimilarityCompetitor]]


class AgeDistribution(BaseModelORM):
    min_age: Optional[int]
    max_age: Optional[int]
    value: Optional[float]

class GenderDistribution(BaseModelORM):
    male: Optional[float]
    female: Optional[float]


class Demographics(BaseModelORM):
    age_distribution: Optional[List[AgeDistribution]]
    gender_distribution: Optional[GenderDistribution]


class TopCountriesTraffic(BaseModelORM):
    country_alpha_2_code: Optional[str]
    country_url_code: Optional[str]
    visits_share: Optional[float]
    visits_share_change: Optional[float]


class Geography(BaseModelORM):
    countries_total_count: Optional[int]
    top_countries_traffics: Optional[List[TopCountriesTraffic]]

class TopIncomingCategory(BaseModelORM):
    category: Optional[str]
    visits_share: Optional[float]

class IncomingReferrals(BaseModelORM):
    referral_sites_total_count: Optional[int]
    top_referral_sites: Optional[List[TopSite]]
    top_incoming_categories: Optional[List[TopIncomingCategory]]

class TopInterestedWebsite(BaseModelORM):
    domain: Optional[str]
    icon: Optional[str]


class Interests(BaseModelORM):
    top_interested_websites: Optional[List[TopInterestedWebsite]]
    top_interested_topics: Optional[List[str]]
    top_interested_categories: Optional[List[str]]


class TopOutgoingCategory(BaseModelORM):
    category: Optional[str]
    visits_share: Optional[float]


class OutgoingReferrals(BaseModelORM):
    outgoing_sites_total_count: Optional[int]
    top_outgoing_sites: Optional[List[TopSite]]
    top_outgoing_categories: Optional[List[TopOutgoingCategory]]

class Overview(BaseModelORM):
    description: Optional[str]
    global_rank: Optional[int]
    global_rank_change: Optional[int]
    country_alpha_2__code: Optional[str]
    country_url_code: Optional[str]
    country_rank: Optional[int]
    country_rank_change: Optional[int]
    category_rank: Optional[int]
    category_rank_change: Optional[int]
    visits_total_count: Optional[int]
    bounce_rate: Optional[float]
    bounce_rate_formatted: Optional[str]
    pages_per_visit: Optional[float]
    visits_avg_duration_formatted: Optional[str]
    company_feedback_recaptcha: Optional[str]
    company_name: Optional[str]
    company_year_founded: Optional[int]
    company_headquarter_country_code: Optional[str]
    company_headquarter_state_code: Optional[int]
    company_headquarter_city: Optional[str]
    company_employees_min: Optional[int]
    company_revenue_min: Optional[int]
    company_category: Optional[str]

class RankCompetitor(BaseModelORM):
    rank: Optional[int]
    domain: Optional[str]
    icon: Optional[str]

class RankHistory(BaseModelORM):
    date: datetime
    rank: int

class Ranking(BaseModelORM):
    global_rank_history: Optional[List[RankHistory]]
    global_rank_competitors: Optional[List[RankCompetitor]]
    country_rank_history: Optional[List[RankHistory]]
    country_rank_competitors: Optional[List[RankCompetitor]]
    category_rank_history: Optional[List[RankHistory]]
    category_rank_competitors: Optional[List[RankCompetitor]]
    global_rank: Optional[int]
    global_rank_change: Optional[int]
    global_rank_prev: Optional[int]
    category_rank: Optional[int]
    category_rank_prev: Optional[int]
    category_rank_change: Optional[int]
    country_rank: Optional[int]
    country_rank_prev: Optional[int]
    country_rank_change: Optional[int]
    country_alpha_2__code: Optional[str]
    country_url_code: Optional[str]


class TopKeyword(BaseModelORM):
    name: Optional[str]
    estimated_value: Optional[float]
    volume: Optional[float]
    cpc: Optional[float]


class SearchesSource(BaseModelORM):
    organic_search_share: Optional[float]
    paid_search_share: Optional[float]
    keywords_total_count: Optional[int]
    top_keywords: Optional[List[TopKeyword]]

class TopSocialNetwork(BaseModelORM):
    name: Optional[str]
    visits_share: Optional[float]
    icon: Optional[str]


class SocialNetworks(BaseModelORM):
    top_social_networks: Optional[List[TopSocialNetwork]]
    social_networks_total_count: Optional[int]

class Category(BaseModelORM):
    category: Optional[str]
    top_tech_name: Optional[str]
    top_tech_icon_url: Optional[str]
    technologies_total_count: Optional[int]


class Technologies(BaseModelORM):
    categories: Optional[List[Category]]
    categories_total_count: Optional[int]
    technologies_total_count: Optional[int]

class Traffic(BaseModelORM):
    visits_total_count: Optional[int]
    visits_total_count_change: Optional[float]
    bounce_rate: Optional[float]
    bounce_rate_formatted: Optional[str]
    pages_per_visit: Optional[float]
    visits_avg_duration_formatted: Optional[str]
    visits_history: Optional[dict[str, int]]

class TrafficSources(BaseModelORM):
    direct_visits_share: Optional[float]
    referral_visits_share: Optional[float]
    search_visits_share: None
    social_networks_visits_share: Optional[float]
    mail_visits_share: Optional[float]
    ads_visits_share: Optional[float]


class Data(BaseModelORM):
    interests: Optional[Interests]
    competitors: Optional[Competitors]
    searches_source: Optional[SearchesSource]
    incoming_referrals: Optional[IncomingReferrals]
    ads_source: Optional[AdsSource]
    social_networks: Optional[SocialNetworks]
    outgoing_referrals: Optional[OutgoingReferrals]
    technologies: Optional[Technologies]
    snapshot_date: Optional[datetime]
    domain: Optional[str]
    icon: Optional[str]
    preview_desktop: Optional[str]
    preview_mobile: Optional[str]
    is_invalid_traffic_data: Optional[bool]
    is_small_site: Optional[bool]
    domain_ga_status: Optional[int]
    is_data_from_ga_highly_discrepant: Optional[bool]
    is_data_from_ga: Optional[bool]
    category: Optional[str]
    overview: Optional[Overview]
    traffic: Optional[Traffic]
    traffic_sources: Optional[TrafficSources]
    ranking: Optional[Ranking]
    demographics: Optional[Demographics]
    geography: Optional[Geography]

class Result(BaseModelORM):
    description: Optional[str]
    status: Optional[int]
    data: Optional[Data]

class SimilarWebTaskResultModel(BaseModelORM):
    task_utc_created_at: datetime
    task_status: Optional[str]
    is_finished: Optional[bool]
    is_succeeded: Optional[bool]
    is_in_progress: Optional[bool]
    task_utc_finished_at: Optional[datetime]
    task_callback_status: Optional[str]
    task_callback_utc_sent_at: Optional[str]
    task_callback_url: Optional[str]
    result: Optional[Result]
