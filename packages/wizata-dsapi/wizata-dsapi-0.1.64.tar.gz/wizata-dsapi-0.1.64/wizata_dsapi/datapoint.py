import uuid
from enum import Enum
from .sql_dto import SqlDto


class BusinessType(Enum):
    TELEMETRY = "telemetry"
    SET_POINTS = "setPoint"
    LOGICAL = "logical"
    MEASUREMENT = "measurement"


class DataPoint(SqlDto):
    """
    A datapoint reference a time-series tag stored on DB.

    :ivar hardware_id: The unique logical hardware Id of the datapoint.
    """

    def __init__(self,
                 datapoint_id=None,
                 hardware_id=None,
                 business_type: BusinessType = None):
        if datapoint_id is None:
            self.datapoint_id = uuid.uuid4()
        else:
            self.datapoint_id = datapoint_id
        if hardware_id is None:
            self.hardware_id = uuid.uuid4()
        else:
            self.hardware_id = hardware_id
        self.business_type = business_type

    def api_id(self) -> str:
        """
        Id of the experiment (experiment_id)

        :return: string formatted UUID of the Experiment.
        """
        return str(self.datapoint_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "DataPoints"

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.datapoint_id = uuid.UUID(obj["id"])

        if "hardwareId" in obj.keys():
            self.hardware_id = obj["hardwareId"]

        if "businessType" in obj.keys():
            self.business_type = BusinessType(str(obj["businessType"]))

    def to_json(self):
        """
        Convert the datapoint to a dictionary compatible to JSON format.

        :return: dictionary representation of the datapoint object.
        """
        obj = {
            "id": str(self.datapoint_id),
            "hardwareId": str(self.hardware_id)
        }
        if self.business_type is not None and isinstance(self.business_type, BusinessType):
            obj["businessType"] = self.business_type.value
        return obj

