from ipaddress import IPv4Address
from bitmath import GiB
from nested_lookup import nested_lookup
import yaml
from VDU import DISK_RBYTES

from VNF import VNF

new_vnf = VNF()
with open("hackfest_multivdu_vnfd.yaml", "r") as description_file:
    vnf_description = yaml.load(description_file, yaml.Loader)
    description = nested_lookup(key="vnfd", document=vnf_description)[0]
    new_vnf.load(description)
    new_vnf.visualization()

#new_vnf.addImage(id="ubuntu20.04", image_filepath="./ISO/ubuntu20.04")
new_vnf.add_ExternalConnectionPoint(id="ext_1")
new_vnf.add_ExternalConnectionPoint(id="mgmt")
new_vnf.add_InternalConnectionPoint(
    id="internal", ip="192.168.0.1", network="192.168.0.0/24"
)
new_vnf.add_VDU(
    id="Compute-node",
    num_vcpu=4,
    size_memory=16,
    size_storage=[64],
    image=["ubuntu20.04"],
    ext_cps=["ext_1", "mgmt"],
    int_cps=["internal"],
)
new_vnf.add_VDU(
    id="Storage-node",
    num_vcpu=4,
    size_memory=16,
    size_storage=[64],
    image=["ubuntu20.04"],
    int_cps=["internal"],
)
new_vnf.add_VDU(
    id="Storage-node-backup",
    num_vcpu=4,
    size_memory=16,
    size_storage=[64],
    image=["ubuntu20.04"],
    int_cps=["internal"],
)
try:
    new_vnf.assign_IP_vdu_interface(
        vdu_id="Compute-node",
        interface_id="Compute-node_int_2",
        ip_address=IPv4Address("192.168.0.128"),
    )
except Exception as e:
    print(e)
new_vnf.add_vdu_telemetry(vdu_id="Storage-node", metrics=[DISK_RBYTES])
new_vnf.addScalingAspect(
    id="test",
    max_scale_level=1,
    vdu_to_scale="Storage-node",
    selected_telemetry=f"Storage-node_{DISK_RBYTES}",
    scale_in_threshold=100,
    scale_out_threshold=300,
    cooldown_time=120,
    threshold_time=10,
    scale=1,
)
with open(f"{new_vnf.id}_vnfd.yaml", "w") as yaml_file:
    yaml.dump(data=new_vnf.yaml_repr(),stream=yaml_file)
new_vnf.visualization()


