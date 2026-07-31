from unittest.mock import patch

import pytest

from core.plugin.entities.plugin_daemon import CredentialType
from core.trigger.entities.entities import SubscriptionBuilder
from models.provider_ids import TriggerProviderID
from services.trigger.trigger_subscription_builder_service import TriggerSubscriptionBuilderService

PROVIDER_ID = TriggerProviderID("org/plugin/provider")


def subscription_builder() -> SubscriptionBuilder:
    return SubscriptionBuilder(
        id="builder-1",
        name="Builder",
        tenant_id="tenant-1",
        user_id="user-1",
        provider_id=str(PROVIDER_ID),
        endpoint_id="builder-1",
        parameters={},
        properties={},
        credentials={},
        credential_type=CredentialType.UNAUTHORIZED,
        credential_expires_at=-1,
        expires_at=-1,
    )


@pytest.mark.parametrize(
    ("tenant_id", "user_id", "provider_id"),
    [
        ("other-tenant", "user-1", PROVIDER_ID),
        ("tenant-1", "other-user", PROVIDER_ID),
        ("tenant-1", "user-1", TriggerProviderID("org/plugin/other")),
    ],
)
def test_get_subscription_builder_rejects_non_owner(
    tenant_id: str,
    user_id: str,
    provider_id: TriggerProviderID,
) -> None:
    with patch.object(
        TriggerSubscriptionBuilderService,
        "_get_subscription_builder_by_endpoint_id",
        return_value=subscription_builder(),
    ):
        with pytest.raises(ValueError, match="not found"):
            TriggerSubscriptionBuilderService.get_subscription_builder(
                tenant_id=tenant_id,
                user_id=user_id,
                provider_id=provider_id,
                subscription_builder_id="builder-1",
            )


def test_get_subscription_builder_accepts_owner() -> None:
    builder = subscription_builder()
    with patch.object(
        TriggerSubscriptionBuilderService,
        "_get_subscription_builder_by_endpoint_id",
        return_value=builder,
    ):
        assert (
            TriggerSubscriptionBuilderService.get_subscription_builder(
                tenant_id="tenant-1",
                user_id="user-1",
                provider_id=PROVIDER_ID,
                subscription_builder_id="builder-1",
            )
            is builder
        )


def test_get_subscription_builder_rejects_mismatched_id() -> None:
    builder = subscription_builder().model_copy(update={"id": "other-builder"})
    with patch.object(
        TriggerSubscriptionBuilderService,
        "_get_subscription_builder_by_endpoint_id",
        return_value=builder,
    ):
        with pytest.raises(ValueError, match="not found"):
            TriggerSubscriptionBuilderService.get_subscription_builder(
                tenant_id="tenant-1",
                user_id="user-1",
                provider_id=PROVIDER_ID,
                subscription_builder_id="builder-1",
            )


def test_get_subscription_builder_rejects_mismatched_endpoint() -> None:
    builder = subscription_builder().model_copy(update={"endpoint_id": "other-builder"})
    with patch(
        "services.trigger.trigger_subscription_builder_service.redis_client.get",
        return_value=builder.model_dump_json(),
    ):
        assert TriggerSubscriptionBuilderService._get_subscription_builder_by_endpoint_id("builder-1") is None
