from datetime import datetime, timedelta, timezone
import logging
import requests
from urllib.parse import quote_plus
import time


class ActivityStreamAPI(object):
    def __init__(self, tenant, username, password, base_url=None):
        self.tenant = tenant
        self.username = username
        self.password = password
        self.base_url = base_url or "https://api.activitystream.com"
        self._current_token = None
        self._current_token_expiry = None

    @property
    def _token(self):
        now = datetime.now(timezone.utc)
        if (
            self._current_token_expiry is not None
            and self._current_token is not None
            and self._current_token_expiry > now
        ):
            return self._current_token

        response = requests.get(
            f"{self.base_url}/api/v1/auth/token",
            headers={
                "username": self.username,
                "password": self.password,
            },
        )
        response.raise_for_status()

        self._current_token = response.json()["accessToken"]
        self._current_token_expiry = now + timedelta(
            seconds=35900
        )  # token expiry is actually 36000 seconds from issue time

        return self._current_token

    def ticketing_data(
        self,
        data_type,
        start_datetime,
        end_datetime,
        filter_type="updatedate",
        chunk_size=timedelta(days=1),
    ):
        start_datetime = start_datetime.replace(microsecond=0)
        end_datetime = end_datetime.replace(microsecond=0) + timedelta(seconds=1)

        if data_type not in ["customers", "tickets"]:
            raise Exception("data_type parameter must be one of: customers, tickets")

        if filter_type not in ["updatedate", "salesdate", "eventdate"]:
            raise Exception(
                "filter_type parameter must be one of: updatedate (the default), salesdate, eventdate"
            )

        if end_datetime < start_datetime:
            raise Exception("end_datetime parameter must be later than start_datetime")

        for chunk_start_datetime, chunk_end_datetime in self._chunk_date_range(
            start_datetime, end_datetime, chunk_size
        ):
            path = "/api/v1/data/{data_type}/{filter_type}?startDate={chunk_start_datetime}&endDate={chunk_end_datetime}&itemsPerPage=1000".format(
                data_type=data_type,
                filter_type=filter_type,
                chunk_start_datetime=quote_plus(chunk_start_datetime.isoformat()),
                chunk_end_datetime=quote_plus(chunk_end_datetime.isoformat()),
            )

            yield from self._retrieve_and_yield_data(path)

    def marketing_data(self, start_datetime):
        start_date = start_datetime.date()

        path = "/api/v1/email/marketing-permissions?tenant={tenant}&updatedAfterDate={start_date}&itemsPerPage=1000".format(
            tenant=self.tenant,
            start_date=quote_plus(start_date.isoformat()),
        )

        yield from self._retrieve_and_yield_data(path)

    def _chunk_date_range(self, start_datetime, end_datetime, chunk_size):
        if type(chunk_size) != timedelta or chunk_size < timedelta(seconds=0):
            raise Exception(
                "chunk_size parameter must be positive datetime.timedelta object"
            )

        chunk_start_datetime = start_datetime
        while chunk_start_datetime < end_datetime:
            chunk_end_datetime = chunk_start_datetime + chunk_size

            # The last chunk should never go beyond the original end_datetime
            if chunk_end_datetime > end_datetime:
                chunk_end_datetime = end_datetime

            yield [chunk_start_datetime, chunk_end_datetime]
            chunk_start_datetime = chunk_end_datetime

    def _retrieve_and_yield_data(self, path):
        error_count = 0
        page = 0
        while True:
            try:
                url = f"{self.base_url}{path}&page={page}"
                response = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {self._token}"},
                )
                response.raise_for_status()
                page_data = response.json()
            except requests.HTTPError as e:
                # Client errors should be raised immediately and not retried
                if e.response.status_code < 500:
                    raise

                error_count += 1

                if error_count > 5:
                    logging.exception(e)
                    raise Exception(f"Error threshold reached for Activity Stream API")

                logging.debug(f"Error response {error_count} - sleeping and retrying")
                time.sleep(2 * error_count)
                continue

            error_count = 0
            for item in page_data["data"]:
                yield item

            if page_data.get("next") is None:
                break

            page += 1
