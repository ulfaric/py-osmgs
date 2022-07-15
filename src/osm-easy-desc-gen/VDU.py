from copy import deepcopy
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Dict, List, Tuple
from bitmath import GiB

from simpy import Container, Environment

# monitoring parameters
CPU_UTIL = "cpu_utilization"
MEM_UTIL_AVE = "average_memory_utilization"
DISK_ROPS = "disk_read_ops"
DISK_WOPS = "disk_write_ops"
DISK_RBYTES = "disk_read_bytes"
DISK_WBYTES = "disk_write_bytes"
PACKETS_RBYTES = "packets_received"
PACKETS_SBYTES = "packets_sent"
Telemetries = [CPU_UTIL,MEM_UTIL_AVE,DISK_ROPS,DISK_WOPS,DISK_RBYTES,DISK_WBYTES,PACKETS_RBYTES,PACKETS_SBYTES]

# interface type
PARAVIRT = "PARAVIRT"
PCI_PT = "PCI-PASSTHROUGH"
SR_IOV = "SR-IOV"
E1000 = "E1000"
RTL8139 = "RTL8139"
PCNET = "PCNET"

class VirtualMemory(Container):
    """Virtual Memory"""

    def __init__(self, env: Environment, size: int):
        super().__init__(env, capacity=size, init=size)
        self.size = GiB(size)


class VirtualCpu(Container):
    """Virtual Cpu"""

    def __init__(self, env: Environment, num_virtual_cpu: int):
        super().__init__(env, capacity=num_virtual_cpu, init=num_virtual_cpu)
        self.num_virtual_cpu = num_virtual_cpu


class VirtualStorage(Container):
    """Virtual Storage"""

    def __init__(self, env: Environment, size: int):
        super().__init__(env, capacity=size, init=size)
        self.size = GiB(size)


class OsmEntity:
    def __init__(self) -> None:
        self._configured: bool = False

    @property
    def configured(self):
        """Check if configured"""
        return self._configured

    def __lt__(self, __o: object) -> bool:
        if hasattr(self, "_id"):
            if self._id < __o._id:
                return True
            else:
                return False
        elif hasattr(self, "_name"):
            if self._name < __o._name:
                return True
            else:
                return False

    def __eq__(self, __o: object) -> bool:
        if hasattr(self, "_id"):
            if self._id == __o._id:
                return True
            else:
                return False
        elif hasattr(self, "_name"):
            if self._name == __o._name:
                return True
            else:
                return False

    def __gt__(self, __o: object) -> bool:
        if hasattr(self, "_id"):
            if self._id > __o._id:
                return True
            else:
                return False
        elif hasattr(self, "_name"):
            if self._name > __o._name:
                return True
            else:
                return False

    def __hash__(self) -> int:
        if hasattr(self, "_id"):
            return hash(getattr(self, "_id"))
        if hasattr(self, "_name"):
            return hash(getattr(self, "_name"))


@dataclass
class VirtualComputeDesc(OsmEntity):
    """Virtual Compute Description"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._number_virtual_cpu: int = None
        self._size_virtual_memory: GiB = None

    def load(self, vcd: Dict):
        """Load Virtual Compute Description.

        Args:
            vcd (Dict): the description.

        Raises:
            RuntimeWarning: raise if it is already configured.
        """
        if self.configured:
            raise RuntimeWarning(
                "This Virtual Compute Description is already configured."
            )
        for key, value in vcd.items():
            if key == "id":
                self._id = value
            elif key == "virtual-cpu":
                self._number_virtual_cpu = value["num-virtual-cpu"]
            elif key == "virtual-memory":
                self._size_virtual_memory = GiB(value["size"])
            else:
                setattr(self, key, value)
        self._configured = True

    def configure(self, id: str, num_vcpu: int, size_mem: float, **kwargs):

        if self.configured:
            raise RuntimeWarning(
                "This Virtual Compute Description is already configured."
            )

        self._id = id
        self._number_virtual_cpu = num_vcpu
        self._size_virtual_memory = GiB(size_mem)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        yaml_repr = dict()
        yaml_repr["id"] = self.id
        yaml_repr["virtual-cpu"] = {"num-virtual-cpu": self.number_virtual_cpu}
        yaml_repr["virtual-memory"] = {"size": self.size_virtual_memory.value}

        return yaml_repr

    @property
    def number_virtual_cpu(self):
        """Get number of virtual cpu."""
        return self._number_virtual_cpu

    @property
    def size_virtual_memory(self):
        """Get size of virtual memory."""
        return self._size_virtual_memory

    @property
    def id(self):
        """Get id."""
        return self._id


@dataclass
class VirtualStorageDesc(OsmEntity):
    """Virtual Storage Description"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._size_virtual_storage: GiB = None

    def load(self, vsd: Dict):

        if self.configured:
            raise RuntimeWarning(
                "This Virtual Storage Description is already configured."
            )

        for key, value in vsd.items():
            if key == "id":
                self._id = value
            elif key == "size-of-storage":
                self._size_virtual_storage = GiB(value)
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(self, id: str, size_storage: int, **kwargs):

        if self.configured:
            raise RuntimeWarning(
                "This Virtual Storage Description is already configured."
            )

        self._id = id
        self._size_virtual_storage = GiB(size_storage)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    def yaml_repr(self) -> dict:
        """return a dictionary for yaml dumping.

        Returns:
            dict: for yaml dumping.
        """
        yaml_repr = dict()
        yaml_repr["id"] = self.id
        yaml_repr["size-of-storage"] = self.size_virtual_storage.value

        return yaml_repr

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def size_virtual_storage(self):
        """Get size of virtual storage."""
        return self._size_virtual_storage


class VDUInterface(OsmEntity):
    """VDU Interface"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._vnf_internal_cp: str = None
        self._name: str = None
        self._position: int = None
        self._ip_address: IPv4Address = None
        self._type: str = None

    def load(self, int_cp_description: dict) -> None:
        """Load Internal Connection Point Configuration from a description.

        Args:
            int_cp_description (dict): Internal connection point configuration description.

        Raises:
            RuntimeWarning: raise if it has already been configured.
        """
        if self.configured:
            raise RuntimeWarning(
                "The internal connection point has already been configured."
            )

        for key, value in int_cp_description.items():
            if key == "id":
                self._id = value
            elif key == "int-virtual-link-desc":
                self._vnf_internal_cp = value
            elif key == "virtual-network-interface-requirement":
                self._name = value[0]["name"]
                if "position" in value[0]:
                    self._position = value[0]["position"]
                if "ip-address" in value[0]:
                    self._ip_address = value[0]["ip-address"]
                self._type = value[0]["virtual-interface"]["type"]
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(
        self,
        id: str,
        position: int,
        type: str,
        ip_address: IPv4Address = None,
        name: str = None,
        vnf_internal_cp=None,
        **kwargs,
    ):
        """Configure the internal connection point.

        Args:
            id (str): id.
            position (int): position.
            type (str): type.
            name (str, optional): name. Defaults to id.
            int_vl (_type_, optional): internal virtual link. Defaults to None.
        """

        if self.configured:
            raise RuntimeWarning(
                "The internal connection point has already been configured."
            )

        self._id = id
        self._position = position
        self._type = type
        if ip_address is not None:
            self._ip_address = ip_address
        if name is not None:
            self._name = name
        else:
            self._name = self._id
        if vnf_internal_cp is not None:
            self._vnf_internal_cp = vnf_internal_cp

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._configured = True

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def vnf_internal_cp(self):
        """Get internal virtual link."""
        return self._vnf_internal_cp

    @property
    def position(self):
        """Get position."""
        return self._position

    @property
    def name(self):
        """Get name."""
        return self._name

    @property
    def type(self):
        """Get type."""
        return self._type

    @property
    def ip_address(self):
        """Get IP address."""
        return self._ip_address

    def __lt__(self, __o: object) -> bool:
        if self._position < __o._position:
            return True
        else:
            return False

    def __eq__(self, __o: object) -> bool:
        if self._position == __o._position:
            return True
        else:
            return False

    def __gt__(self, __o: object) -> bool:
        if self._position > __o._position:
            return True
        else:
            return False

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
        if self.vnf_internal_cp is not None:
            yaml_repr["int-virtual-link-desc"] = self.vnf_internal_cp
        yaml_repr["virtual-network-interface-requirement"] = list()
        yaml_repr["virtual-network-interface-requirement"].append(
            {
                "name": self.name,
                "position": self.position,
                "virtual-interface": {"type": self.type},
            }
        )
        if self.ip_address is not None:
            yaml_repr["virtual-network-interface-requirement"][0][
                "ip-address"
            ] = self.ip_address.compressed
        return yaml_repr


class MonitoringParameter(OsmEntity):
    """Monitoring Parameters"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._name: str = None
        self._performance_metric: str = None

    def load(self, mon_param_desc: Dict):
        """Configure the monitoring parameter by a description.

        Args:
            mon_param_desc (Dict): description.

        Raises:
            RuntimeWarning: raise if it is already configured.
        """

        if self._configured:
            raise RuntimeWarning("This monitoring parameter is already configured.")

        for key, value in mon_param_desc.items():
            if key == "id":
                self._id = value
            elif key == "name":
                self._name = value
            elif key == "performance-metric":
                self._performance_metric = value
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(self, id: str, performance_metric: str, name: str = None, **kwargs):
        """Configure the monitoring parameter.

        Args:
            id (str): id.
            performance_metric (str): performance metric, limited to
            name (str, optional): name. Defaults to id.

        Raises:
            RuntimeWarning: raise if it is already configured
        """

        if self._configured:
            raise RuntimeWarning("This monitoring parameter is already configured.")

        self._id = id
        self._performance_metric = performance_metric

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

        yaml_repr["id"] = self.id
        yaml_repr["name"] = self.name
        yaml_repr["performance-metric"] = self.performance_metric

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
    def performance_metric(self):
        """Get performance metric."""
        return self._performance_metric


class VDU(OsmEntity):
    """VDU"""

    def __init__(self) -> None:
        super().__init__()
        self._id: str = None
        self._name: str = None
        self._image: List[str] = list()
        self._cloud_init_file: str = None
        self._vcd: str = None
        self._vsd: List[str] = list()
        self._interfaces: List[VDUInterface] = list()
        self._telementries: List[MonitoringParameter] = list()

        self._initialized: bool = False
        self.virtual_cpu: VirtualCpu = None
        self.virtual_memory: VirtualMemory = None
        self.Virtual_storage: List[VirtualStorage] = list()

    @property
    def id(self):
        """Get id."""
        return self._id

    @property
    def image(self):
        """Get image."""
        return self._image

    @property
    def vcd(self):
        """Return Virtual Computer Descritption Id."""
        return self._vcd

    @property
    def vsd(self):
        """Return Virtual Computer Descritption Id."""
        return self._vsd

    @property
    def initialized(self):
        """Get status of initialization."""
        return self._initialized

    @property
    def telemetries(self):
        """Get telementry."""
        return self._telementries

    @property
    def telemetries_id(self):
        """Get a list o telemetries ids."""
        telemetries_id = list()
        for telemetry in self.telemetries:
            telemetries_id.append(telemetry.id)
        return telemetries_id

    @property
    def interfaces(self):
        """Get internal connection points."""
        return self._interfaces

    @property
    def cloud_init_file(self):
        """Get clould-init file."""
        return self._cloud_init_file

    @property
    def Interfaces_id(self):
        """Get a list of internal connection points' ids."""
        vdu_cp_list = list()
        for int_cp in self.interfaces:
            vdu_cp_list.append(int_cp.id)
        return vdu_cp_list

    def load(self, vdu_desc: Dict) -> None:
        """Initialize VDU from a VDU description.

        Args:
            vdu_desc (dict): VDU desccription.
        """
        if self.configured:
            raise RuntimeWarning("The VDU has already been configured.")

        for key, value in vdu_desc.items():
            if key == "id":
                self._id = value
            elif key == "cloud-init-file":
                self._cloud_init_file = value
            elif key == "name":
                self._name = value
            elif key == "sw-image-desc" or key == "image":
                self._image.append(value)
            elif key == "alternative-sw-image-desc":
                for alt_img in value:
                    self._image.append(alt_img)
            elif key == "virtual-compute-desc":
                self._vcd = value
            elif key == "virtual-storage-desc":
                for vsd in value:
                    self._vsd.append(vsd)
            elif key == "int-cpd":
                for internal_cp_decription in value:
                    internal_cp = VDUInterface()
                    internal_cp.load(internal_cp_decription)
                    self._interfaces.append(internal_cp)
            elif key == "monitoring-parameter":
                for mon_param in value:
                    metric = MonitoringParameter()
                    metric.load(mon_param)
                    self._telementries.append(metric)
            else:
                setattr(self, key, value)

        self._configured = True

    def configure(
        self,
        id: str,
        image: List[str],
        virtual_compute_desc: str,
        virtual_storage_desc: List[str],
        name: str = None,
        cloud_init_file: str = None,
        **kwargs,
    ):
        """Configure the VDU.

        Args:
            id (str): id.
            image (List[str]): image for the VDU, the first one will be primary, rest will be alternatives.
            int_cpd (List[Tuple[str, str, str]]): internal connection point, (name, type, ip-address).
            virtual_compute_desc (str): virtual compute description, only the description name.
            virtual_storage_desc (List[str]): virtual storage description, only the description name.
            telementry (List[str,str]): list of telementry to be collected, (id, metric).
            name (str, optional): name of the vdu. Defaults to id.
        """
        if self.configured:
            raise RuntimeWarning("The VDU has already been configured.")

        self._id = id
        self._image = image
        self._vcd = virtual_compute_desc
        self._vsd = virtual_storage_desc

        if name is not None:
            self._name = name

        if cloud_init_file is not None:
            self._cloud_init_file = cloud_init_file

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_telementry(self, id:str, metric:str):
        """Add a new telementry to collect.

        Args:
            telementry (Tuple[str,str]): the new telementry, (id, metric).
        """
        new_metric = MonitoringParameter()
        new_metric.configure(id=id, performance_metric=metric)
        self._telementries.append(new_metric)

    def remove_telementry(self, telementry_metric: str):
        """Remove a telementry by its metric.

        Args:
            telementry_id (str): the telementry metric.
        """
        for metric in self._telementries:
            if metric.performance_metric == telementry_metric:
                self._telementries.remove(metric)

    def addInterface(
        self,
        id: str = None,
        vnf_internal_cp: str = None,
        type: str = PARAVIRT,
        ip_address: IPv4Address = None,
        name: str = None,
    ):
        """Add a new interface to VDU.

        Args:
            id (str): id. Defaults to {vdu_id}_int_x.
            vnf_internal_cp (str): reference to VNF internal connection point.
            type (str, optional): Type. Defaults to PARAVIRT.
            ip_address (IPv4Address, optional): IP address. Defaults to None.
            name (str, optional): name. Defaults to id.
        """
        if id is None:
            id = f"{self.id}_int_{len(self._interfaces)}"
        new_interface = VDUInterface()
        if ip_address is not None:
            new_interface.configure(
                id=id,
                position=len(self._interfaces),
                type=type,
                ip_address=ip_address,
                vnf_internal_cp=vnf_internal_cp,
                name=name
            )
        else:
            new_interface.configure(
                id=id,
                position=len(self._interfaces),
                type=type,
                ip_address=ip_address,
                vnf_internal_cp=vnf_internal_cp,
                name=name
            )

        self._interfaces.append(new_interface)

    def remove_Interface(self,id:str):
        """remove a interface from VDU by id.

        Args:
            id (str): Interface id.
        """
        for interface in self._interfaces:
            if interface.id == id:
                self._interfaces.remove(interface)

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
        if self.cloud_init_file is not None:
            yaml_repr["cloud-init-file"] = self.cloud_init_file
        yaml_repr["sw-image-desc"] = self.image[0]
        if len(self.image) > 1:
            yaml_repr["alternative-sw-image-desc"] = self.image[1:-1]
        yaml_repr["int-cpd"] = list()
        for internal_cp in self.interfaces:
            yaml_repr["int-cpd"].append(internal_cp.yaml_repr())
        yaml_repr["virtual-compute-desc"] = self.vcd
        yaml_repr["virtual-storage-desc"] = self.vsd
        if len(self.telemetries)!=0:
            yaml_repr["monitoring-parameter"] = list()
            for metric in self.telemetries:
                yaml_repr["monitoring-parameter"].append(metric.yaml_repr())
        return yaml_repr
