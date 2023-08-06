import uuid
from .api_dto import ApiDto


class Twin(ApiDto):
    """
    Digital Twin item/asset declared and managed on Wizata.

    :ivar twin_id: UUID of the Digital Twin.
    :ivar hardware_id: str hardware id identifying the Asset.
    :ivar name: logical display name of the Asset.
    """

    def __init__(self, twin_id=None, hardware_id=None, name=None, parent_id=None):
        if twin_id is None:
            self.twin_id = uuid.uuid4()
        else:
            self.twin_id = twin_id
        self.hardware_id = hardware_id
        self.name = name
        self.parent_id = parent_id

    def api_id(self) -> str:
        """
        Id of the experiment (experiment_id)

        :return: string formatted UUID of the Experiment.
        """
        return str(self.twin_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "Twins"

    def from_json(self, obj):
        """
        Load the Twin entity from a dictionary.

        :param obj: Dict version of the Twin.
        """
        if "id" in obj.keys():
            self.twin_id = uuid.UUID(obj["id"])
        if "hardwareId" in obj.keys() and obj["hardwareId"] is not None:
            self.hardware_id = obj["hardwareId"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "parentId" in obj.keys() and obj["parentId"] is not None:
            self.parent_id = uuid.UUID(obj["parentId"])

    def to_json(self):
        """
        Convert the twin to a dictionary compatible to JSON format.

        :return: dictionary representation of the Twin object.
        """
        obj = {
            "id": str(self.twin_id)
        }
        if self.hardware_id is not None:
            obj["hardwareId"] = str(self.hardware_id)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.parent_id is not None:
            obj["parentId"] = str(self.parent_id)
        return obj
