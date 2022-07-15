import os
from pathlib import Path
from tkinter import IntVar, StringVar, Listbox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.validation import validator, add_validation, add_numeric_validation
from ttkbootstrap.constants import *
from VDU import (
    CPU_UTIL,
    DISK_RBYTES,
    DISK_ROPS,
    DISK_WBYTES,
    DISK_WOPS,
    MEM_UTIL_AVE,
    PACKETS_RBYTES,
    PACKETS_SBYTES,
)

from VNF import VNF
import yaml
import webbrowser
from nested_lookup import nested_lookup

from paramiko import SSHClient, AutoAddPolicy

root = ttk.Window(themename="sandstone", title="OSM VNF Descriptor Generator")
root.resizable(width=False, height=False)

vnf = VNF()
cloud_init_files = list()
cloud_init_files_names = list()

vnf_id = StringVar(master=root)
vnfd_file_path = StringVar(master=root)

image_id = StringVar(master=root)
image_filepath = StringVar(master=root)

ext_cp_id = StringVar(master=root)
ext_cp_to_vdu_id = StringVar(master=root)
ext_cp_to_vdu_interface_id = StringVar(master=root)

int_cp_id = StringVar(master=root)
int_cp_ip = StringVar(master=root)
int_cp_net = StringVar(master=root)
int_cp_id = StringVar(master=root)

vdu_id = StringVar(master=root)
vcpu = StringVar(master=root, value="2")
mem_size = StringVar(master=root, value="8")
storage_size = StringVar(master=root, value="16,32")
cloud_init_file = StringVar(master=root)

aspect_id = StringVar(master=root)
max_scale_level = StringVar(master=root)
scale_delta = StringVar(master=root)

osm_client_ip = StringVar(master=root)
osm_client_user_name = StringVar(master=root)
osm_client_password = StringVar(master=root)
upload_progress = IntVar(master=root,value=0)

@validator
def number_list_validation(event):
    if event.postchangetext == "":
        return True
    else:
        for char in event.postchangetext:
            if char.isdigit() or char == "," or char == " ":
                continue
            else:
                return False
        return True


@validator
def vdu_id_validation(event):
    if event.postchangetext == "":
        return True
    else:
        if vnf.vdus_id.count(event.postchangetext) == 0:
            return False
        else:
            return True


@validator
def vdu_interface_validation(event):
    if event.postchangetext == "":
        return True
    else:
        if vnf.vdu_interfaces_id.count(event.postchangetext) == 0:
            return False
        else:
            return True


def create_vnf():
    try:
        if vnf_id.get() == "":
            raise RuntimeError("The VNF id can not be empty.")
        vnf.create(id=vnf_id.get())
        vnf.visualization()
        ext_cp_selections.insert(END, "mgmt")
        file_path = Path(os.path.abspath(f"./{vnf.id}.html"))
        webbrowser.open(url=file_path.as_uri(), new=0)
        cloud_init_files.clear()
        cloud_init_files_names.clear()
        to_modification()
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def select_vnfd():
    try:
        vnfd_file = Path(os.path.abspath(filedialog.askopenfilename()))
        vnfd_file_path.set(str(vnfd_file))
        load_vnf()
        to_modification()
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def select_cloud_init_file():
    try:
        cloud_init_file_path = Path(os.path.abspath(filedialog.askopenfilename()))
        cloud_init_file.set(str(cloud_init_file_path))
        cloud_init_files_names.append(cloud_init_file_path.stem)
        with open(cloud_init_file_path,"r") as f:
            cloud_init_files.append(f.read())
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def to_modification():
    try:
        page_1.pack_forget()
        page_2.pack(fill=BOTH, expand=True)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def load_vnf():
    try:
        description_file = open(vnfd_file_path.get(), "r")
        vnf_description = yaml.load(description_file, yaml.Loader)
        description = nested_lookup(key="vnfd", document=vnf_description)[0]
        vnf.load(description)
        vnf.visualization()
        file_path = Path(os.path.abspath(f"./{vnf.id}.html"))
        webbrowser.open(url=file_path.as_uri(), new=0)
        page_1.pack_forget()
        page_2.pack(fill=BOTH, expand=True)
        for image_id in vnf.images_id:
            image_selections.insert(END, image_id)
        for ext_cp in vnf.ext_cps_id:
            ext_cp_selections.insert(END, ext_cp)
        for int_cp in vnf.int_cps_id:
            int_cp_selections.insert(END, int_cp)
        for vdu in vnf.vdus:
            telemetry_vdu_selections.insert(END, vdu.id)
        for telemetry in vnf.vdus_telemetries:
            scaling_telemetry_selections.insert(END,telemetry)

        cloud_init_files.clear()
        cloud_init_files_names.clear()

        cloud_directory = Path(vnfd_file_path.get()).parent / "cloud_init"
        for filename in os.listdir(cloud_directory):
            cloud_init_files_names.append(filename)
            with open(os.path.join(cloud_directory, filename), 'r') as f:
                cloud_init_files.append(f.read())
        
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def import_image():
    try:
        if vnf.id is None:
            raise RuntimeError("The VNF is not initialized.")
        if image_id.get() == "":
            raise RuntimeError("The image id can not be empty.")
        if image_filepath.get() == "":
            raise RuntimeError("The image file path can not be empty.")
        vnf.add_Image(id=image_id.get(), image_filepath=image_filepath.get())
        image_selections.insert(END, image_id.get())
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def add_External_cp():
    try:
        if ext_cp_to_vdu_id.get() == "" and ext_cp_to_vdu_interface_id.get() == "":
            if ext_cp_id.get() == "":
                vnf.add_ExternalConnectionPoint()
            else:
                vnf.add_ExternalConnectionPoint(id=ext_cp_id.get())
        elif ext_cp_to_vdu_id.get() != "" and ext_cp_to_vdu_interface_id.get() != "":
            if ext_cp_id.get() == "":
                vnf.add_ExternalConnectionPoint(
                    vdu_id=ext_cp_to_vdu_id.get(),
                    vdu_cp=ext_cp_to_vdu_interface_id.get(),
                )
            else:
                vnf.add_ExternalConnectionPoint(
                    id=ext_cp_id.get(),
                    vdu_id=ext_cp_to_vdu_id.get(),
                    vdu_cp=ext_cp_to_vdu_interface_id.get(),
                )
        else:
            raise RuntimeError("Cannot found the given VDU or VDU interface.")
        ext_cp_selections.insert(END, vnf.ext_cps[-1].id)
        vnf.visualization()
        file_path = Path(os.path.abspath(f"./{vnf.id}.html"))
        webbrowser.open(url=file_path.as_uri(), new=0)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def add_Internal_cp():
    try:
        if int_cp_ip.get() == "" and int_cp_net.get() == "":
            if int_cp_id.get() == "":
                vnf.add_InternalConnectionPoint()
            else:
                vnf.add_InternalConnectionPoint(id=int_cp_id.get())
        elif int_cp_ip.get() != "" and int_cp_net.get() != "":
            if int_cp_id.get() == "":
                vnf.add_InternalConnectionPoint(
                    ip=int_cp_ip.get(), network=int_cp_net.get()
                )
            else:
                vnf.add_InternalConnectionPoint(
                    id=int_cp_id.get(), ip=int_cp_ip.get(), network=int_cp_net.get()
                )
        else:
            raise RuntimeError(
                "The default gate-way and network must be given at the same time."
            )
        int_cp_selections.insert(END, vnf.int_cps[-1].id)
        vnf.visualization()
        file_path = Path(os.path.abspath(f"./{vnf.id}.html"))
        webbrowser.open(url=file_path.as_uri(), new=0)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def add_VDU():
    try:
        if vnf.id is None:
            raise RuntimeError("The VNF is not created.")
        if vdu_id.get() == "":
            raise RuntimeError("The VDU id can not be empty")
        if (
            "invalid" in entry_vcpu.state()
            or "invalid" in entry_mem_size.state()
            or "invalid" in entry_vdu_storage.state()
        ):
            raise RuntimeError("Please check the computational configurations.")

        images = list()
        for i in image_selections.curselection():
            images.append(image_selections.get(i))
        if len(images) == 0:
            raise RuntimeError("A image must be selected.")

        ext_cps = list()
        for i in ext_cp_selections.curselection():
            ext_cps.append(ext_cp_selections.get(i))

        int_cps = list()
        for i in int_cp_selections.curselection():
            int_cps.append(int_cp_selections.get(i))

        if len(ext_cps) == 0 and len(int_cps) == 0:
            raise RuntimeError("A connection point must be selected.")

        storage_list = list()
        storage_list_str = storage_size.get().replace(" ", "").split(",")
        for disk_size in storage_list_str:
            storage_list.append(float(disk_size))

        cloud_init_file_name = None
        if cloud_init_file.get() != "":
            cloud_init_file_name = Path(cloud_init_file.get()).name

        vnf.add_VDU(
            id=vdu_id.get(),
            num_vcpu=int(vcpu.get()),
            size_memory=int(mem_size.get()),
            size_storage=storage_list,
            image=images,
            ext_cps=ext_cps,
            int_cps=int_cps,
            cloud_init_file = cloud_init_file_name
        )
        vnf.visualization()
        file_path = Path(os.path.abspath(f"./{vnf.id}.html"))
        webbrowser.open(url=file_path.as_uri(), new=0)
        image_selections.selection_clear(0, END)
        ext_cp_selections.selection_clear(0, END)
        int_cp_selections.selection_clear(0, END)
        telemetry_vdu_selections.insert(END, vdu_id.get())

    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def add_vdu_telemetry():
    try:
        selected_vdu = list()
        for i in telemetry_vdu_selections.curselection():
            selected_vdu.append(telemetry_vdu_selections.get(i))
        if len(selected_vdu) == 0:
            raise RuntimeError("A VDU must be selected.")
        else:
            vdu_telemetries = list()
            if "selected" in chk_cpu_util.state():
                vdu_telemetries.append(CPU_UTIL)
            if "selected" in chk_mem_util.state():
                vdu_telemetries.append(MEM_UTIL_AVE)
            if "selected" in chk_disk_read.state():
                vdu_telemetries.append(DISK_RBYTES)
            if "selected" in chk_disk_write.state():
                vdu_telemetries.append(DISK_WBYTES)
            if "selected" in chk_packet_in.state():
                vdu_telemetries.append(PACKETS_RBYTES)
            if "selected" in chk_packet_out.state():
                vdu_telemetries.append(PACKETS_SBYTES)
            if len(vdu_telemetries) == 0:
                raise RuntimeError("No telemetry is selected.")
            else:
                for vdu in selected_vdu:
                    vnf.add_vdu_telemetry(vdu_id=vdu, metrics=vdu_telemetries)
                    for metric in vdu_telemetries:
                        scaling_telemetry_selections.insert(END, f"{vdu}_{metric}")
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def add_scaling_aspect():
    try:
        telemtry = scaling_telemetry_selections.get(scaling_telemetry_selections.curselection())
        vdu_to_scale = None
        for vdu in vnf.vdus:
            for metric in vdu.telemetries:
                if metric.id == telemtry:
                    vdu_to_scale = vdu.id
                    break
        vnf.addScalingAspect(
            id=aspect_id.get(),
            max_scale_level=int(max_scale_level.get()),
            scale_in_threshold=scale_in_threshold.amountusedvar.get(),
            scale_out_threshold=scale_out_threshold.amountusedvar.get(),
            cooldown_time=cooldown_time.amountusedvar.get(),
            threshold_time=threshold_time.amountusedvar.get(),
            selected_telemetry=telemtry,
            vdu_to_scale=vdu_to_scale,
            scale=int(scale_delta.get())
        )
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def to_modification():
    try:
        page_1.pack_forget()
        page_3.pack_forget()
        page_4.pack_forget()
        page_2.pack(fill=BOTH, expand=True)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def to_initialization():
    try:
        page_2.pack_forget()
        page_3.pack_forget()
        page_4.pack_forget()
        page_1.pack(fill=BOTH, expand=True)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)


def to_scaling_aspect():
    try:
        page_1.pack_forget()
        page_2.pack_forget()
        page_4.pack_forget()
        page_3.pack(fill=BOTH, expand=True)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def scaling_aspect_to_modfication():
    try:
        page_1.pack_forget()
        page_3.pack_forget()
        page_4.pack_forget()
        page_2.pack(fill=BOTH, expand=True)
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def to_final():
    try:
        upload_progress.set(0)
        page_1.pack_forget()
        page_2.pack_forget()
        page_3.pack_forget()
        page_4.pack(fill=BOTH, expand=True)
        os.makedirs(Path().resolve() / f"{vnf.id}",exist_ok=True)
        with open(Path().resolve() / f"{vnf.id}/{vnf.id}_vnfd.yaml", "w+") as yaml_file:
            yaml.dump(data=vnf.yaml_repr(),stream=yaml_file)
        with open(Path().resolve() / f"{vnf.id}/{vnf.id}_vnfd.yaml", "r") as yaml_file:
            vnfd.delete("1.0",END)
            vnfd.insert(END,yaml_file.read())
        os.makedirs(Path().resolve() / f"{vnf.id}/cloud-init",exist_ok=True)
        for i in range(len(cloud_init_files_names)):
            with open(Path().resolve() / f"{vnf.id}/cloud-init/{cloud_init_files_names[i]}","w+") as f:
                f.write(cloud_init_files[i])
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)

def upload():
    try:
        upload_progress.set(0)
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=osm_client_ip.get(), username=osm_client_user_name.get(),password=osm_client_password.get())
        upload_progress.set(10)
        stdin, stdout, stderr = ssh.exec_command(f"rm -rf ~/{vnf.id}")
        if stdout.channel.recv_exit_status() == 0:
            upload_progress.set(20)
            stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{vnf.id}")
            if stdout.channel.recv_exit_status() == 0:
                upload_progress.set(30)
                with open(Path().resolve() / f"{vnf.id}/{vnf.id}_vnfd.yaml", "r") as yaml_file:
                    stdin, stdout, stderr = ssh.exec_command(f"echo \"{yaml_file.read()}\" > ~/{vnf.id}/{vnf.id}_vnfd.yaml")
                if stdout.channel.recv_exit_status() == 0:
                    upload_progress.set(50)
                    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p ~/{vnf.id}/cloud_init")
                    if stdout.channel.recv_exit_status() == 0:
                        upload_progress.set(60)
                        for i in range(len(cloud_init_files_names)):
                            stdin, stdout, stderr = ssh.exec_command(f"echo \"{cloud_init_files[i]}\" > ~/{vnf.id}/cloud_init/{cloud_init_files_names[i]}")
                            if stdout.channel.recv_exit_status() == 0:
                                continue
                            else:
                                raise RuntimeError(f"Failed to upload cloud-init file {cloud_init_files_names[i]}.")
                        stdin, stdout, stderr = ssh.exec_command(f"osm nfpkg-create {vnf.id}")
                        if stdout.channel.recv_exit_status() == 0:
                            upload_progress.set(100)
                        else:
                            print(stdout.channel.recv(nbytes=10000))
                    else:
                        raise RuntimeError(f"Can not make directory ~/{vnf.id}/cloud_int on osm client machine.")
                else:
                    raise RuntimeError(f"Can not write vnf desciption file {vnf.id}_vnfd.yaml on osm client machine.")
            else:
                raise RuntimeError(f"Can not make directory {vnf.id} on osm client machine.")
        else:
            raise RuntimeError(f"Can not remove directory {vnf.id} on osm client machine.")
    except Exception as e:
        Messagebox.ok(message=str(e), title="Error", alert=True, parent=root)




# page 1: initialize or load VNF
page_1 = ttk.Frame(master=root)
page_1.pack(fill=BOTH, expand=True)
# Initialize the VNF with default external managment interface "mgmt"
initialization_frame = ttk.Labelframe(master=page_1, text="Create", style=INFO)
initialization_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(
    master=initialization_frame, text="VNF id:", style=INFO, width=8, anchor=E
).grid(column=0, row=0, padx=5, pady=5, sticky=E)
ttk.Entry(master=initialization_frame, textvariable=vnf_id, style=INFO).grid(
    column=1, row=0, padx=5, pady=5, sticky=W
)
ttk.Button(
    master=initialization_frame, text="Create", style=INFO, command=create_vnf, width=10
).grid(column=2, row=0, padx=5, pady=5, sticky=W)
# Load vnf description.
load_frame = ttk.Labelframe(master=page_1, text="Load", style=INFO)
load_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(master=load_frame, text="VNF:", style=INFO, width=8, anchor=E).grid(
    column=0, row=0, padx=5, pady=5, sticky=E
)
ttk.Entry(master=load_frame, textvariable=vnfd_file_path, style=INFO, width=50).grid(
    column=1, row=0, padx=5, pady=5, sticky=W
)
ttk.Button(
    master=load_frame, text="Load", style=INFO, command=select_vnfd, width=10
).grid(column=2, row=0, padx=5, pady=5, sticky=W)


# page 2: Add new components.
page_2 = ttk.Frame(master=root)
step_one_frame = ttk.Labelframe(master=page_2, text="Import Images", style=INFO)
step_one_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(master=step_one_frame, text="Image id:", style=INFO, width=8, anchor=E).grid(
    column=0, row=0, padx=5, pady=5, sticky=W
)
ttk.Entry(master=step_one_frame, textvariable=image_id, style=INFO).grid(
    column=1, row=0, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_one_frame, text="File Path:", style=INFO, width=8, anchor=E).grid(
    column=0, row=1, padx=5, pady=5, sticky=W
)
ttk.Entry(master=step_one_frame, textvariable=image_filepath, style=INFO).grid(
    column=1, row=1, padx=5, pady=5, sticky=W
)
ttk.Button(
    master=step_one_frame, text="Import", style=INFO, command=import_image, width=10
).grid(column=2, row=1, padx=5, pady=5, sticky=W)

# Step-two: Add external and internal connection points.
step_two_frame = ttk.Labelframe(master=page_2, text="Add Connection Points", style=INFO)
step_two_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(master=step_two_frame, text="External Connection Point:", style=INFO).grid(
    column=0, row=0, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_two_frame, text="id:", style=INFO).grid(
    column=0, row=1, padx=5, pady=5, sticky=E
)
ttk.Entry(master=step_two_frame, textvariable=ext_cp_id, style=INFO).grid(
    column=1, row=1, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_two_frame, text="to VDU:", style=PRIMARY).grid(
    column=2, row=1, padx=5, pady=5, sticky=E
)
entry_ext_cp_vdu_id = ttk.Entry(
    master=step_two_frame, textvariable=ext_cp_to_vdu_id, style=PRIMARY
)
entry_ext_cp_vdu_id.grid(column=3, row=1, padx=5, pady=5, sticky=W)
add_validation(
    entry_ext_cp_vdu_id,
    func=vdu_id_validation,
    when="focusout",
)
ttk.Label(master=step_two_frame, text="on Interface:", style=PRIMARY).grid(
    column=4, row=1, padx=5, pady=5, sticky=E
)
ttk.Entry(
    master=step_two_frame, textvariable=ext_cp_to_vdu_interface_id, style=PRIMARY
).grid(column=5, row=1, padx=5, pady=5, sticky=W)
ttk.Button(
    master=step_two_frame, text="Add", style=INFO, command=add_External_cp, width=10
).grid(column=6, row=1, padx=5, pady=5, sticky=W)
ttk.Label(master=step_two_frame, text="Internal Connection Point:", style=INFO).grid(
    column=0, row=2, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_two_frame, text="id:", style=INFO).grid(
    column=0, row=3, padx=5, pady=5, sticky=E
)
ttk.Entry(master=step_two_frame, textvariable=int_cp_id, style=INFO).grid(
    column=1, row=3, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_two_frame, text="Default Gateway:", style=PRIMARY).grid(
    column=2, row=3, padx=5, pady=5, sticky=E
)
ttk.Entry(master=step_two_frame, textvariable=int_cp_ip, style=PRIMARY).grid(
    column=3, row=3, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_two_frame, text="Network:", style=PRIMARY).grid(
    column=4, row=3, padx=5, pady=5, sticky=E
)
ttk.Entry(master=step_two_frame, textvariable=int_cp_net, style=PRIMARY).grid(
    column=5, row=3, padx=5, pady=5, sticky=W
)
ttk.Button(
    master=step_two_frame, text="Add", style=INFO, command=add_Internal_cp, width=10
).grid(column=6, row=3, padx=5, pady=5, sticky=W)

# Step-three: Add VDUs.
step_three_frame = ttk.Labelframe(master=page_2, text="Add VDU", style=INFO)
step_three_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
step_three_sub_frame_1 = ttk.Frame(master=step_three_frame)
step_three_sub_frame_1.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(
    master=step_three_sub_frame_1, text="id:", style=INFO, width=7, anchor=E
).grid(column=0, row=0, padx=5, pady=5, sticky=E)
ttk.Entry(master=step_three_sub_frame_1, textvariable=vdu_id, style=INFO).grid(
    column=1, row=0, padx=5, pady=5, sticky=W
)
ttk.Label(master=step_three_sub_frame_1, text="vCPU:", style=INFO).grid(
    column=2, row=0, padx=5, pady=5, sticky=E
)
entry_vcpu = ttk.Entry(master=step_three_sub_frame_1, textvariable=vcpu, style=INFO)
entry_vcpu.grid(column=3, row=0, padx=5, pady=5, sticky=W)
add_numeric_validation(entry_vcpu, when="focusout")
ttk.Label(master=step_three_sub_frame_1, text="Memory(GB):", style=INFO).grid(
    column=4, row=0, padx=5, pady=5, sticky=E
)
entry_mem_size = ttk.Entry(
    master=step_three_sub_frame_1, textvariable=mem_size, style=INFO
)
entry_mem_size.grid(column=5, row=0, padx=5, pady=5, sticky=W)
add_numeric_validation(entry_mem_size, when="focusout")
ttk.Label(master=step_three_sub_frame_1, text="Storage(GB):", style=INFO).grid(
    column=6, row=0, padx=5, pady=5, sticky=E
)
entry_vdu_storage = ttk.Entry(
    master=step_three_sub_frame_1, textvariable=storage_size, style=INFO
)
entry_vdu_storage.grid(column=7, row=0, padx=5, pady=5, sticky=W)
add_validation(entry_vdu_storage, func=number_list_validation, when="focusout")
step_three_sub_frame_2 = ttk.Frame(master=step_three_frame)
step_three_sub_frame_2.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(
    master=step_three_sub_frame_2, text="Image:", style=INFO, width=7, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=NE)
image_selections_frame = ttk.Frame(master=step_three_sub_frame_2)
image_selections_frame.pack(side=LEFT)
image_selections_scrollbar = ttk.Scrollbar(
    master=image_selections_frame, orient="vertical", style=INFO
)
image_selections_scrollbar.pack(side=RIGHT)
image_selections = Listbox(
    master=image_selections_frame,
    selectmode="multiple",
    yscrollcommand=image_selections_scrollbar.set,
    exportselection=False,
)
image_selections.pack(side=LEFT, padx=5, pady=5)
image_selections_scrollbar.configure(command=image_selections.yview)
ttk.Label(
    master=step_three_sub_frame_2,
    text="External Connection Point:",
    style=INFO,
    anchor=E,
).pack(side=LEFT, padx=5, pady=5, anchor=NE)
ext_cp_selections_frame = ttk.Frame(master=step_three_sub_frame_2)
ext_cp_selections_frame.pack(side=LEFT)
ext_selections_scrollbar = ttk.Scrollbar(
    master=ext_cp_selections_frame, orient="vertical", style=INFO
)
ext_selections_scrollbar.pack(side=RIGHT)
ext_cp_selections = Listbox(
    master=ext_cp_selections_frame,
    selectmode="multiple",
    yscrollcommand=ext_selections_scrollbar.set,
    exportselection=False,
)
ext_cp_selections.pack(side=LEFT, padx=5, pady=5)
ext_selections_scrollbar.configure(command=image_selections.yview)
ttk.Label(
    master=step_three_sub_frame_2,
    text="Internal Connection Point:",
    style=INFO,
    anchor=E,
).pack(side=LEFT, padx=5, pady=5, anchor=NE)
int_cp_selections_frame = ttk.Frame(master=step_three_sub_frame_2)
int_cp_selections_frame.pack(side=LEFT)
int_selections_scrollbar = ttk.Scrollbar(
    master=int_cp_selections_frame, orient="vertical", style=INFO
)
int_selections_scrollbar.pack(side=RIGHT)
int_cp_selections = Listbox(
    master=int_cp_selections_frame,
    selectmode="multiple",
    yscrollcommand=int_selections_scrollbar.set,
    exportselection=False,
)
int_cp_selections.pack(side=LEFT, padx=5, pady=5)
int_selections_scrollbar.configure(command=image_selections.yview)
step_three_sub_frame_3 = ttk.Frame(master=step_three_frame)
step_three_sub_frame_3.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
ttk.Label(
    master=step_three_sub_frame_3, text="Cloud-init:", style=INFO, width=10, anchor=E
).grid(column=0, row=0, padx=5, pady=5, sticky=E)
ttk.Entry(master=step_three_sub_frame_3, textvariable=cloud_init_file, style=INFO, width=50).grid(
    column=1, row=0, padx=5, pady=5, sticky=W
)
ttk.Button(
    master=step_three_sub_frame_3, text="Browse", style=INFO, command=select_cloud_init_file, width=10
).grid(column=2, row=0, padx=5, pady=5, sticky=W)
ttk.Button(
    master=step_three_frame, text="Add", style=INFO, command=add_VDU, width=10
).pack(side=TOP, padx=5, pady=5, anchor=NW)
ttk.Button(
    master=page_2, text="Next>", style=INFO, command=to_scaling_aspect, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)
ttk.Button(
    master=page_2, text="<Back", style=INFO, command=to_initialization, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)

# Step-four: Add VDU telemetry.
page_3 = ttk.Frame(master=root)
step_four_frame = ttk.Labelframe(master=page_3, text="Add VDU Telemetry", style=INFO)
step_four_frame.pack(side=TOP, padx=5, pady=5, anchor=W, fill=BOTH)
step_four_subframe_1 = ttk.Frame(master=step_four_frame)
step_four_subframe_1.pack(side=LEFT, padx=5, pady=5, fill=BOTH)
ttk.Label(
    master=step_four_subframe_1, text="VDU id:", style=INFO, width=8, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=W)
telemetry_vdu_selections_frame = ttk.Frame(master=step_four_subframe_1)
telemetry_vdu_selections_frame.pack(side=LEFT, padx=5, pady=5, fill=BOTH)
telemetry_vdu_selection_scrollbar = ttk.Scrollbar(
    master=telemetry_vdu_selections_frame, orient=VERTICAL, style=INFO
)
telemetry_vdu_selections = Listbox(
    master=telemetry_vdu_selections_frame,
    selectmode=MULTIPLE,
    yscrollcommand=telemetry_vdu_selection_scrollbar.set,
    exportselection=False,
)
telemetry_vdu_selections.pack(side=LEFT, padx=5, pady=5)
telemetry_vdu_selection_scrollbar.configure(command=telemetry_vdu_selections.yview)
telemetry_vdu_selection_scrollbar.pack(side=RIGHT)

step_four_subframe_2 = ttk.Frame(master=step_four_frame)
step_four_subframe_2.pack(side=LEFT, padx=5, pady=5, fill=BOTH)
chk_cpu_util = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="CPU UTIL",
    style="info-outline-toolbutton",
    width=15,
)
chk_cpu_util.grid(row=0, column=0, padx=5, pady=5)
chk_mem_util = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="MEM UTIL",
    style="info-outline-toolbutton",
    width=15,
)
chk_mem_util.grid(row=0, column=1, padx=5, pady=5)
chk_disk_read = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="DISK READ",
    style="info-outline-toolbutton",
    width=15,
)
chk_disk_read.grid(row=0, column=2, padx=5, pady=5)
chk_disk_write = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="DISK WRITE",
    style="info-outline-toolbutton",
    width=15,
)
chk_disk_write.grid(row=1, column=0, padx=5, pady=5)
chk_packet_in = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="PACKET IN",
    style="info-outline-toolbutton",
    width=15,
)
chk_packet_in.grid(row=1, column=1, padx=5, pady=5)
chk_packet_out = ttk.Checkbutton(
    master=step_four_subframe_2,
    text="PACKET OUT",
    style="info-outline-toolbutton",
    width=15,
)
chk_packet_out.grid(row=1, column=2, padx=5, pady=5)
ttk.Button(
    master=step_four_subframe_2,
    text="Add",
    style=INFO,
    width=10,
    command=add_vdu_telemetry,
).grid(row=2, column=0, padx=5, pady=5, sticky=W)

step_five_frame = ttk.Labelframe(master=page_3, text="Add Scaling Aspects", style=INFO)
step_five_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH)
step_five_subframe_1 = ttk.Frame(master=step_five_frame)
step_five_subframe_1.pack(side=TOP, padx=5, pady=5, anchor=W)
ttk.Label(
    master=step_five_subframe_1, text="Aspect id:", style=INFO, width=9, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=E)
ttk.Entry(master=step_five_subframe_1, textvariable=aspect_id, style=INFO).pack(
    side=LEFT, padx=5, pady=5, anchor=W
)
ttk.Label(
    master=step_five_subframe_1, text="Max Scale Level:", style=INFO, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=E)
ttk.Entry(master=step_five_subframe_1, textvariable=max_scale_level, style=INFO).pack(
    side=LEFT, padx=5, pady=5, anchor=W
)
ttk.Label(master=step_five_subframe_1, text="Delta:", style=INFO, anchor=E).pack(
    side=LEFT, padx=5, pady=5, anchor=E
)
ttk.Entry(master=step_five_subframe_1, textvariable=scale_delta, style=INFO).pack(
    side=LEFT, padx=5, pady=5, anchor=W
)
ttk.Button(
    master=step_five_subframe_1,
    text="Add",
    style=INFO,
    width=10,
    command=add_scaling_aspect,
).pack(side=RIGHT, padx=5, pady=5, anchor=E)
step_five_subframe_2 = ttk.Frame(master=step_five_frame)
step_five_subframe_2.pack(side=TOP, padx=5, pady=5)
scaling_vdu_selections_frame = ttk.Frame(master=step_five_subframe_2)
scaling_vdu_selections_frame.grid(row=0, column=0)
ttk.Label(
    master=scaling_vdu_selections_frame, text="VDU Telemetries:", style=INFO, anchor=E
).pack(side=TOP, padx=5, pady=5, anchor=W)
scaling_vdu_selections_scrollbar = ttk.Scrollbar(
    master=scaling_vdu_selections_frame, orient=VERTICAL, style=INFO
)
scaling_telemetry_selections = Listbox(
    master=scaling_vdu_selections_frame,
    selectmode=SINGLE,
    yscrollcommand=scaling_vdu_selections_scrollbar.set,
    exportselection=False,
)
scaling_telemetry_selections.pack(side=LEFT, padx=5, pady=5)
scaling_vdu_selections_scrollbar.configure(command=telemetry_vdu_selections.yview)
scaling_vdu_selections_scrollbar.pack(side=RIGHT)
scale_in_threshold = ttk.Meter(
    master=step_five_subframe_2,
    subtext="Scale-in Threshold",
    amounttotal=100,
    amountused=0,
    metertype=SEMI,
    style=INFO,
    interactive=True,
)
scale_in_threshold.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
scale_out_threshold = ttk.Meter(
    master=step_five_subframe_2,
    subtext="Scale-out Threshold",
    amounttotal=100,
    amountused=0,
    metertype=SEMI,
    style=INFO,
    interactive=True,
)
scale_out_threshold.grid(row=0, column=3, padx=5, pady=5, columnspan=2)
threshold_time = ttk.Meter(
    master=step_five_subframe_2,
    subtext="Threshold Time",
    textright="s",
    amounttotal=100,
    amountused=0,
    metertype=SEMI,
    style=INFO,
    interactive=True,
)
threshold_time.grid(row=0, column=5, padx=5, pady=5, columnspan=2)
cooldown_time = ttk.Meter(
    master=step_five_subframe_2,
    subtext="Cooldown Time",
    textright="s",
    amounttotal=100,
    amountused=0,
    metertype=SEMI,
    style=INFO,
    interactive=True,
)
cooldown_time.grid(row=0, column=7, padx=5, pady=5, columnspan=2)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=scale_in_threshold.amountusedvar,
    style=INFO,
    width=5,
).grid(row=1, column=1, padx=5, pady=5, sticky=E)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=scale_in_threshold.amounttotalvar,
    style=INFO,
    width=5,
).grid(row=1, column=2, padx=5, pady=5, sticky=W)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=scale_out_threshold.amountusedvar,
    style=INFO,
    width=5,
).grid(row=1, column=3, padx=5, pady=5, sticky=E)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=scale_out_threshold.amounttotalvar,
    style=INFO,
    width=5,
).grid(row=1, column=4, padx=5, pady=5, sticky=W)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=threshold_time.amountusedvar,
    style=INFO,
    width=5,
).grid(row=1, column=5, padx=5, pady=5, sticky=E)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=threshold_time.amounttotalvar,
    style=INFO,
    width=5,
).grid(row=1, column=6, padx=5, pady=5, sticky=W)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=cooldown_time.amountusedvar,
    style=INFO,
    width=5,
).grid(row=1, column=7, padx=5, pady=5, sticky=E)
ttk.Entry(
    master=step_five_subframe_2,
    textvariable=cooldown_time.amounttotalvar,
    style=INFO,
    width=5,
).grid(row=1, column=8, padx=5, pady=5, sticky=W)
ttk.Button(
    master=page_3, text="Next>", style=INFO, command=to_final, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)
ttk.Button(
    master=page_3, text="<Back", style=INFO, command=scaling_aspect_to_modfication, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)


page_4 = ttk.Frame(master=root)
vnfd = ttk.ScrolledText(master=page_4)
vnfd.pack(side=TOP,padx=5,pady=5, fill=BOTH)
page_4_sub_frame_1 = ttk.Frame(master=page_4)
page_4_sub_frame_1.pack(side=TOP, padx=5,pady=5, fill=BOTH)
ttk.Label(
    master=page_4_sub_frame_1, text="OSM Client IP:", style=INFO, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=E)
ttk.Entry(
    master=page_4_sub_frame_1,
    textvariable=osm_client_ip,
    style=INFO,
).pack(side=LEFT,padx=5,pady=5)
ttk.Label(
    master=page_4_sub_frame_1, text="User name:", style=INFO, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=E)
ttk.Entry(
    master=page_4_sub_frame_1,
    textvariable=osm_client_user_name,
    style=INFO,
).pack(side=LEFT,padx=5,pady=5)
ttk.Label(
    master=page_4_sub_frame_1, text="Password:", style=INFO, anchor=E
).pack(side=LEFT, padx=5, pady=5, anchor=E)
ttk.Entry(
    master=page_4_sub_frame_1,
    textvariable=osm_client_password,
    style=INFO,
    show="*"
).pack(side=LEFT,padx=5,pady=5)
ttk.Progressbar(master=page_4,maximum=100,orient=HORIZONTAL,variable=upload_progress,style=INFO).pack(side=TOP,padx=5,pady=5,fill=BOTH)
ttk.Button(
    master=page_4, text="Upload", style=INFO, command=upload, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)
ttk.Button(
    master=page_4, text="<Back", style=INFO, command=to_scaling_aspect, width=10
).pack(side=RIGHT, padx=5, pady=5, anchor=NW)

root.mainloop()
