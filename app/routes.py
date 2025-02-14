from collections import defaultdict

from flask import Blueprint, jsonify
from settings import get_settings

from exceptions import NotfoundExceptionError
from stract.service import StractService, get_stract_service
from utils import generate_csv

router = Blueprint("api", __name__)
settings = get_settings()
stract_service: StractService = get_stract_service()


@router.route("/")
def home():
    return jsonify(settings.info_settings.to_dict())


@router.route("/<platform>", methods=["GET"])
def get_ads_insights(platform):
    all_platforms = stract_service.get_all_platforms()
    if not (plataform_value := next(
        (p.value for p in all_platforms if p.text == platform), None)):
        raise NotfoundExceptionError("Platform not found")
    accounts = stract_service.get_accounts(plataform_value)
    fields = stract_service.get_fileds(plataform_value)

    insights_data = []
    for account in accounts:
        insights = stract_service.get_insights(plataform_value, account,
                                               fields)
        row = {"Platform": platform, "Account Name": account.name}
        for field in fields:
            row[field.text] = insights.get(field.value, None)
        insights_data.append(row)

    return generate_csv(insights_data, f'ads_insights({platform})')


@router.route("/<platform>/resumo", methods=["GET"])
def get_ads_summary(platform):
    all_platforms = stract_service.get_all_platforms()
    if not (plataform_value := next(
        (p.value for p in all_platforms if p.text == platform), None)):
        raise NotfoundExceptionError("Platform not found")

    accounts = stract_service.get_accounts(plataform_value)
    fields = stract_service.get_fileds(plataform_value)

    aggregated_data = defaultdict(lambda: {
        "Platform": platform,
        "Account Name": ""
    })

    for account in accounts:
        insights = stract_service.get_insights(plataform_value, account,
                                               fields)
        account_name = account.name

        if account_name not in aggregated_data:
            aggregated_data[account_name]["Account Name"] = account_name

        for field in fields:
            field_name = field.text
            field_value = insights.get(field.value, None)

            if isinstance(field_value, (int, float)):
                aggregated_data[account_name][
                    field_name] = aggregated_data[account_name].get(
                        field_name, 0) + field_value
            else:
                aggregated_data[account_name][field_name] = ""

    insights_data = list(aggregated_data.values())

    return generate_csv(insights_data, f'ads_summary({platform})')


@router.route("/geral", methods=["GET"])
def get_all_ads_insights():
    all_platforms = stract_service.get_all_platforms()
    all_data = []

    for platform in all_platforms:
        platform_name = platform.text
        platform_value = platform.value
        accounts = stract_service.get_accounts(platform_value)
        fields = stract_service.get_fileds(platform_value)

        for account in accounts:
            insights = stract_service.get_insights(platform_value, account,
                                                   fields)
            row = {"Platform": platform_name, "Account Name": account.name}

            for field in fields:
                field_name = field.text
                field_value = insights.get(field.value, None)
                row[field_name] = field_value

            if platform_name.lower(
            ) == "google" and "spend" in row and "clicks" in row:
                spend = row["spend"]
                clicks = row["clicks"]
                row["Cost per Click"] = round(spend /
                                              clicks, 2) if clicks else None

            all_data.append(row)

    return generate_csv(all_data, "ads_insights_all_platforms")


@router.route("/geral/resumo", methods=["GET"])
def ads_summary_all_platforms():
    all_platforms = stract_service.get_all_platforms()
    aggregated_data = {}

    for platform in all_platforms:
        platform_name = platform.text
        platform_value = platform.value
        accounts = stract_service.get_accounts(platform_value)
        fields = stract_service.get_fileds(platform_value)

        if platform_name not in aggregated_data:
            aggregated_data[platform_name] = {"Platform": platform_name}

        for account in accounts:
            insights = stract_service.get_insights(platform_value, account,
                                                   fields)

            for field in fields:
                field_name = field.text
                field_value = insights.get(field.value, None)

                if isinstance(field_value, (int, float)):
                    aggregated_data[platform_name][
                        field_name] = aggregated_data[platform_name].get(
                            field_name, 0) + field_value
                else:
                    aggregated_data[platform_name][field_name] = ""

        if platform_name.lower() == "google analytics":
            spend = aggregated_data[platform_name]["Spend"]
            clicks = aggregated_data[platform_name]["Clicks"]
            aggregated_data[platform_name]["Cost Per Click"] = round(
                spend / clicks, 2) if clicks else None

    insights_data = list(aggregated_data.values())
    return generate_csv(insights_data, "ads_summary_all_platforms")
