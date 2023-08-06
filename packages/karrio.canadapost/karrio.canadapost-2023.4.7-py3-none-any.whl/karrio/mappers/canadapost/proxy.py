import base64
import time
from typing import List
from canadapost_lib.rating import mailing_scenario
from karrio.api.proxy import Proxy as BaseProxy
from karrio.core.errors import ShippingSDKError
from karrio.core.utils import (
    request as http,
    exec_async,
    Serializable,
    Deserializable,
    Pipeline,
    Job,
    XP,
)
from karrio.mappers.canadapost.settings import Settings


class Proxy(BaseProxy):
    settings: Settings

    def get_rates(self, request: Serializable) -> Deserializable:
        response = http(
            url=f"{self.settings.server_url}/rs/ship/price",
            data=request.serialize(),
            trace=self.trace_as("xml"),
            method="POST",
            headers={
                "Content-Type": "application/vnd.cpc.ship.rate-v4+xml",
                "Accept": "application/vnd.cpc.ship.rate-v4+xml",
                "Authorization": f"Basic {self.settings.authorization}",
                "Accept-language": f"{self.settings.language}-CA",
            },
        )

        return Deserializable(response, XP.to_xml)

    def get_tracking(self, request: Serializable) -> Deserializable:
        """
        get_tracking make parallel request for each pin
        """
        _throttle = 0.0

        def track(tracking_pin: str) -> str:
            nonlocal _throttle
            time.sleep(_throttle)
            _throttle += 0.025

            return http(
                url=f"{self.settings.server_url}/vis/track/pin/{tracking_pin}/detail",
                trace=self.trace_as("xml"),
                method="GET",
                headers={
                    "Accept": "application/vnd.cpc.track-v2+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        response: List[str] = exec_async(track, request.serialize())

        return Deserializable(XP.bundle_xml(xml_strings=response), XP.to_xml)

    def create_shipment(self, request: Serializable) -> Deserializable:
        def _contract_shipment(job: Job):
            return http(
                url=f"{self.settings.server_url}/rs/{self.settings.customer_number}/{self.settings.customer_number}/shipment",
                data=job.data.serialize(),
                trace=self.trace_as("xml"),
                method="POST",
                headers={
                    "Content-Type": "application/vnd.cpc.shipment-v8+xml",
                    "Accept": "application/vnd.cpc.shipment-v8+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def _non_contract_shipment(job: Job):
            return http(
                url=f"{self.settings.server_url}/rs/{self.settings.customer_number}/ncshipment",
                data=job.data.serialize(),
                trace=self.trace_as("xml"),
                method="POST",
                headers={
                    "Accept": "application/vnd.cpc.ncshipment-v4+xml",
                    "Content-Type": "application/vnd.cpc.ncshipment-v4+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def _get_label(job: Job):
            label_string = http(
                decoder=lambda b: base64.encodebytes(b).decode("utf-8"),
                url=job.data["href"],
                method="GET",
                headers={
                    "Accept": job.data["media"],
                    "Authorization": f"Basic {self.settings.authorization}",
                },
            )
            return f"<label>{label_string}</label>"

        def process(job: Job):
            if job.data is None:
                return job.fallback

            subprocess = {
                "contract_shipment": _contract_shipment,
                "non_contract_shipment": _non_contract_shipment,
                "shipment_label": _get_label,
            }
            if job.id not in subprocess:
                raise ShippingSDKError(f"Unknown shipment request job id: {job.id}")

            return subprocess[job.id](job)

        pipeline: Pipeline = request.serialize()
        response = pipeline.apply(process)

        return Deserializable(XP.bundle_xml(response), XP.to_xml)

    def cancel_shipment(self, request: Serializable) -> Deserializable:
        def _request(method: str, shipment_id: str, path: str = "", **kwargs):
            return http(
                url=f"{self.settings.server_url}/rs/{self.settings.customer_number}/{self.settings.customer_number}/shipment/{shipment_id}{path}",
                trace=self.trace_as("xml"),
                method=method,
                headers={
                    "Content-Type": "application/vnd.cpc.shipment-v8+xml",
                    "Accept": "application/vnd.cpc.shipment-v8+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
                **kwargs,
            )

        def process(job: Job):
            if job.data is None:
                return job.fallback

            subprocess = {
                "info": lambda _: _request("GET", job.data.serialize()),
                "refund": lambda _: _request(
                    "POST",
                    job.data["id"],
                    "/refund",
                    data=job.data["payload"].serialize(),
                ),
                "cancel": lambda _: _request("DELETE", job.data.serialize()),
            }
            if job.id not in subprocess:
                raise ShippingSDKError(
                    f"Unknown shipment cancel request job id: {job.id}"
                )

            return subprocess[job.id](job)

        pipeline: Pipeline = request.serialize()
        response = pipeline.apply(process)
        return Deserializable(XP.bundle_xml(response), XP.to_xml)

    def schedule_pickup(self, request: Serializable) -> Deserializable:
        def _availability(job: Job) -> str:
            return http(
                url=f"{self.settings.server_url}/ad/pickup/pickupavailability/{job.data}",
                trace=self.trace_as("xml"),
                method="GET",
                headers={
                    "Accept": "application/vnd.cpc.pickup+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def _create_pickup(job: Job) -> str:
            return http(
                url=f"{self.settings.server_url}/enab/{self.settings.customer_number}/pickuprequest",
                data=job.data.serialize(),
                trace=self.trace_as("xml"),
                method="POST",
                headers={
                    "Accept": "application/vnd.cpc.pickuprequest+xml",
                    "Content-Type": "application/vnd.cpc.pickuprequest+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def process(job: Job):
            if job.data is None:
                return job.fallback

            subprocess = {
                "create_pickup": _create_pickup,
                "availability": _availability,
            }
            if job.id not in subprocess:
                raise ShippingSDKError(f"Unknown pickup request job id: {job.id}")

            return subprocess[job.id](job)

        pipeline: Pipeline = request.serialize()
        response = pipeline.apply(process)

        return Deserializable(XP.bundle_xml(response), XP.to_xml)

    def modify_pickup(self, request: Serializable) -> Deserializable:
        def _get_pickup(job: Job) -> str:
            return http(
                url=f"{self.settings.server_url}{job.data.serialize()}",
                trace=self.trace_as("xml"),
                method="GET",
                headers={
                    "Accept": "application/vnd.cpc.pickup+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def _update_pickup(job: Job) -> str:
            payload = job.data.serialize()
            return http(
                url=f"{self.settings.server_url}/enab/{self.settings.customer_number}/pickuprequest/{payload['pickuprequest']}",
                data=payload["data"],
                trace=self.trace_as("xml"),
                method="PUT",
                headers={
                    "Accept": "application/vnd.cpc.pickuprequest+xml",
                    "Authorization": f"Basic {self.settings.authorization}",
                    "Accept-language": f"{self.settings.language}-CA",
                },
            )

        def process(job: Job):
            if job.data is None:
                return job.fallback

            subprocess = {
                "update_pickup": _update_pickup,
                "get_pickup": _get_pickup,
            }
            if job.id not in subprocess:
                raise ShippingSDKError(f"Unknown pickup request job id: {job.id}")

            return subprocess[job.id](job)

        pipeline: Pipeline = request.serialize()
        response = pipeline.apply(process)

        return Deserializable(XP.bundle_xml(response), XP.to_xml)

    def cancel_pickup(self, request: Serializable) -> Deserializable:
        pickuprequest = request.serialize()
        response = http(
            url=f"{self.settings.server_url}/enab/{self.settings.customer_number}/pickuprequest/{pickuprequest}",
            trace=self.trace_as("xml"),
            method="DELETE",
            headers={
                "Accept": "application/vnd.cpc.pickuprequest+xml",
                "Authorization": f"Basic {self.settings.authorization}",
                "Accept-language": f"{self.settings.language}-CA",
            },
        )

        return Deserializable(response or "<wrapper></wrapper>", XP.to_xml)
