# activitystreampython
A Python 3 module for interacting with the Activity Stream Data Service API v1.

To find out more about the Activity Stream Data Service API, [browse the Swagger documentation](https://api.activitystream.com/api/v1/swagger-ui/index.html).

## Usage

### Installation

`pip install activitystreampython`

### Sample usage

```python
from activitystreampython import ActivityStreamAPI
from datetime import datetime, timezone, timedelta

tenant = "demo"  # Your Activity Stream tenant (this will be the same as the Activity Stream subdomain)
username = "example@example.com"  # The email address for your API user
password = "correct-horse-battery-staple"  # The password for your API user - NB: don't store passwords in code!

end_datetime = datetime.now(timezone.utc)
start_datetime = end_datetime - timedelta(days=7)

activity_stream = ActivityStreamAPI(tenant=tenant, username=username, password=password)

# Retrieve customers
# This method initialises a generator which can be iterated over to retrieve customer data

customers = activity_stream.ticketing_data(
    data_type="customers",
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    filter_type="updatedate",
)

for customer in customers:
    print(customer)

# Retrieve tickets
# This method initialises a generator which can be iterated over to retrieve ticket data

tickets = activity_stream.ticketing_data(
    data_type="tickets",
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    filter_type="updatedate",
)

for ticket in tickets:
    print(ticket)

# Retrieve marketing permissions
# This method initialises a generator which can be iterated over to retrieve marketing permission data

marketing_permissions = activity_stream.marketing_data(start_datetime=start_datetime)

for marketing_permission in marketing_permissions:
    print(marketing_permission)
```

### Notes

We recommend using the `updatedate` `filter_type` if you are using this package to keep an external
database up-to-date with Activity Stream data. That way you can be sure that you will never miss out
on data even if historic records are backfilled in Activity Stream. For the initial import, using the 
`eventdate` `filter_type` may be more predictable in terms of data volumes for each time period.

This package is not officially supported, although we do use it internally and will endeavour to
avoid breaking changes.

## License

Copyright 2023 crowdEngage Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
   
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
