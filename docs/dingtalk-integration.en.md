# DingTalk Integration and Permission Notes

[中文](dingtalk-integration.md) | [English](dingtalk-integration.en.md)

This note addresses a practical deployment question:

`If Zhiyuxing is integrated into DingTalk, do users have to depend on one personal account or one specific organization permission to access it?`

## Short Answer

Usually no. It depends on the app type and authorization model:

- if the app is an **internal enterprise app**, it is normally only available inside the bound DingTalk organization
- if the goal is to let **other companies or external teams** use it, a single-organization internal app is not enough
- if the integration uses **organization-level APIs**, it usually also involves administrator authorization, app authorization, or delegated user authorization

## Why the Project Should Not Depend Only on DingTalk Access

If access requires all of the following:

- joining a specific DingTalk organization first
- having the app enabled by an admin
- completing organization-level or user-level authorization
- then finally opening the actual page

then the project becomes harder to reuse, demonstrate, and maintain.

A more robust structure is:

1. provide an independent web entry point so the service can run and be accessed directly
2. state clearly in the README that DingTalk is an optional integration scenario, not the only entry point
3. document the DingTalk version separately, including permission boundaries and deployment assumptions

## Common DingTalk Permission Layers

### 1. Internal Enterprise App

- better suited for internal organizational use
- usually bound to a single organization
- not ideal as the only external access path

If the current project depends on internal enterprise app capabilities, it is better to describe DingTalk as a real deployment scenario, not the only runtime form.

### 2. Multi-Organization Distribution or Third-Party App

- if the goal is to let other organizations install and use the app, the design has to move toward multi-organization distribution
- the focus is no longer “borrowing one person’s account”
- the real issue becomes whether another organization can install and authorize the app

From an architecture perspective, this is closer to platform and multi-tenant design.

### 3. Delegated User Authorization

- some capabilities work only after the app is installed and then an individual user grants authorization
- this is about the user granting access to data within their own identity scope
- it is not the same thing as inheriting one person’s private account permissions

## Strategy Used in This Repository

- the web service is the default entry point
- DingTalk is preserved as a business integration scenario in the docs
- the project does not require users to rely on one specific personal account
- if organization-level DingTalk capabilities are added later, the exact authorization flow can be documented based on the actual app type

## References

- DingTalk developer note on upgrading a single-organization app to multi-organization distribution:
  [self_to_upstream](https://open-dingtalk.github.io/developerpedia/docs/develop/permission/single_to_multi/self_to_upstream)
- DingTalk developer docs on permission and access models:
  [Authorization management index](https://open-dingtalk.github.io/developerpedia/docs/develop/permission/intro)
