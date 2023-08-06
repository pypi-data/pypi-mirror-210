from datetime import datetime
from ups_lib.pickup_web_service_schema import (
    PickupRateRequest,
    RequestType,
    PickupDateInfoType,
    PickupAddressType,
    PhoneType,
)
from karrio.core.utils import (
    Serializable,
    create_envelope,
    Envelope,
    DF,
    SF,
)
from karrio.core.models import PickupRequest
from karrio.providers.ups.utils import Settings, default_request_serializer


def pickup_rate_request(payload: PickupRequest, settings: Settings) -> Serializable:
    pickup_date = DF.date(payload.pickup_date)
    same_day = pickup_date.date() == datetime.today().date()

    request = create_envelope(
        header_content=settings.Security,
        body_content=PickupRateRequest(
            Request=RequestType(),
            ShipperAccount=None,
            PickupAddress=PickupAddressType(
                CompanyName=payload.address.company_name,
                ContactName=payload.address.person_name,
                AddressLine=SF.concat_str(
                    payload.address.address_line1, payload.address.address_line2
                ),
                Room=None,
                Floor=None,
                City=payload.address.city,
                StateProvince=payload.address.state_code,
                Urbanization=None,
                PostalCode=payload.address.postal_code,
                CountryCode=payload.address.country_code,
                ResidentialIndicator=("Y" if payload.address.residential else "N"),
                PickupPoint=payload.package_location,
                Phone=PhoneType(Number=payload.address.phone_number or "000-000-0000"),
            ),
            AlternateAddressIndicator="Y",
            ServiceDateOption=("01" if same_day else "02"),
            PickupDateInfo=PickupDateInfoType(
                CloseTime=DF.ftime(payload.closing_time, "%H:%M", "%H%M"),
                ReadyTime=DF.ftime(payload.ready_time, "%H:%M", "%H%M"),
                PickupDate=pickup_date.strftime("%Y%m%d"),
            ),
            TaxInformationIndicator=None,
            UserLevelDiscountIndicator=None,
        ),
    )

    return Serializable(
        request,
        default_request_serializer(
            "v11", 'xmlns:v11="http://www.ups.com/XMLSchema/XOLTWS/Pickup/v1.1"'
        ),
    )
