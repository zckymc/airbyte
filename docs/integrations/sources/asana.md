# Asana

This page contains the setup guide and reference information for the [Asana](https://asana.com/) source connector.

## Prerequisites

Authentication for the Asana source can be handled via Oauth (Recommended for Airbyte Cloud users) or using a Personal Access Token.
To obtain a Personal Access Token for your Asana account, please 
[follow these steps](https://developers.asana.com/docs/personal-access-token).

#### For Airbyte Open Source users:

If you intend to authenticate using Oauth on Airbyte Open Source, you will need to acquire the following from your Asana account:
- `client_id`
- `client_secret`
- `refresh_token`

:::caution
Acquiring the `refresh_token` can be a challenging and lengthy process. You will need working knowledge of http protocols, dev tools and URI encoding, as well as the use of an API testing app like Postman.

For detailed instructions on the steps needed to acquire a `refresh_token`, please refer to the 
[Asana documentation](https://developers.asana.com/docs/oauth).
:::



## Setup guide
### Set up the Asana source connector in Airbyte
1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**.

:::tip
If this is your first time setting up a source, skip the next step and proceed to step 4.
:::

3. In the top-right corner, click **+ New source**. 
4. Find and select **Asana** from the list of available sources.
4. Enter a **Source name** of your choosing for the connector.

### Select an Authentication method
#### For Airbyte Cloud users:
1. To authenticate, select *one* of the two options below:
    - **Recommended:** From the dropdown menu, select **Authenticate via Asana (Oauth)** and click **Authenticate your Asana account**.
    - From the dropdown menu, select **Authenticate with Personal Access Token** and enter your Personal Access Token.
    
2. Click **Set up source** and wait for the tests to complete.

#### For Airbyte Open Source users:
1. To authenticate, select *one* of the two options below:
    - From the dropdown menu, select **Authenticate via Asana (Oauth)** and enter your
  `client_id`, `client_secret`, and `refresh_token`.
    - From the dropdown menu, select **Authenticate with Personal Access Token** and enter your 
  Personal Access Token.


2. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Asana source connector supports the following 
[sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Supported streams

- [Custom fields](https://developers.asana.com/docs/custom-fields)
- [Projects](https://developers.asana.com/docs/projects)
- [Sections](https://developers.asana.com/docs/sections)
- [Stories](https://developers.asana.com/docs/stories)
- [Tags](https://developers.asana.com/docs/tags)
- [Tasks](https://developers.asana.com/docs/tasks)
- [Teams](https://developers.asana.com/docs/teams)
- [Team Memberships](https://developers.asana.com/docs/team-memberships)
- [Users](https://developers.asana.com/docs/users)
- [Workspaces](https://developers.asana.com/docs/workspaces)

## Performance considerations

The connector is restricted by normal Asana request limitations. For more information on this topic, refer to the 
[Asana documentation](https://developers.asana.com/docs/rate-limits).

## Data type mapping

| Integration Type         | Airbyte Type |
| :----------------------- | :----------- |
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                    |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| 0.1.7   | 2023-05-29 | [26716](https://github.com/airbytehq/airbyte/pull/26716) | Remove authSpecification from spec.json, use advancedAuth instead         |
| 0.1.6   | 2023-05-26 | [26653](https://github.com/airbytehq/airbyte/pull/26653) | Fix order of authentication methods                        |
| 0.1.5   | 2022-11-16 | [19561](https://github.com/airbytehq/airbyte/pull/19561) | Added errors handling, updated SAT with new format         |
| 0.1.4   | 2022-08-18 | [15749](https://github.com/airbytehq/airbyte/pull/15749) | Add cache to project stream                                |
| 0.1.3   | 2021-10-06 | [6832](https://github.com/airbytehq/airbyte/pull/6832)   | Add oauth init flow parameters support                     |
| 0.1.2   | 2021-09-24 | [6402](https://github.com/airbytehq/airbyte/pull/6402)   | Fix SAT tests: update schemas and invalid_config.json file |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add entrypoint and bump version for connector              |
| 0.1.0   | 2021-05-25 | [3510](https://github.com/airbytehq/airbyte/pull/3510)   | New Source: Asana                                          |
