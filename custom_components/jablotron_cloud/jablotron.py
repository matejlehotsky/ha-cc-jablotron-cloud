"""Client for Jablotron Cloud API."""

from jablotronpy import Jablotron
from jablotronpy.exceptions import ControlActionException

from .types import JablotronServiceData


class JablotronBridge(Jablotron):
    """Extended Jablotron bridge with temperature control."""

    def set_thermo_device_temperature(
        self,
        service_id: int,
        object_device_id: str,
        temperature: float,
        service_type: str = "JA100",
    ) -> bool:
        """
        Set target temperature for a thermo device.

        :param service_id: id of service to control thermo device for
        :param object_device_id: id of thermo device to control
        :param temperature: target temperature to set
        :param service_type: type of service to control thermo device for
        """

        response = self._send_request(
            endpoint=f"{service_type}/controlThermoDevice.json",
            payload={
                "service-id": service_id,
                "control-components": [
                    {
                        "actions": {"set-temperature": temperature},
                        "component-id": object_device_id,
                    }
                ],
            },
        )

        response_body = response.json()
        response_data = response_body.get("data", {})

        for error in response_data.get("control-errors", []):
            raise ControlActionException(
                "Control action failed with unexpected error.", error
            )

        states = response_data.get("states", [])
        state = next(
            filter(lambda s: s["object-device-id"] == object_device_id, states),
            None,
        )

        return state is not None


class JablotronClient:
    """Client for Jablotron Cloud API."""

    services: dict[int, JablotronServiceData] = {}

    def __init__(
        self,
        username: str,
        password: str,
        default_pin: str | None = None,
        force_arm: bool = True,
    ) -> None:
        """Initialize Jablotron client."""

        self._username = username
        self._password = password
        self._default_pin = default_pin
        self.force_arm = force_arm

    def get_bridge(self) -> JablotronBridge:
        """Return Jablotron bridge instance."""

        bridge = JablotronBridge(self._username, self._password, self._default_pin)
        bridge.perform_login()

        return bridge
