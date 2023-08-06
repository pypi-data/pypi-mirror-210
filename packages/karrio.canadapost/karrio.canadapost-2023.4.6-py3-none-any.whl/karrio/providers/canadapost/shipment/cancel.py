import karrio.lib as lib
from typing import List, Tuple
from canadapost_lib.shipment import ShipmentRefundRequestType, ShipmentInfoType
from karrio.core.models import ShipmentCancelRequest, ConfirmationDetails, Message
from karrio.core.utils import (
    Element,
    Serializable,
    Pipeline,
    Job,
    XP,
)
from karrio.providers.canadapost.error import parse_error_response
from karrio.providers.canadapost.utils import Settings


def parse_shipment_cancel_response(
    _response: lib.Deserializable[Element], settings: Settings
) -> Tuple[ConfirmationDetails, List[Message]]:
    response = _response.deserialize()
    errors = parse_error_response(response, settings)
    success = len(errors) == 0
    confirmation: ConfirmationDetails = (
        ConfirmationDetails(
            carrier_id=settings.carrier_id,
            carrier_name=settings.carrier_name,
            success=success,
            operation="Cancel Shipment",
        )
        if success
        else None
    )

    return confirmation, errors


def shipment_cancel_request(payload: ShipmentCancelRequest, _) -> Serializable:
    identifier = Serializable(payload.shipment_identifier)

    def _refund_if_submitted(shipment_details: str):
        shipment = XP.to_object(ShipmentInfoType, XP.to_xml(shipment_details))
        transmitted = shipment.shipment_status == "transmitted"
        data = (
            dict(
                id=payload.shipment_identifier,
                payload=Serializable(
                    ShipmentRefundRequestType(email=payload.options.get("email")),
                    lambda request: XP.export(
                        request,
                        name_="shipment-refund-request",
                        namespacedef_='xmlns="http://www.canadapost.ca/ws/shipment-v8"',
                    ),
                ),
            )
            if transmitted
            else None
        )

        return Job(id="refund", data=data, fallback=shipment_details)

    def _cancel_other_wise(previous_job_response: str):
        response: Element = XP.to_xml(previous_job_response)
        refunded = response.tag == "shipment-refund-request-info"
        data = identifier if not refunded else None

        return Job(id="cancel", data=data)

    request: Pipeline = Pipeline(
        info=lambda *_: Job(id="info", data=identifier),
        refund=_refund_if_submitted,
        cancel=_cancel_other_wise,
    )

    return Serializable(request)
