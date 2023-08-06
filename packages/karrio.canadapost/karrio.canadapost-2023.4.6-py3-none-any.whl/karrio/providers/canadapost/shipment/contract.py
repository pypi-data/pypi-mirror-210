from canadapost_lib.shipment import (
    ShipmentType,
    ShipmentInfoType,
    DeliverySpecType,
    SenderType,
    AddressDetailsType,
    DestinationType,
    DestinationAddressDetailsType,
    ParcelCharacteristicsType,
    optionsType,
    ReferencesType,
    NotificationType,
    PrintPreferencesType,
    sku_listType,
    SkuType,
    dimensionsType,
    OptionType,
    CustomsType,
    PreferencesType,
    SettlementInfoType,
    groupIdOrTransmitShipment,
)
import typing
import karrio.lib as lib
import karrio.core.units as units
import karrio.core.models as models
import karrio.providers.canadapost.error as provider_error
import karrio.providers.canadapost.units as provider_units
import karrio.providers.canadapost.utils as provider_utils


def parse_shipment_response(
    _response: lib.Deserializable[lib.Element],
    settings: provider_utils.Settings,
) -> typing.Tuple[models.ShipmentDetails, typing.List[models.Message]]:
    response = (
        _response.deserialize() if hasattr(_response, "deserialize") else _response
    )
    shipment = (
        _extract_shipment(response, settings)
        if len(lib.find_element("shipment-id", response)) > 0
        else None
    )
    return shipment, provider_error.parse_error_response(response, settings)


def _extract_shipment(
    response: lib.Element,
    settings: provider_utils.Settings,
) -> models.ShipmentDetails:
    info: ShipmentInfoType = lib.find_element(
        "shipment-info", response, ShipmentInfoType, first=True
    )
    label: lib.Element = lib.find_element("label", response, first=True)

    return models.ShipmentDetails(
        carrier_name=settings.carrier_name,
        carrier_id=settings.carrier_id,
        tracking_number=info.tracking_pin,
        shipment_identifier=info.tracking_pin,
        docs=models.Documents(label=getattr(label, "text", None)),
        meta=dict(
            carrier_tracking_link=settings.tracking_url.format(info.tracking_pin),
        ),
    )


def shipment_request(
    payload: models.ShipmentRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    shipper = lib.to_address(payload.shipper)
    recipient = lib.to_address(payload.recipient)
    service = provider_units.ServiceType.map(payload.service).value_or_key
    package = lib.to_packages(
        payload.parcels,
        provider_units.PackagePresets,
        required=["weight"],
        package_option_type=provider_units.ShippingOption,
    ).single
    options = lib.to_shipping_options(
        options=payload.options,
        package_options=package.options,
        is_international=(
            recipient.country_code is not None and recipient.country_code != "CA"
        ),
        initializer=provider_units.shipping_options_initializer,
    )

    customs = lib.to_customs_info(payload.customs)
    duty = getattr(customs, "duty", None) or models.Duty()
    label_encoding, label_format = provider_units.LabelType[
        payload.label_type or "PDF_4x6"
    ].value

    request = ShipmentType(
        customer_request_id=None,
        groupIdOrTransmitShipment=groupIdOrTransmitShipment(),
        quickship_label_requested=None,
        cpc_pickup_indicator=None,
        requested_shipping_point=provider_utils.format_ca_postal_code(
            shipper.postal_code
        ),
        shipping_point_id=None,
        expected_mailing_date=options.shipment_date.state,
        provide_pricing_info=True,
        provide_receipt_info=None,
        delivery_spec=DeliverySpecType(
            service_code=service,
            sender=SenderType(
                name=shipper.person_name,
                company=(shipper.company_name or "Not Applicable"),
                contact_phone=(shipper.phone_number or "000 000 0000"),
                address_details=AddressDetailsType(
                    city=shipper.city,
                    prov_state=shipper.state_code,
                    country_code=shipper.country_code,
                    postal_zip_code=provider_utils.format_ca_postal_code(
                        shipper.postal_code
                    ),
                    address_line_1=shipper.street,
                    address_line_2=lib.text(shipper.address_line2),
                ),
            ),
            destination=DestinationType(
                name=recipient.person_name,
                company=recipient.company_name,
                additional_address_info=None,
                client_voice_number=recipient.phone_number or "000 000 0000",
                address_details=DestinationAddressDetailsType(
                    city=recipient.city,
                    prov_state=recipient.state_code,
                    country_code=recipient.country_code,
                    postal_zip_code=provider_utils.format_ca_postal_code(
                        recipient.postal_code
                    ),
                    address_line_1=recipient.street,
                    address_line_2=lib.text(recipient.address_line2),
                ),
            ),
            parcel_characteristics=ParcelCharacteristicsType(
                weight=package.weight.map(provider_units.MeasurementOptions).KG,
                dimensions=dimensionsType(
                    length=package.length.map(provider_units.MeasurementOptions).CM,
                    width=package.width.map(provider_units.MeasurementOptions).CM,
                    height=package.height.map(provider_units.MeasurementOptions).CM,
                ),
                unpackaged=None,
                mailing_tube=None,
            ),
            options=(
                optionsType(
                    option=[
                        OptionType(
                            option_code=option.code,
                            option_amount=lib.to_money(option.state),
                            option_qualifier_1=None,
                            option_qualifier_2=None,
                        )
                        for _, option in options.items()
                        if option.state is not False
                    ]
                )
                if any(options.items())
                else None
            ),
            notification=(
                NotificationType(
                    email=(options.email_notification_to.state or recipient.email),
                    on_shipment=True,
                    on_exception=True,
                    on_delivery=True,
                )
                if options.email_notification.state
                and any([options.email_notification_to.state, recipient.email])
                else None
            ),
            print_preferences=PrintPreferencesType(
                output_format=label_format,
                encoding=label_encoding,
            ),
            preferences=PreferencesType(
                service_code=None,
                show_packing_instructions=False,
                show_postage_rate=True,
                show_insured_value=True,
            ),
            customs=(
                CustomsType(
                    currency=options.currency.state or units.Currency.CAD.name,
                    conversion_from_cad=None,
                    reason_for_export="OTH",
                    other_reason=customs.content_type,
                    duties_and_taxes_prepaid=duty.account_number,
                    certificate_number=customs.options.certificate_number.state,
                    licence_number=customs.options.license_number.state,
                    invoice_number=customs.invoice,
                    sku_list=(
                        sku_listType(
                            item=[
                                SkuType(
                                    customs_number_of_units=item.quantity,
                                    customs_description=lib.text(
                                        item.title
                                        or item.description
                                        or item.sku
                                        or "N/B",
                                        max=35,
                                    ),
                                    sku=item.sku or "0000",
                                    hs_tariff_code=item.hs_code,
                                    unit_weight=(item.weight or 1),
                                    customs_value_per_unit=item.value_amount,
                                    customs_unit_of_measure=None,
                                    country_of_origin=(
                                        item.origin_country or shipper.country_code
                                    ),
                                    province_of_origin=shipper.state_code or "N/B",
                                )
                                for item in customs.commodities
                            ]
                        )
                    )
                    if any(customs.commodities or [])
                    else None,
                )
                if payload.customs is not None
                else None
            ),
            references=ReferencesType(
                cost_centre=(
                    options.canadapost_cost_center.state
                    or settings.connection_config.cost_center.state
                    or payload.reference
                ),
                customer_ref_1=payload.reference,
                customer_ref_2=None,
            ),
            settlement_info=SettlementInfoType(
                paid_by_customer=getattr(
                    payload.payment, "account_number", settings.customer_number
                ),
                contract_id=settings.contract_id,
                cif_shipment=None,
                intended_method_of_payment=provider_units.PaymentType.map(
                    getattr(payload.payment, "paid_by", None)
                ).value,
                promo_code=None,
            ),
        ),
        return_spec=None,
        pre_authorized_payment=None,
    )
    request.groupIdOrTransmitShipment.original_tagname_ = "transmit-shipment"

    return lib.Serializable(request, _request_serializer)


def _request_serializer(request: ShipmentType) -> str:
    return lib.to_xml(
        request,
        name_="shipment",
        namespacedef_='xmlns="http://www.canadapost.ca/ws/shipment-v8"',
    )
