from copy import deepcopy
from ipaddress import IPv4Address, IPv4Network, ip_address, ip_network
from itertools import count
from pathlib import Path
import re
from typing import Dict, List, Tuple
from bitmath import GiB


from pyvis.network import Network
from VDU import VDU, OsmEntity, Telemetries, VirtualComputeDesc, VirtualStorageDesc


class ImageDescription(OsmEntity):
    """Image description"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._name: str = None
        self._image: str = None
        self._vim_type: str = None

    def load(self, image_desc: Dict):
        """load image description.

        Args:
            image_desc (Dict): image description.

        Raises:
            RuntimeWarning: raise if it is already configured.
        """

        if self.configured:
            raise RuntimeWarning("This image description is already configured.")

        for key, value in image_desc.items():
            if key == "id":
                self._id = value
            elif key == "name":
                self._name = value
            elif key == "image":
                self._image = value
            elif key == "vim-type":
                self._vim_type = value
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(
        self, id: str, image: str, name: str = None, vim_type: str = None, **kwargs
    ):
        """Configure a image description.

        Args:
            id (str): id.
            image (str): image file name.
            name (str, optional): name. Defaults to id.
            vim_type (str, optional): vim type. Defaults to None.

        Raises:
            RuntimeWarning: if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning("This image description is already configured.")

        self._id = id
        self._image = image
        if name is not None:
            self._name = name
        else:
            self._name = self._id
        if vim_type is not None:
            self._vim_type = vim_type

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self._id
        yaml_repr["name"] = self._name
        yaml_repr["image"] = self._image
        if self._vim_type is not None:
            yaml_repr["vim_type"] = self._vim_type

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def image(self):
        """Get image."""
        return self._image

    @property
    def vim_type(self):
        """Get vim type."""
        return self._vim_type


class ExternalConnectionPoint(OsmEntity):
    """External Connection Point"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._vdu_interface: str = None
        self._vdu_id: str = None
        self._configured: bool = False

    def load(self, ext_cp_description: dict):
        """Load configurations from a description.

        Args:
            ext_cp_description (dict): external connection point description.
        """
        if self.configured:
            raise RuntimeWarning("The external connection point is already configured.")
        for key, value in ext_cp_description.items():
            if key == "id":
                self._id = value
            elif key == "int-cpd":
                self._vdu_interface = value["cpd"]
                self._vdu_id = value["vdu-id"]
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(
        self, id: str, vdu: str = None, vdu_connection_point: str = None, **kwargs
    ):
        """Config the external connection point.

        Args:
            id (str): id.
            vdu (str): VDU.
            vdu_connection_point (str): the connection point of the VDU.

        Raises:
            RuntimeWarning: raise if the external connection point is already configured.
        """
        if self.configured:
            raise RuntimeWarning("The external connection point is already configured.")
        self._id = id
        if vdu_connection_point is not None:
            self._vdu_interface = vdu_connection_point
        if vdu is not None:
            self._vdu_id = vdu
        self._configured = True

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self.id
        if (self.vdu_id is not None) and (self.vdu_interface is not None):
            yaml_repr["int-cpd"] = {"cpd": self.vdu_interface, "vdu-id": self.vdu_id}
        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def vdu_interface(self):
        """Get connection point."""
        return self._vdu_interface

    @property
    def vdu_id(self):
        """Get VDU id."""
        return self._vdu_id


class InternalConnectionPoint(OsmEntity):
    def __init__(self) -> None:
        super().__init__()
        self._id: str = None

    def load(self, int_cpd: Dict):

        if self.configured:
            raise RuntimeWarning(
                "This Internal Connection Point (Virtual Link) is already configured."
            )

        for key, value in int_cpd.items():
            if key == "id":
                self._id = value
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(self, id: str, **kwargs):
        if self.configured:
            raise RuntimeWarning(
                "This Internal Connection Point (Virtual Link) is already configured."
            )

        self._id = id

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self.id

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id


class ScalingCriteria(OsmEntity):
    def __init__(self) -> None:
        super().__init__()
        self._name: str = None
        self._scale_in_relational_operation: str = None
        self._scale_in_threshold: int = None
        self._scale_out_relational_operation: str = None
        self._scale_out_threshold: int = None
        self._vnf_monitoring_param_ref: str = None

    def load(self, scaling_criteria_description: dict):

        if self.configured:
            raise RuntimeWarning("The scaling criteria is already configured.")

        for key, value in scaling_criteria_description.items():
            if key == "name":
                self._name = value
            elif key == "scale-in-relational-operation":
                self._scale_in_relational_operation = value
            elif key == "scale-in-threshold":
                self._scale_in_threshold = value
            elif key == "scale-out-relational-operation":
                self._scale_out_relational_operation = value
            elif key == "scale-out-threshold":
                self._scale_out_threshold = value
            elif key == "vnf_cpu_util":
                self._vnf_monitoring_param_ref = value
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(
        self,
        name: str,
        monitoring_param_ref: str,
        scale_in_threshold: int = None,
        scale_out_threshold: int = None,
        **kwargs,
    ):
        """Configure the scaling policy

        Args:
            name (str): name.
            monitoring_param_ref (str): monitoring parameters reference.
            scale_in_threshold (int): scale in threshold.
            scale_out_threshold (int): scale out threshold.

        Raises:
            RuntimeWarning: _description_
        """
        if self.configured:
            raise RuntimeWarning("The scaling criteria is already configured.")

        if scale_in_threshold is not None and scale_out_threshold is not None:
            if scale_in_threshold >= scale_out_threshold:
                raise RuntimeError(
                    "The scale out threshold is less or equal to scale in threshold."
                )

        self._name = name
        self._vnf_monitoring_param_ref = monitoring_param_ref

        if scale_in_threshold is not None:
            self._scale_in_relational_operation = "LT"
            self._scale_in_threshold = scale_in_threshold

        if scale_out_threshold is not None:
            self._scale_out_relational_operation = "GT"
            self._scale_out_threshold = scale_out_threshold

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["name"] = self.name
        if self.scale_in_relational_operation is not None:
            yaml_repr[
                "scale-in-relational-operation"
            ] = self.scale_in_relational_operation
            yaml_repr["scale-in-threshold"] = self.scale_in_threshold
        if self.scale_out_relational_operation is not None:
            yaml_repr[
                "scale-out-relational-operation"
            ] = self.scale_out_relational_operation
            yaml_repr["scale-out-threshold"] = self.scale_out_threshold
        yaml_repr["vnf-monitoring-param-ref"] = self.vnf_monitoring_param_ref

        return yaml_repr

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def scale_in_relational_operation(self):
        """Get scale in operator"""
        return self._scale_in_relational_operation

    @property
    def scale_out_relational_operation(self):
        """Get scale in operator"""
        return self._scale_out_relational_operation

    @property
    def scale_in_threshold(self):
        """Get scale in threshold."""
        return self._scale_in_threshold

    @property
    def scale_out_threshold(self):
        """Get scale in threshold."""
        return self._scale_out_threshold

    @property
    def vnf_monitoring_param_ref(self):
        """Get monitoring parameter reference."""
        return self._vnf_monitoring_param_ref


class ScalingPolicy(OsmEntity):
    def __init__(self) -> None:
        self._cooldown_time: int = None
        self._name: str = None
        self._scaling_criteria: List[ScalingCriteria] = list()
        self._threshold_time: int = None
        self._scaling_type: str = None
        self._configured: bool = False

    def load(self, scaling_policy_description: dict):
        """Load configuration from a description file.

        Args:
            scaling_policy_description (dict): description file.

        Raises:
            RuntimeWarning: raise if it has already been configured.
        """

        if self.configured:
            raise RuntimeWarning("The scaling policy is already configured.")

        for key, value in scaling_policy_description.items():
            if key == "cooldown-time":
                self._cooldown_time = value
            elif key == "name":
                self._name = value
            elif key == "scaling-criteria":
                for scaling_criteria_description in value:
                    scaling_criteria = ScalingCriteria()
                    scaling_criteria.load(scaling_criteria_description)
                    self._scaling_criteria.append(scaling_criteria)
            elif key == "scaling-type":
                self._scaling_type = value
            elif key == "threshold-time":
                self._threshold_time = value
            else:
                setattr(self, key, value)

    def configure(
        self,
        name: str,
        cooldown_time: int,
        threshold_time: int,
        scale_in_out_threshold_param_ref: List[Tuple[int, int, str]],
        scaling_type: str = "automatic",
        **kwargs,
    ):
        """Config the scaling policy.

        Args:
            name (str): name.
            cooldown_time (int): cooldown time.
            threshold_time (int): threshold time.
            scale_in_out_threshold_param_ref (List[Tuple[int, int, str]]): (scale in Threshold, scale out Threshold, monitoring parameter)
            scaling_type (str, optional): scaling type. Defaults to "automatic".

        Raises:
            RuntimeWarning: raise if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning("The scaling policy is already configured.")

        self._name = name
        self._cooldown_time = cooldown_time
        self._threshold_time = threshold_time
        self._scaling_type = scaling_type

        for thresholds_param in scale_in_out_threshold_param_ref:
            try:
                scaling_criteria = ScalingCriteria()
                scaling_criteria.configure(
                    name=thresholds_param[2],
                    monitoring_param_ref=thresholds_param[2],
                    scale_in_threshold=thresholds_param[0],
                    scale_out_threshold=thresholds_param[1],
                )
                self._scaling_criteria.append(scaling_criteria)
            except Exception as e:
                print(f"Fail to configure scaling criteria {thresholds_param}, {e}")

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["cooldown-time"] = self.cooldown_time
        yaml_repr["name"] = self.name
        yaml_repr["scaling-type"] = self.scaling_type
        yaml_repr["threshold-time"] = self.threshold_time

        yaml_repr["scaling-criteria"] = list()
        for scaling_criteria in self.scaling_criteria:
            yaml_repr["scaling-criteria"].append(scaling_criteria.yaml_repr())

        return yaml_repr

    @property
    def cooldown_time(self):
        """Get cooldown time."""
        return self._cooldown_time

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def scaling_type(self):
        """Get scaling type."""
        return self._scaling_type

    @property
    def threshold_time(self):
        """Get threshold time."""
        return self._threshold_time

    @property
    def scaling_criteria(self):
        """get scaling criteria."""
        return self._scaling_criteria


class Deltas(OsmEntity):
    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._vdu_delta: List[Tuple[str, int]] = list()

    def load(self, aspect_delta_details: dict):
        """Config from a description

        Args:
            aspect_delta_details (dict): description.

        Raises:
            RuntimeWarning: raise if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning(
                "The aspect delta details have already been configured."
            )

        for key, value in aspect_delta_details.items():
            if key == "id":
                self._id = value
            elif key == "vdu-delta":
                for vdu_delta in value:
                    vdu_id = vdu_delta["id"]
                    number_of_instances = vdu_delta["number-of-instances"]
                    self._vdu_delta.append((vdu_id, number_of_instances))
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(self, id: str, vdu_delta: List[Tuple[str, int]], **kwargs):
        """Configure the VDU delta details.

        Args:
            id (str): id.
            vdu_delta (List[Tuple[str,int]]): (vdu_id,num_instances)

        Raises:
            RuntimeWarning: raise if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning(
                "The aspect delta details have already been configured."
            )

        self._id = id
        self._vdu_delta = vdu_delta

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self.id
        yaml_repr["vdu-delta"] = list()
        for vdu_delta in self.vdu_delta:
            yaml_repr["vdu-delta"].append(
                {"id": vdu_delta[0], "number-of-instances": vdu_delta[-1]}
            )
        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def vdu_delta(self):
        """Get VDU deltas."""
        return self._vdu_delta


class ScalingAspect:
    def __init__(self) -> None:
        self._id: str = None
        self._name: str = None
        self._aspect_delta_details: List[Deltas] = list()
        self._max_scale_level: int = None
        self._scaling_policy: List[ScalingPolicy] = list()
        self._configured: bool = False

        self._scale_level: int = 0

    def load(self, scaling_aspect_description: dict):
        """Configure caling aspect from a decription

        Args:
            scaling_aspect_description (dict): description.

        Raises:
            RuntimeWarning: raise if it has realdy been configured.
        """

        if self.configured:
            raise RuntimeWarning("The scaling aspect is already configured.")

        for key, value in scaling_aspect_description.items():
            if key == "aspect-delta-details":
                deltas = value["deltas"]
                for delta in deltas:
                    vdu_delta = Deltas()
                    vdu_delta.load(delta)
                    self._aspect_delta_details.append(vdu_delta)
            elif key == "id":
                self._id = value
            elif key == "max-scale-level":
                self._max_scale_level = value
            elif key == "name":
                self._name = value
            elif key == "scaling-policy":
                for scaling_policy in value:
                    s_p = ScalingPolicy()
                    s_p.load(scaling_policy)
                    self._scaling_policy.append(s_p)
            else:
                setattr(self, key, value)

    def configure(
        self,
        id: str,
        max_scale_level: int,
        vdu_deltas: List[Deltas] = None,
        scaling_policies: List[ScalingPolicy] = None,
        name: str = None,
        **kwargs,
    ):
        """Configure the scaling aspect

        Args:
            id (str): id.
            max_scale_level (int): max scale level.
            vdu_delta (List[Tuple[str, int]]): VDU delta, [(vdu_id, number_of_instances),...]
            scaling_policy (List[Tuple[str, str, int, int, int, int, str]]): Scaling policy, [(name,type,cooldowntime,threshold_time,scale_in_threshold,scale_out_threshold, monitor_parameter),...]
            name (str, optional): Name. Defaults to id.

        Raises:
            RuntimeWarning: _description_
        """

        if self.configured:
            raise RuntimeWarning("The scaling aspect is already configured.")

        self._id = id
        if name is None:
            self._name = self._id
        else:
            self._name = name
        self._max_scale_level = max_scale_level

        self._aspect_delta_details = vdu_deltas

        self._scaling_policy = scaling_policies

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self.id
        yaml_repr["name"] = self.name
        yaml_repr["max-scale-level"] = self.max_scale_level
        yaml_repr["aspect-delta-details"] = {"deltas": list()}
        for deltas in self.aspect_delta_details:
            yaml_repr["aspect-delta-details"]["deltas"].append(deltas.yaml_repr())
        yaml_repr["scaling-policy"] = list()
        for policy in self.scaling_policy:
            yaml_repr["scaling-policy"].append(policy.yaml_repr())

        return yaml_repr

    @property
    def configured(self):
        """Check if configured."""
        return self._configured

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def max_scale_level(self):
        """Get max scale level."""
        return self._max_scale_level

    @property
    def aspect_delta_details(self):
        """Get aspect delta details."""
        return self._aspect_delta_details

    @property
    def scaling_policy(self):
        """Get scaling policy."""
        return self._scaling_policy


class VirtualLinkProfile(OsmEntity):
    """Internal Virtual Link"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._cidr: IPv4Network = None
        self._descriptiion: str = None
        self._dhcp_enabled: bool = False
        self._gateway_ip: IPv4Address = None
        self._ip_version: str = None
        self._name: str = None

    def load(self, vl_profile: Dict):
        """Load Virtual Link Profile from a description.

        Args:
            vl_profile (Dict): Virtual Link Profile description.

        Raises:
            RuntimeWarning: raise if this virtual link profile is already configured.
        """

        if self.configured:
            raise RuntimeWarning("This Virtual Link Profile is already configured.")

        for key, value in vl_profile["flavour"]:
            if key == "id":
                self._id = value
            elif key == "virtual-link-protocol-data":
                self._cidr = IPv4Network(value["l3-protocol-data"]["cidr"])
                self._descriptiion = value["l3-protocol-data"]["description"]
                self._dhcp_enabled = value["l3-protocol-data"]["dhcp-enabled"]
                self._gateway_ip = IPv4Address(value["l3-protocol-data"]["gateway-ip"])
                self._ip_version = value["l3-protocol-data"]["ip-version"]
                self._name = value["l3-protocol-data"]["name"]

        self._configured = True

    def configure(
        self,
        id: str,
        cidr: IPv4Network,
        gateway_ip: IPv4Address,
        dhcp_enabled: bool,
        ip_version: str,
        desciption: str = None,
        name: str = None,
        **kwargs,
    ):
        """Configure the virtual link profile

        Args:
            id (str): id.
            cidr (str): cidr, x.x.x.x/y
            gateway_ip (str): default gate way ip, x.x.x.x
            dhcp_enabled (bool): true or false.
            ip_version (str): limited to "ipv4".
            desciption (str, optional): description. Defaults to Unknown.
            name (str, optional): name. Defaults to id.

        Raises:
            RuntimeWarning: raise if it is already configured
        """
        if self.configured:
            raise RuntimeWarning("This Virtual Link Profile is already configured.")

        self._id = id
        self._cidr = cidr
        self._gateway_ip = gateway_ip
        self._dhcp_enabled = dhcp_enabled
        self._ip_version = ip_version
        if desciption is not None:
            self._descriptiion = desciption
        else:
            self._descriptiion = "Internal Virtual Links"
        if name is not None:
            self._name = name
        else:
            self._name = self._id

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)
        yaml_repr["flavour"] = dict()
        yaml_repr["flavour"]["id"] = self.id
        yaml_repr["flavour"]["virtual-link-protocol-data"] = dict()
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"] = dict()
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "cidr"
        ] = self.cidr.compressed
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "dhcp-enabled"
        ] = self.dhcp_enabled
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "gateway-ip"
        ] = self.gateway_ip.compressed
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "ip-version"
        ] = self.ip_version
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "name"
        ] = self.name
        yaml_repr["flavour"]["virtual-link-protocol-data"]["l3-protocol-data"][
            "description"
        ] = self.description

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def description(self):
        """Get description."""
        return self._descriptiion

    @property
    def cidr(self):
        """Get cidr."""
        return self._cidr

    @property
    def dhcp_enabled(self):
        """Get dhcp setting."""
        return self._dhcp_enabled

    @property
    def gateway_ip(self):
        """Get default gateway ip."""
        return self._gateway_ip

    @property
    def ip_version(self):
        """Get ip version."""
        return self._ip_version


class VduProfile(OsmEntity):
    def __init__(self) -> None:
        super().__init__()
        self._id = None
        self._min_number_instances = None
        self._max_number_instances = None

    def load(self, vdu_profile: Dict):

        if self.configured:
            raise RuntimeWarning("This VDU Profile has already been configured.")

        for key, value in vdu_profile.items():
            if key == "id":
                self._id = value
            elif key == "min-number-of-instances":
                self._min_number_instances = value
            elif key == "max-number-of-instances":
                self._max_number_instances = value
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(self, id: str, min_num: int, max_num: int = None, **kwargs):
        """Configure the VDU profile.

        Args:
            id (str): id.
            min_num (int): min number of instances.
            max_num (int): max number of instances.

        Raises:
            RuntimeWarning: raise if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning("This VDU Profile has already been configured.")

        self._id = id
        self._min_number_instances = min_num
        self._max_number_instances = max_num

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)
        yaml_repr["id"] = self.id
        yaml_repr["min-number-of-instances"] = self.min_number_instances
        if self.max_number_instances is not None:
            yaml_repr["max-number-of_instances"] = self.max_number_instances

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def min_number_instances(self):
        """Get min number of instances."""
        return self._min_number_instances

    @property
    def max_number_instances(self):
        """Get min number of instances."""
        return self._max_number_instances


class DF(OsmEntity):
    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._vdu_profile: List[VduProfile] = list()
        self._scaling_aspect: List[ScalingAspect] = list()
        self._virtual_link_profile: List[VirtualLinkProfile] = list()

    def load(self, df_description: dict):
        """Configure df with a description.

        Args:
            df_description (dict): the description.

        Raises:
            RuntimeWarning: raise if it has been already configured.
        """

        if self.configured:
            raise RuntimeWarning("The df of this VNF has already been configured.")

        for key, value in df_description.items():
            if key == "id":
                self._id = value
            elif key == "vdu-profile":
                for vdu_profile in value:
                    new_vdu_profile = VduProfile()
                    new_vdu_profile.load(vdu_profile)
                    self._vdu_profile.append(new_vdu_profile)
            elif key == "scaling-aspect":
                for scaling_aspect_descirption in value:
                    scaling_aspect = ScalingAspect()
                    scaling_aspect.load(scaling_aspect_descirption)
                    self._scaling_aspect.append(scaling_aspect)
            elif key == "virtual-link-profile":
                vl_profile = VirtualLinkProfile()
                vl_profile.load(value)
                self._virtual_link_profile.append(vl_profile)
            else:
                setattr(self, key, value)

    def configure(
        self,
        id: str,
        vdu_profiles: List[Tuple[str, int, int]],
        scaling_aspects: List[ScalingAspect] = None,
        virtual_link_profile: List[VirtualLinkProfile] = None,
        **kwargs,
    ):
        """Configure the df

        Args:
            id (str): id
            vdu_profile (List[Tuple[str, int, int]]): vdu profile, (vdu_id, min_number_of_instances, max_number_of_instances)
            scaling_aspects (List[ScalingAspect], optional): list of scaling aspect. Defaults to None.

        """
        if self.configured:
            raise RuntimeWarning("The df of this VNF has already been configured.")

        self._id = id
        for vdu_profile in vdu_profiles:
            new_vdu_profile = VduProfile()
            new_vdu_profile.configure(vdu_profile[0], vdu_profile[1], vdu_profile[2])
        self._vdu_profile.append(new_vdu_profile)

        if scaling_aspects is not None:
            vdu_list = list()
            for vdu in self._vdu_profile:
                vdu_list.append(vdu[0])
            for scaling_aspect in scaling_aspects:
                aspect_is_valid = True
                for delta_details in scaling_aspect.aspect_delta_details:
                    for vdu_delta in delta_details.vdu_delta:
                        if vdu_list.count(vdu_delta[0]) == 0:
                            aspect_is_valid = False
                            raise RuntimeWarning(
                                f"Scaling aspect {scaling_aspect.id} - aspect delta details contain a non-existing VDU reference!"
                            )
                        else:
                            continue
                if aspect_is_valid:
                    self._scaling_aspect.append(scaling_aspect)

        if virtual_link_profile is not None:
            for vl_profile in virtual_link_profile:
                self._virtual_link_profile.append(vl_profile)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def add_scalingaspect(self, scaling_aspects: List[ScalingAspect]):
        """Add  scaling aspects.

        Args:
            scaling_aspects (List[ScalingAspect]): scaling aspects.

        Raises:
            RuntimeWarning: raise if found missing VDU
        """
        vdu_list = list()
        for vdu in self._vdu_profile:
            vdu_list.append(vdu.id)
        for scaling_aspect in scaling_aspects:
            aspect_is_valid = True
            for delta_details in scaling_aspect.aspect_delta_details:
                for vdu_delta in delta_details.vdu_delta:
                    if vdu_list.count(vdu_delta[0]) == 0:
                        aspect_is_valid = False
                        raise RuntimeWarning(
                            f"Scaling aspect {scaling_aspect.id} - aspect delta details contain a non-existing VDU reference!"
                        )
                    else:
                        continue
            if aspect_is_valid:
                self._scaling_aspect.append(scaling_aspect)

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = deepcopy(vdu_dict)
        for key, value in vdu_dict.items():
            if key.count("_") != 0 or key == "interface":
                yaml_repr.pop(key)

        yaml_repr["id"] = self.id
        yaml_repr["instantiation-level"] = list()
        yaml_repr["instantiation-level"].append(
            {"id": "default-instantiation-level", "vdu-level": list()}
        )
        if len(self.scaling_aspects) != 0:
            yaml_repr["scaling-aspect"] = list()
            for scaling_aspect in self.scaling_aspects:
                yaml_repr["scaling-aspect"].append(scaling_aspect.yaml_repr())
        yaml_repr["vdu-profile"] = list()
        for vdu in self.vdu_profile:
            yaml_repr["instantiation-level"][0]["vdu-level"].append(
                {"number-of-instances": vdu.min_number_instances, "vdu-id": vdu.id}
            )
            yaml_repr["vdu-profile"].append(vdu.yaml_repr())

        if len(self.virtual_link_profile) != 0:
            yaml_repr["virtual-link-profile"] = list()
            for vl in self.virtual_link_profile:
                yaml_repr["virtual-link-profile"].append(vl.yaml_repr())

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def vdu_profile(self):
        """Get VDU profile."""
        return self._vdu_profile

    @property
    def virtual_link_profile(self):
        """Get Virtual Link Profile."""
        return self._virtual_link_profile

    @property
    def scaling_aspects(self):
        """Get scaling aspects."""
        return self._scaling_aspect


class VNF(OsmEntity):
    """VNF"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._description: str = None
        self._product_name: str = None
        self._version: str = None

        self._df: List[DF] = list()
        self._ext_cps: List[ExternalConnectionPoint] = list()
        self._int_cps: List[InternalConnectionPoint] = list()
        self._mgmt_cp: str = None
        self._vdus: List[VDU] = list()

        self._images: List[ImageDescription] = list()
        self._virtual_compute_desc: List[VirtualComputeDesc] = list()
        self._virtual_storage_desc: List[VirtualStorageDesc] = list()

        self._visualization: Network = None

    @property
    def ext_cps(self):
        """Get external connection points."""
        return self._ext_cps

    @property
    def mgmt_cp(self):
        """Get management connection point."""
        return self._mgmt_cp

    @property
    def images(self):
        """Get images."""
        return self._images

    @property
    def version(self):
        """Get version."""
        return self._version

    @property
    def vdus(self):
        """Get VDU."""
        return self._vdus

    @property
    def product_name(self):
        """Get production name."""
        return self._product_name

    @property
    def int_cps(self):
        """Get internal connection points."""
        return self._int_cps

    @property
    def df(self):
        """Get df."""
        return self._df

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def virtual_compute_descriptions(self):
        """Get virtual compute descriptions."""
        return self._virtual_compute_desc

    @property
    def virtual_storage_descriptions(self):
        """Get virtual storage descriptions."""
        return self._virtual_storage_desc

    @property
    def ext_cps_id(self) -> List[str]:

        ext_cp_id_list = list()
        for ext_cp in self.ext_cps:
            ext_cp_id_list.append(ext_cp.id)
        return ext_cp_id_list

    @property
    def int_cps_id(self) -> List[str]:
        int_cp_id_list = list()
        for int_cp in self.int_cps:
            int_cp_id_list.append(int_cp.id)
        return int_cp_id_list

    @property
    def vdu_interfaces_id(self) -> List[str]:
        vdu_int_cp_id_list = list()
        for vdu in self.vdus:
            for int_cp in vdu.interfaces:
                vdu_int_cp_id_list.append(int_cp.id)
        return vdu_int_cp_id_list

    @property
    def vdus_id(self) -> List[str]:
        vdu_id_list = list()
        for vdu in self.vdus:
            vdu_id_list.append(vdu.id)
        return vdu_id_list

    @property
    def vdus_telemetries(self) -> List[str]:
        telemetries = list()
        for vdu in self.vdus:
            for metric in vdu.telemetries:
                telemetries.append(metric.id)
        return telemetries

    @property
    def images_id(self):
        image_list = list()
        for image in self._images:
            image_list.append(image.id)
        return image_list

    def load(self, vnf_desc: Dict):

        if self.configured:
            raise RuntimeWarning("This VNF is already configured.")

        for key, value in vnf_desc.items():
            if key == "id":
                self._id = value
            elif key == "description":
                self._description = value
            elif key == "product-name":
                self._product_name = value
            elif key == "version":
                self._version = value
            elif key == "df":
                df = DF()
                df.load(value[0])
                self._df.append(df)
            elif key == "ext-cpd":
                for ext_cp in value:
                    new_ext_cp = ExternalConnectionPoint()
                    new_ext_cp.load(ext_cp)
                    self._ext_cps.append(new_ext_cp)
            elif key == "int-virtual-link-desc":
                for int_cpd in value:
                    new_int_cp = InternalConnectionPoint()
                    new_int_cp.load(int_cpd)
                    self._int_cps.append(new_int_cp)
            elif key == "mgmt-cp":
                self._mgmt_cp = value
            elif key == "vdu":
                for vdu in value:
                    new_vdu = VDU()
                    new_vdu.load(vdu)
                    self._vdus.append(new_vdu)
            elif key == "virtual-compute-desc":
                for vcd in value:
                    new_vcd = VirtualComputeDesc()
                    new_vcd.load(vcd)
                    self._virtual_compute_desc.append(new_vcd)
            elif key == "virtual-storage-desc":
                for vsd in value:
                    new_vsd = VirtualStorageDesc()
                    new_vsd.load(vsd)
                    self._virtual_storage_desc.append(new_vsd)
            elif key == "sw-image-desc":
                for image in value:
                    new_image = ImageDescription()
                    new_image.load(image)
                    self._images.append(new_image)
            else:
                setattr(self, key, value)

        self._configured = True

    def visualization(self, detailed: bool = False):
        """Visualize the VNF"""
        self._visualization = Network(height="100%", width="100%")
        visualization = self._visualization

        if len(self.int_cps) != 0:
            for i, int_cp in enumerate(self.int_cps):
                title = "No Configuration."
                for vl_profile in self.df[0].virtual_link_profile:
                    if vl_profile.id == int_cp.id:
                        title = f"gateway: {vl_profile.gateway_ip}, network: {vl_profile.cidr}, DHCP-{vl_profile.dhcp_enabled}"
                visualization.add_node(
                    n_id=int_cp.id,
                    shape="image",
                    image="https://img.icons8.com/ios-filled/50/000000/switch.png",
                    title=title,
                    level=0,
                )

        if len(self.vdus) != 0:
            for i, vdu in enumerate(self.vdus):
                title = "Telemetry: "
                # label = None
                # for vcd in self.virtual_compute_descriptions:
                #     if vcd.id == vdu.vcd:
                #         label = f"Image:{vdu.image}\nCPU:{vcd.number_virtual_cpu}\nMEM:{vcd.size_virtual_memory}"
                for telemetry in vdu.telemetries:
                    title += f" {telemetry.id},"
                visualization.add_node(
                    n_id=vdu.id,
                    shape="image",
                    image="https://img.icons8.com/ios-filled/50/000000/google-compute-engine.png",
                    level=2,
                    title=title,
                    # label=label,
                    group=i,
                )
                for j, int_cp in enumerate(vdu.interfaces):
                    title = "DHCP"
                    if int_cp.ip_address is not None:
                        title = int_cp.ip_address.compressed
                    visualization.add_node(
                        n_id=int_cp.id,
                        shape="image",
                        image="https://img.icons8.com/external-smashingstocks-fill-lineal-smashing-stocks/67/000000/external-ethernet-networking-smashingstocks-fill-lineal-smashing-stocks.png",
                        level=1,
                        title=title,
                        group=i,
                    )
                    visualization.add_edge(source=int_cp.id, to=vdu.id, group=i)
                    if int_cp.vnf_internal_cp is not None:
                        visualization.add_edge(
                            source=int_cp.id, to=int_cp.vnf_internal_cp, group=i
                        )
        if len(self.ext_cps) != 0:
            for i, cp in enumerate(self.ext_cps):
                visualization.add_node(
                    n_id=cp.id,
                    shape="image",
                    image="https://img.icons8.com/ios-filled/50/000000/router.png",
                    level=-1,
                    group=-1,
                )
                if cp.vdu_interface is not None:
                    visualization.add_edge(source=cp.id, to=cp.vdu_interface, group=-1)

            file_name = self.product_name + ".html"
            visualization.toggle_physics(False)
            visualization.set_options(
                """
            var options = {
            "layout": {
                "hierarchical": {
                "enabled": true,
                "levelSeparation": -150,
                "direction": "RL"
                }
            }
            }
            """
            )
            visualization.save_graph(file_name)

    def create(
        self,
        id: str,
        product_name: str = None,
        verion: str = None,
        mgmt_id: str = None,
        **kwargs,
    ):
        """Create VNF with given id, product name and version.

        Args:
            id (str): id.
            product_name (str, optional): product name. Defaults to id.
            verion (str, optional): version number. Defaults to 1.0.
        """
        self._id = id
        if product_name is None:
            self._product_name = self._id
        else:
            self._product_name = product_name

        if verion is None:
            self._version = 1.0
        else:
            self._version = verion

        mgmt_cp = ExternalConnectionPoint()
        if mgmt_id is None:
            mgmt_cp.configure(id="mgmt")
        else:
            mgmt_cp.configure(id=mgmt_id)

        self._ext_cps.append(mgmt_cp)
        self._mgmt_cp = mgmt_cp.id

        self._df = [DF()]
        self._df[0]._id = "default-df"

    def add_Image(
        self, id: str, image_filepath: str, name: str = None, vim_type: str = None
    ):
        if id is None or image_filepath is None:
            raise RuntimeError("Image id and filepath can not be empty.")
        if self.images_id.count(id) != 0:
            raise RuntimeError(f"Image {id} has already been imported.")
        image_filepath = Path(image_filepath)
        image = ImageDescription()
        if name is None:
            image.configure(
                id=id, name=id, image=str(image_filepath), vim_type=vim_type
            )
        else:
            image.configure(
                id=id, name=name, image=str(image_filepath), vim_type=vim_type
            )

        self._images.append(image)

    def remove_image(self, image_id:str):
        """Remove the image description from the VNF.

        Args:
            image_id (str): id of the image description.
        """
        

    def add_ExternalConnectionPoint(
        self, id: str = None, vdu_id: str = None, vdu_cp: str = None
    ):

        if vdu_id is not None:
            vdu_id_list = self.vdus_id
            if vdu_id_list.count(vdu_id) == 0:
                raise RuntimeError("The given VDU does not belong to this VNF!")
            else:
                if vdu_cp is None:
                    raise RuntimeError(
                        f"A VDU connection point on VDU {vdu_id} must be given."
                    )
                else:
                    for vdu in self.vdus:
                        if vdu.id == vdu_id:
                            vdu_cp_list = vdu.Interfaces_id
                            if vdu_cp_list.count(vdu_cp) == 0:
                                raise RuntimeError(
                                    f"The given VDU connection point {vdu_cp} does not exist on VDU {vdu_id}"
                                )

        new_ext_cp = ExternalConnectionPoint()
        if id is None:
            new_ext_cp.configure(
                id=f"ext_{len(self.ext_cps)}", vdu=vdu_id, vdu_connection_point=vdu_cp
            )
        else:
            new_ext_cp.configure(id=id, vdu=vdu_id, vdu_connection_point=vdu_cp)

        ext_cp_list = self.ext_cps_id
        if ext_cp_list.count(new_ext_cp.id) != 0:
            raise RuntimeError(
                f"The external connection point {new_ext_cp.id} already exists."
            )
        else:
            self._ext_cps.append(new_ext_cp)
            return True

    def remove_ExternalConnectionPoint(self, ext_cp_id: str):
        """Remove the external connection point. This will also remove the VDU interface connecting to it.

        Args:
            ext_cp_id (str): id of the external connection point.
        """
        if self.ext_cps_id.count(ext_cp_id)==0:
            raise RuntimeError(f"The external connection point {ext_cp_id} does not belong to VNF {self.id}.")

        for ext_cp in self._ext_cps:
            if ext_cp.id == ext_cp_id:
                for vdu in self.vdus:
                    if vdu.id == ext_cp.vdu_id:
                        for interface in vdu._interfaces:
                            if interface.id == ext_cp.vdu_interface:
                                vdu._interfaces.remove(interface)
                                break
                        break
                self._ext_cps.remove(ext_cp)
                break
            else:
                continue
        
        return True

    def add_InternalConnectionPoint(
        self,
        id: str = None,
        ip: str = None,
        network: str = None,
        dhcp_enabled: bool = True,
    ):

        if ip is not None:
            if network is not None:
                ip: IPv4Address = ip_address(ip)
                network: IPv4Network = ip_network(network)
                new_int_vl = VirtualLinkProfile()
                new_int_vl.configure(
                    id=id,
                    cidr=network,
                    gateway_ip=list(network.hosts())[0],
                    dhcp_enabled=dhcp_enabled,
                    ip_version="ipv4",
                )
                new_int_cp = InternalConnectionPoint()
                new_int_cp.configure(id=id)
                self._int_cps.append(new_int_cp)
                self._df[0]._virtual_link_profile.append(new_int_vl)
            else:
                raise RuntimeError(f"A network must be indicated for ip address {ip}")
        else:
            if id is None:
                new_int_cp = InternalConnectionPoint()
                new_int_cp.configure(id=f"int_{len(self._int_cps)}")
                if self.int_cps_id.count(new_int_cp.id) != 0:
                    raise RuntimeError(
                        f"The internal connection point {new_int_cp.id} already exists."
                    )
                else:
                    self._int_cps.append(new_int_cp)
                return True
            else:
                new_int_cp = InternalConnectionPoint()
                new_int_cp.configure(id=id)
                if self.int_cps_id.count(new_int_cp.id) != 0:
                    raise RuntimeError(
                        f"The internal connection point {new_int_cp.id} already exists."
                    )
                else:
                    self._int_cps.append(new_int_cp)
                return True

    def remove_InternalConnectionPoint(self, int_cp_id: str):
        """Remove the internal connection point. This will also remove the VDU interface connect to it.

        Args:
            int_cp_id (str): id of the internal connection point.
        """

        int_cp_list = self.int_cps_id
        if int_cp_list.count(int_cp_id) == 0:
            raise RuntimeError(f"Cannnot found {int_cp} in VNF {self.id}")

        for int_cp in self._int_cps:
            if int_cp.id == int_cp_id:
                self._int_cps.remove(int_cp)
                break

        for int_cp_profile in self.df[0]._virtual_link_profile:
            if int_cp_profile.id == int_cp_id:
                self.df[0]._virtual_link_profile.remove(int_cp_profile)

        for vdu in self._vdus:
            for interface in vdu._interfaces:
                if interface.vnf_internal_cp == int_cp_id:
                    vdu._interfaces.remove(interface)

        return True

    def add_VDU(
        self,
        id: str,
        num_vcpu: int,
        size_memory: float,
        size_storage: List[float],
        image: List[str],
        ext_cps: List[str] = None,
        int_cps: List[str] = None,
        name: str = None,
        max_num: int = None,
        cloud_init_file: str = None,
    ):

        if ext_cps is None and int_cps is None:
            raise RuntimeError(
                f"The VDU {id} is not connected to any connection points."
            )

        new_vcd = VirtualComputeDesc()
        new_vcd.configure(id=f"{id}-compute", num_vcpu=num_vcpu, size_mem=size_memory)

        vsd_list = list()
        vsd_id_list = list()
        for size in size_storage:
            new_vsd = VirtualStorageDesc()
            new_vsd.configure(id=f"{id}-storage", size_storage=size)
            vsd_list.append(new_vsd)
            vsd_id_list.append(new_vsd.id)

        new_vdu = VDU()
        new_vdu.configure(
            id=id,
            image=image,
            virtual_compute_desc=new_vcd.id,
            virtual_storage_desc=vsd_id_list,
            cloud_init_file=cloud_init_file,
        )

        if ext_cps is not None:
            ext_cp_list = self.ext_cps_id
            for ext_cp in ext_cps:
                if ext_cp_list.count(ext_cp) == 0:
                    raise RuntimeError(f"Cannot found {ext_cp} in VNF {self.id}")

        if int_cps is not None:
            int_cp_list = self.int_cps_id
            for int_cp in int_cps:
                if int_cp_list.count(int_cp) == 0:
                    raise RuntimeError(f"Cannnot found {int_cp} in VNF {self.id}")

        if ext_cps is not None:
            for ext_cp in ext_cps:
                for cp in self.ext_cps:
                    if cp.id == ext_cp:
                        if cp._vdu_id is None:
                            cp._vdu_id = id
                            new_vdu.addInterface()
                            cp._vdu_interface = new_vdu.interfaces[-1].id
                        else:
                            raise RuntimeError(
                                f"Another VDU {cp.vdu_id} has already connected to External Connection Point {cp.id}."
                            )

        if int_cps is not None:
            for int_cp in int_cps:
                for cp in self.int_cps:
                    if int_cp == cp.id:
                        new_vdu.addInterface(vnf_internal_cp=cp.id)

        self._virtual_compute_desc.append(new_vcd)
        for new_vsd in vsd_list:
            self._virtual_storage_desc.append(new_vsd)

        self._vdus.append(new_vdu)
        new_vdu_profile = VduProfile()
        new_vdu_profile.configure(id=new_vdu.id, min_num=1, max_num=max_num)
        self.df[0].vdu_profile.append(new_vdu_profile)

    def remove_VDU(self, vdu_id: str):
        """Remove the VDU, along with any scaling aspects that envolves it.

        Args:
            vdu_id (str): id of the VDU.
        """

        vdu_list = self.vdus_id
        if vdu_list.count(vdu_id) == 0:
            raise RuntimeError(f"The {vdu_id} does not belong to this VNF.")

        vdu_telemetries = list()
        for vdu in self._vdus:
            if vdu.id == vdu_id:
                vdu_telemetries = vdu.telemetries_id
                self._vdus.remove(vdu)

        for vdu_profile in self.df[0]._vdu_profile:
            if vdu_profile.id == vdu_id:
                self.df[0]._vdu_profile.remove(vdu_profile)

        for scaling_aspect in self.df[0].scaling_aspects:
            need_removal = False
            for delta in scaling_aspect.aspect_delta_details:
                for vdu_delta in delta.vdu_delta:
                    if vdu_delta[0] == vdu_id:
                        need_removal = True
                        break
            for scaling_policy in scaling_aspect.scaling_policy:
                for criteria in scaling_policy.scaling_criteria:
                    if vdu_telemetries.count(criteria.vnf_monitoring_param_ref) != 0:
                        need_removal = True
                        break
            if need_removal:
                self.df[0]._scaling_aspect.remove(scaling_aspect)

    def assign_IP_vdu_interface(
        self, vdu_id: str, interface_id: str, ip_address: IPv4Address
    ):
        """Assign IP to a VDU's interface

        Args:
            vdu_id (str): VDU id.
            interface_id (str): Interface id.
            ip_address (IPv4Address): IPv4 address.
        """
        vdu_list = self.vdus_id
        if vdu_list.count(vdu_id) == 0:
            raise RuntimeError(f"The {vdu_id} does not belong to this VNF.")

        for vdu in self._vdus:
            if vdu.id == vdu_id:
                for interface in vdu._interfaces:
                    if interface.id == interface_id:
                        if interface.vnf_internal_cp is not None:
                            for vl_profile in self.df[0].virtual_link_profile:
                                if vl_profile.id == interface.vnf_internal_cp:
                                    if ip_address in vl_profile.cidr:
                                        interface._ip_address = ip_address
                                    else:
                                        raise RuntimeError(
                                            f"The IP address {ip_address.compressed} is not within {vl_profile.cidr.compressed}"
                                        )
                                    break
                                else:
                                    continue
                        else:
                            interface.ip_address = ip_address
                        break
                    else:
                        continue
                break
            else:
                continue

    def unassign_IP_vdu_interface(self, vdu_id: str, interface_id: str):
        """Unassign the IP from a VDU's interface.

        Args:
            vdu_id (str): id of the VDU.
            interface_id (str): id of the interface.
        """
        vdu_list = self.vdus_id
        if vdu_list.count(vdu_id) == 0:
            raise RuntimeError(f"The {vdu_id} does not belong to this VNF.")

        for vdu in self._vdus:
            if vdu.id == vdu_id:
                for interface in vdu._interfaces:
                    if interface.id == interface_id:
                        interface._ip_address = None
                        return True

        return False

    def add_vdu_telemetry(self, vdu_id: str, metrics: List[str]):
        """Add Telemetry to a VDU.

        Args:
            vdu_id (str): VDU id.
            metrics (List[str]): List of metrics.
        """
        vdu_list = self.vdus_id
        if vdu_list.count(vdu_id) == 0:
            raise RuntimeError(f"The {vdu_id} does not belong to this VNF.")

        for vdu in self.vdus:
            if vdu.id == vdu_id:
                for metric in metrics:
                    if Telemetries.count(metric) == 0:
                        raise RuntimeError(f"The metric {metric} is not available.")
                    else:
                        vdu.add_telementry(id=f"{vdu.id}_{metric}", metric=metric)
                return True
            else:
                continue

        return False

    def remove_vdu_telemetry(self, vdu_id: str, metrics: List[str]):
        """Remove vdu telemetry.

        Args:
            vdu_id (str): id of the vdu.
            metrics (List[str]): list of the telemetries.
        """
        vdu_list = self.vdus_id
        if vdu_list.count(vdu_id) == 0:
            raise RuntimeError(f"The {vdu_id} does not belong to this VNF.")

        for vdu in self.vdus:
            if vdu.id == vdu_id:
                for metric in metrics:
                    for telemetry in vdu._telementries:
                        if telemetry.id == f"{vdu.id}_{metric}":
                            vdu._telementries.remove(telemetry)
                return True
            else:
                continue

        return False

    def addScalingAspect(
        self,
        id: str,
        max_scale_level: int,
        vdu_to_scale: str,
        selected_telemetry: str,
        scale_in_threshold: int,
        scale_out_threshold: int,
        cooldown_time: int,
        threshold_time: int,
        scale: int,
    ):

        for scaling_aspect in self.df[0].scaling_aspects:
            if scaling_aspect.id == id:
                raise RuntimeError(
                    f"The scaling apsect {id} already exists in VNF {self.id}."
                )

        telemetris_list = list()
        for vdu in self.vdus:
            for telemetry in vdu.telemetries:
                telemetris_list.append(telemetry.id)
        if telemetris_list.count(selected_telemetry) == 0:
            raise RuntimeError(f"The telemetry {selected_telemetry} can not be found.")

        new_aspectDelta = Deltas()
        new_aspectDelta.configure(id=f"{id}", vdu_delta=[(vdu_to_scale, scale)])

        new_scalingPolicy = ScalingPolicy()
        new_scalingPolicy.configure(
            name=f"{id}",
            cooldown_time=cooldown_time,
            threshold_time=threshold_time,
            scale_in_out_threshold_param_ref=[
                (scale_in_threshold, scale_out_threshold, selected_telemetry)
            ],
        )

        new_scalingAspect = ScalingAspect()
        new_scalingAspect.configure(
            id=id,
            max_scale_level=max_scale_level,
            vdu_deltas=[new_aspectDelta],
            scaling_policies=[new_scalingPolicy],
        )

        self.df[0].add_scalingaspect([new_scalingAspect])

    def remove_scaling_aspect(self, scaling_aspect_id: str):
        """Remove the scaling aspect from VNF description.

        Args:
            aspect_id (str): id of the scaling aspect.
        """
        for scaling_aspect in self.df[0]._scaling_aspect:
            if scaling_aspect.id == scaling_aspect_id:
                self.df[0]._scaling_aspect.remove(scaling_aspect)
                return True

        raise RuntimeError(f"The scaling aspect {scaling_aspect_id} can not be found.")

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        vdu_dict = self.__dict__
        yaml_repr = {"vnfd": deepcopy(vdu_dict)}
        for key, value in vdu_dict.items():
            if key.count("_") != 0:
                yaml_repr["vnfd"].pop(key)

        yaml_repr["vnfd"]["id"] = self.id
        yaml_repr["vnfd"]["mgmt-cp"] = self.mgmt_cp
        yaml_repr["vnfd"]["product-name"] = self.product_name
        yaml_repr["vnfd"]["version"] = self.version

        yaml_repr["vnfd"]["df"] = list()
        for df in self.df:
            yaml_repr["vnfd"]["df"].append(df.yaml_repr())

        yaml_repr["vnfd"]["ext-cpd"] = list()
        for ext_cp in self.ext_cps:
            yaml_repr["vnfd"]["ext-cpd"].append(ext_cp.yaml_repr())

        yaml_repr["vnfd"]["sw-image-desc"] = list()
        for image in self.images:
            yaml_repr["vnfd"]["sw-image-desc"].append(image.yaml_repr())

        yaml_repr["vnfd"]["vdu"] = list()
        for vdu in self.vdus:
            yaml_repr["vnfd"]["vdu"].append(vdu.yaml_repr())

        yaml_repr["vnfd"]["virtual-compute-desc"] = list()
        for vcd in self.virtual_compute_descriptions:
            yaml_repr["vnfd"]["virtual-compute-desc"].append(vcd.yaml_repr())

        yaml_repr["vnfd"]["virtual-storage-desc"] = list()
        for vsd in self.virtual_storage_descriptions:
            yaml_repr["vnfd"]["virtual-storage-desc"].append(vsd.yaml_repr())

        return yaml_repr
