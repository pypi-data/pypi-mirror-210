from typing import cast
from functools import partial
from ups_lib.pickup_web_service_schema import PickupCreationResponse
from karrio.core.utils import Job, Pipeline, XP, Serializable
from karrio.core.models import (
    PickupRequest,
    PickupUpdateRequest,
    PickupCancelRequest,
)
from karrio.providers.ups.utils import Settings
from karrio.providers.ups.pickup.create import (
    _rate_pickup,
    _create_pickup,
    parse_pickup_response,
)
from karrio.providers.ups.pickup.cancel import pickup_cancel_request

parse_pickup_update_response = parse_pickup_response


def pickup_update_request(
    payload: PickupUpdateRequest, settings: Settings
) -> Serializable:
    """
    Create a pickup request
    Steps
        1 - rate pickup
        2 - create pickup
        3 - cancel old pickup
    :param payload: PickupUpdateRequest
    :param settings: Settings
    :return: Serializable
    """
    request: Pipeline = Pipeline(
        rate=lambda *_: _rate_pickup(
            payload=cast(PickupRequest, payload), settings=settings
        ),
        create=partial(_create_pickup, payload=payload, settings=settings),
        cancel=partial(_cancel_pickup_request, payload=payload, settings=settings),
    )
    return Serializable(request)


def _cancel_pickup_request(
    response: str, payload: PickupUpdateRequest, settings: Settings
):
    reply = next(
        iter(
            XP.to_xml(response).xpath(
                ".//*[local-name() = $name]", name="PickupCreationResponse"
            )
        ),
        None,
    )
    new_pickup = XP.to_object(PickupCreationResponse, reply)
    data = (
        pickup_cancel_request(
            PickupCancelRequest(confirmation_number=payload.confirmation_number),
            settings,
        )
        if new_pickup is not None and new_pickup.PRN is not None
        else None
    )

    return Job(id="cancel_pickup", data=data, fallback="")
