from typing import Tuple, List
from ups_lib.av_request import (
    AddressValidationRequest as UPSAddressValidationRequest,
    AddressType,
    RequestType,
)
from ups_lib.av_response import Response
from karrio.core.utils import Serializable, Element, XP
from karrio.core.models import (
    AddressValidationRequest,
    Message,
    AddressValidationDetails,
)
from karrio.providers.ups.utils import Settings
from karrio.providers.ups.error import parse_error_response
import karrio.lib as lib


def parse_address_validation_response(
    _response: lib.Deserializable[Element], settings: Settings
) -> Tuple[AddressValidationDetails, List[Message]]:
    response = _response.deserialize()
    status = XP.to_object(Response, lib.find_element("Response", response, first=True))
    success = status is not None and status.ResponseStatusCode == "1"
    validation_details = (
        AddressValidationDetails(
            carrier_id=settings.carrier_id,
            carrier_name=settings.carrier_name,
            success=success,
        )
        if success
        else None
    )

    return validation_details, parse_error_response(response, settings)


def address_validation_request(payload: AddressValidationRequest, _) -> Serializable:
    request = UPSAddressValidationRequest(
        Request=RequestType(
            TransactionReference=None,
            RequestAction="AV",
        ),
        Address=AddressType(
            City=payload.address.city,
            StateProvinceCode=payload.address.state_code,
            CountryCode=payload.address.country_code,
            PostalCode=payload.address.postal_code,
        ),
    )

    return Serializable(request, _request_serializer)


def _request_serializer(request: UPSAddressValidationRequest) -> str:
    return XP.export(request, namespacedef_='xml:lang="en-US"')
