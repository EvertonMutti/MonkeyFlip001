from http import HTTPStatus
from typing import Optional

import requests

from exceptions import APIError, UnknownAPIError
from settings import Settings, get_settings
from stract.models import Account, Field, Platform


class StractService():

    def __init__(self, settings: Settings):
        self.auth_token = settings.stract_settings.token
        self.base_url = settings.stract_settings.base_url

    def __make_request(self,
                       path: str,
                       query_params: Optional[str] = {},
                       headers: Optional[dict] = {}) -> requests.Response:
        headers['Authorization'] = self.auth_token

        try:
            response = requests.get(f"{self.base_url}{path}",
                                    params=query_params,
                                    headers=headers,
                                    timeout=45)
            if 'error' in response.json(
            ) and response.status_code == HTTPStatus.OK:
                raise UnknownAPIError("Serviço não disponível")
            return response

        except UnknownAPIError as error:
            raise error

        except Exception as error:
            raise APIError(
                f"Erro na comunicação com {self.base_url}{path}{query_params}: {error}"
            )

    def get_all_platforms(self) -> list[Platform]:
        response = self.__make_request("/platforms")
        try:
            platforms_data = response.json()
            return [Platform(**p) for p in platforms_data.get("platforms", [])]
        except (ValueError, TypeError) as e:
            raise APIError(f"Erro ao processar resposta da API: {e}")

    def get_accounts(self, platform: str) -> list[Account]:
        accounts = []
        current_page = 1

        while True:
            response = self.__make_request("/accounts",
                                           query_params={
                                               "platform": platform,
                                               "page": current_page
                                           })

            try:
                data = response.json()
                accounts.extend(
                    [Account(**p) for p in data.get("accounts", [])])

                pagination = data.get("pagination", {})
                if pagination.get("current", current_page) >= pagination.get(
                        "total", current_page):
                    break

                current_page += 1

            except (ValueError, TypeError, KeyError) as e:
                raise APIError(f"Erro ao processar resposta da API: {e}")

        return accounts

    def get_fileds(self, platform: str) -> list[Field]:
        fields = []
        current_page = 1

        while True:
            response = self.__make_request("/fields",
                                           query_params={
                                               "platform": platform,
                                               "page": current_page
                                           })

            try:
                data = response.json()
                fields.extend([Field(**p) for p in data.get("fields", [])])

                pagination = data.get("pagination", {})
                if pagination.get("current", current_page) >= pagination.get(
                        "total", current_page):
                    break

                current_page += 1

            except (ValueError, TypeError, KeyError) as e:
                raise APIError(f"Erro ao processar resposta da API: {e}")
        return fields

    def get_insights(self, platform: str, account: Account,
                     fields: Field | list[Field]) -> dict:
        insights = {}
        current_page = 1
        if isinstance(fields, Field):
            fields = [fields]

        fields_str = ','.join([field.value for field in fields])

        while True:
            response = self.__make_request("/insights",
                                           query_params={
                                               "platform": platform,
                                               "account": int(account.id),
                                               "token": account.token,
                                               "fields": fields_str
                                           })

            try:
                data = response.json()
                for insight in data.get("insights", []):
                    insights.update(insight)

                pagination = data.get("pagination", {})
                if pagination.get("current", current_page) >= pagination.get(
                        "total", current_page):
                    break

                current_page += 1

            except (ValueError, TypeError, KeyError) as e:
                raise APIError(f"Erro ao processar resposta da API: {e}")

        return insights


def get_stract_service() -> StractService:
    return StractService(get_settings())
