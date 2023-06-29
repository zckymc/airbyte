# Chartmogul
This page contains the setup guide and reference information for the [Chartmogul](https://chartmogul.com/) source connector.

## Prerequisites
* Chartmogul API key

## Setup guide
### Step 1: Set up a Chartmogul API key

1. To access the Chartmogul API, you will need to create an API key. Please follow the instructions found in the [Chartmogul documentation](https://help.chartmogul.com/hc/en-us/articles/4407796325906-Creating-and-Managing-API-keys#creating-an-api-key).

### Step 2: Set up the Chartmogul connector in Airbyte
**For Airbyte Cloud:**

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Select **Chartmogul** from the list of available sources.
4. Enter a **Source name**.
4. Enter the **API key** that you obtained.
5. Enter a **Start date**. The **Start date** must be formatted as a UTC timestamp in the following format: `YYYY-MM-DD"T"HH:MM:SS"Z"`. For example, an input of `2017-01-25T06:30:00Z` will signify a start date of 6:30 AM on January 25th, 2017. When feasible, any data before this date will not be replicated. 

:::note
The **Start date** will only apply to the `Activities` stream. The `Customers` endpoint does not provide a way to filter by the creation or update dates.
:::

7. From the **Interval** dropdown menu, select an interval period for the `CustomerCount` stream. The available options are **day**, **week**, **month**, and **quarter**.

8. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Chartmogul source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported Streams

This connector outputs the following full refresh streams:

* [Activities](https://dev.chartmogul.com/reference/list-activities)
* [CustomerCount](https://dev.chartmogul.com/reference/retrieve-customer-count)
* [Customers](https://dev.chartmogul.com/reference/list-customers)

## Performance considerations

The Chartmogul connector should not run into Chartmogul API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.1 | 2023-02-15 | [23075](https://github.com/airbytehq/airbyte/pull/23075) | Specified date formatting in specification |
| 0.2.0 | 2022-11-15 | [19276](https://github.com/airbytehq/airbyte/pull/19276) | Migrate connector from Alpha (Python) to Beta (YAML) |
| 0.1.1 | 2022-03-02 | [10756](https://github.com/airbytehq/airbyte/pull/10756) | Add new stream: customer-count |
| 0.1.0 | 2022-01-10 | [9381](https://github.com/airbytehq/airbyte/pull/9381) | New Source: Chartmogul |
