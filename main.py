from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import subprocess
import traceback
import tempfile
import pathlib
import struct
import shutil
import time
import sys
import os

self_dir = pathlib.Path(
    sys.executable
    if getattr(sys, "frozen", False) else
    __file__
).parent


class Quit(Exception):
    pass


def ensure_cp2077_path():
    global cp2077_path
    root.status_btn["text"] = "Getting game folder..."

    if cp2077_path is None:
        cp2077_path = filedialog.askdirectory(
            parent=root,
            title='Select your "Cyberpunk 2077" game folder...'
        )

    if cp2077_path == "":
        cp2077_path = None
        raise Quit()

    cp2077_path = pathlib.Path(cp2077_path)

    if not (cp2077_path / "archive/pc/content/basegame_1_engine.archive").is_file():
        cp2077_path = None
        messagebox.showerror(
            "Invalid Folder!",
            "This doesn't look like a game folder, a required game file (archive\\pc\\content\\basegame_1_engine.archive) is missing!\n\n"
            'Make sure you\'re selecting the game *FOLDER*! The one called "Cyberpunk 2077"!'
        )
        raise Quit()


def ensure_dir_exists(path):
    path.mkdir(
        parents=True,
        exist_ok=True
    )


def ensure_temp_dir():
    root.status_btn["text"] = "Preparing..."
    shutil.rmtree(
        self_dir / "Temp",
        ignore_errors=True
    )
    ensure_dir_exists(self_dir / "Temp")


def float_to_bytes(float):
    return struct.pack("<f", float)


def run_proc(*args, **kwargs):
    return subprocess.Popen(
        [
            *args
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs
    )


def proc_log(proc):
    return str(
        proc.stdout.read(),
        encoding="utf-8"
    ).strip()


def wait_proc(proc):
    while proc.poll() is None:
        time.sleep(0.01)
        root.update()


def save_error_log(log):
    with tempfile.TemporaryFile(
        mode="w",
        prefix="BetterMinimap-Error-",
        suffix=".txt",
        delete=False
    ) as f:
        f.write(log)
        temp_files.append(f.name)
        return f.name


def setup_variables():
    root.status_btn["text"] = "Preparing..."

    veh_zooms = {
        "default": 100,
        "slight": 150,
        "medium": 200,
        "big": 250,
        "ultra": 300
    }
    ped_zooms = {
        "default": {
            25: 25,
            35: 35
        },
        "slight": {
            25: 37,
            35: 52
        },
        "medium": {
            25: 50,
            35: 70
        },
        "big": {
            25: 62,
            35: 87
        },
        "ultra": {
            25: 75,
            35: 105
        }
    }

    if root.compass_or_minimap_var.get() == "compass":
        settings["rootWidth"] = float_to_bytes(9000)
        settings["rootHeight"] = float_to_bytes(9000)
        settings["contentWidth"] = float_to_bytes(450)
        settings["contentHeight"] = float_to_bytes(999999)
        settings["borderWidth"] = float_to_bytes(0)
        settings["borderHeight"] = float_to_bytes(0)
        settings["highlightWidth"] = float_to_bytes(450)
        settings["highlightHeight"] = float_to_bytes(450)
        settings["backgroundWidth"] = float_to_bytes(0)
        settings["backgroundHeight"] = float_to_bytes(0)
        settings["marginTop"] = float_to_bytes(0)
        settings["marginRight"] = float_to_bytes(0)
        settings["visionRadiusVehicle"] = float_to_bytes(veh_zooms["default"])
        settings["visionRadiusQuestArea"] = float_to_bytes(ped_zooms["default"][25])
        settings["visionRadiusInterior"] = float_to_bytes(ped_zooms["default"][25])
        settings["visionRadiusExterior"] = float_to_bytes(ped_zooms["default"][35])
    elif root.compass_or_minimap_var.get() == "minimap":
        settings["rootWidth"] = float_to_bytes(450)
        settings["rootHeight"] = float_to_bytes(450)
        settings["contentWidth"] = float_to_bytes(450)
        settings["contentHeight"] = float_to_bytes(450)
        settings["borderWidth"] = float_to_bytes(450)
        settings["borderHeight"] = float_to_bytes(450)
        settings["highlightWidth"] = float_to_bytes(450)
        settings["highlightHeight"] = float_to_bytes(450)
        settings["backgroundWidth"] = float_to_bytes(450)
        settings["backgroundHeight"] = float_to_bytes(450)
        settings["marginTop"] = float_to_bytes(450)
        settings["marginRight"] = float_to_bytes(434)
        settings["visionRadiusVehicle"] = float_to_bytes(veh_zooms[root.veh_zoom_var.get()])
        settings["visionRadiusQuestArea"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][25])
        settings["visionRadiusInterior"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][25])
        settings["visionRadiusExterior"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][35])
        if root.bigger_minimap_var.get():
            settings["rootWidth"] = float_to_bytes(510)
            settings["rootHeight"] = float_to_bytes(510)
            settings["contentWidth"] = float_to_bytes(510)
            settings["contentHeight"] = float_to_bytes(510)
            settings["borderWidth"] = float_to_bytes(510)
            settings["borderHeight"] = float_to_bytes(510)
            settings["highlightWidth"] = float_to_bytes(510)
            settings["highlightHeight"] = float_to_bytes(510)
            settings["backgroundWidth"] = float_to_bytes(510)
            settings["backgroundHeight"] = float_to_bytes(510)
            settings["marginRight"] = float_to_bytes(500)
        if root.transparent_minimap_var.get():
            settings["backgroundWidth"] = float_to_bytes(0)
            settings["backgroundHeight"] = float_to_bytes(0)
        if root.no_minimap_border_var.get():
            settings["borderWidth"] = float_to_bytes(0)
            settings["borderHeight"] = float_to_bytes(0)


def extract_inkwidget():
    root.status_btn["text"] = "Extracting..."

    try:
        extract_proc = run_proc(
            self_dir / "WolvenKit.CLI/WolvenKit.CLI.exe", "unbundle",
            "--path", cp2077_path / "archive/pc/content/basegame_1_engine.archive",
            "--outpath", self_dir / "Temp",
            "--hash", "7622623606735548588"  # base\gameplay\gui\widgets\minimap\minimap.inkwidget
        )
        wait_proc(extract_proc)
        extract_log = proc_log(extract_proc)
    except OSError as exc:
        error = str(exc).lower()
        if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
            messagebox.showerror(
                "Extract error!",
                "WolvenKit.CLI executable is missing or corrupted!\n\n"
                "Make sure your antivirus didn't mess with it..."
            )
            raise Quit()
        else:
            raise

    if "Microsoft.NETCore.App" in extract_log:
        if messagebox.showerror(
            "Extract error!",
            "WolvenKit.CLI requires the .NET runtime and it is missing, install it and try again!\n\n"
            "Click Ok to install it now...",
            type="okcancel"
        ) == "ok":
            try:
                root.status_btn["text"] = "Installing .NET runtime..."
                dotnet_proc = run_proc(self_dir / "dotnet-runtime.exe", "/silent")
                wait_proc(dotnet_proc)
                root.after(200, install)
            except OSError as exc:
                error = str(exc).lower()
                if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
                    messagebox.showerror(
                        "Extract error!",
                        ".NET executable is missing or corrupted!\n\n"
                        "Make sure your antivirus didn't mess with it..."
                    )
                    raise Quit()
                else:
                    raise
        raise Quit()

    if not (self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget").is_file():
        if extract_log:
            error_file = save_error_log(extract_log)
            messagebox.showerror(
                "Extract error!",
                "Something went wrong extracting the minimap file!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        else:
            messagebox.showerror(
                "Extract error!",
                "Something went wrong extracting the minimap file and the installer couldn't catch the error log!\n\n"
                "Please report this on NexusMods..."
            )
        raise Quit()


def replace_inkwidget_values():
    root.status_btn["text"] = "Editing inkwidget..."

    with open(self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget", "rb") as f:
        data = f.read()

    strings_start = data.find(b"minimapFrame")
    strings_start = data.rfind(b"\x00\x00", 0, strings_start) + 2
    strings_end = data.find(b"\x00\x00", strings_start) - 1

    strings = {}
    string_index = 1
    offset = strings_start
    while offset < strings_end:
        offset_end = data.find(b"\x00", offset)
        string = str(data[offset:offset_end], encoding="utf-8")
        strings[string] = string_index
        offset = offset_end + 1
        string_index += 1

    def String(string):
        return struct.pack("<H", strings[string])

    def Type(type):
        return String(type)

    def Size(size):
        return struct.pack("<I", size)

    class Search():
        pass

    class Skip():
        def __init__(self, count):
            self.count = count

    class Value():
        def __init__(self, setting):
            self.setting = setting

    def CName(name):
        return [
            String("name"),
            Type("CName"),
            Size(6),
            String(name)
        ]

    def Vector2(name):
        return [
            String(name),
            Type("Vector2"),
            Size(31),
            Skip(1)
        ]

    def InkMargin(name):
        return [
            String(name),
            Type("inkMargin"),
            Size(31),
            Skip(1)
        ]

    def Float(name):
        return [
            String(name),
            Type("Float"),
            Size(8)
        ]

    patterns = [
        [
            *CName("Root"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("rootWidth"),
            *Float("Y"),
            Value("rootHeight")
        ],
        [
            *CName("MiniMapContainer"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("contentWidth"),
            *Float("Y"),
            Value("contentHeight")
        ],
        [
            *CName("border"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("borderWidth"),
            *Float("Y"),
            Value("borderHeight")
        ],
        [
            *CName("borderHighlight"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("highlightWidth"),
            *Float("Y"),
            Value("highlightHeight")
        ],
        [
            *CName("bgColorFiller"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("backgroundWidth"),
            *Float("Y"),
            Value("backgroundHeight")
        ],
        [
            *(CName("timeAndSMS") if "timeAndSMS" in strings else CName("unredMessagesGroup")),
            Search(),
            *InkMargin("margin"),
            *Float("top"),
            Value("marginTop"),
            *Float("right"),
            Value("marginRight")
        ],
        [
            *Float("visionRadiusVehicle"),
            Value("visionRadiusVehicle")
        ],
        [
            *Float("visionRadiusQuestArea"),
            Value("visionRadiusQuestArea")
        ],
        [
            *Float("visionRadiusInterior"),
            Value("visionRadiusInterior")
        ],
        [
            *Float("visionRadiusExterior"),
            Value("visionRadiusExterior")
        ]
    ]

    for pattern in patterns:
        search = b""
        offset = 0
        for instruction in pattern:
            if isinstance(instruction, Search):
                offset = data.find(search, offset) + len(search)
                search = b""
            elif isinstance(instruction, Skip):
                offset = data.find(search, offset) + len(search)
                search = b""
                offset += instruction.count
            elif isinstance(instruction, Value):
                offset = data.find(search, offset) + len(search)
                search = b""
                value = settings[instruction.setting]
                length = len(value)
                data = data[:offset] + value + data[offset + length:]
                offset += length
            else:
                search += instruction

    with open(self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget", "wb") as f:
        f.write(data)


def pack_archive():
    root.status_btn["text"] = "Packing..."

    try:
        pack_proc = run_proc(
            self_dir / "WolvenKit.CLI/WolvenKit.CLI.exe", "pack",
            "--path", self_dir / "Temp",
            "--outpath", self_dir / "Temp"
        )
        wait_proc(pack_proc)
        pack_log = proc_log(pack_proc)
    except OSError as exc:
        error = str(exc).lower()
        if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
            messagebox.showerror(
                "Packing error!",
                "WolvenKit.CLI executable is missing or corrupted!\n\n"
                "Make sure your antivirus didn't mess with it..."
            )
            raise Quit()
        else:
            raise

    if "Microsoft.NETCore.App" in pack_log:
        if messagebox.showerror(
            "Packing error!",
            "WolvenKit.CLI requires the .NET runtime and it is missing, install it and try again!\n\n"
            "Click Ok to install it now...",
            type="okcancel"
        ) == "ok":
            try:
                root.status_btn["text"] = "Installing .NET runtime..."
                dotnet_proc = run_proc(self_dir / "dotnet-runtime.exe", "/silent")
                wait_proc(dotnet_proc)
                root.after(200, install)
            except OSError as exc:
                error = str(exc).lower()
                if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
                    messagebox.showerror(
                        "Packing error!",
                        ".NET executable is missing or corrupted!\n\n"
                        "Make sure your antivirus didn't mess with it..."
                    )
                    raise Quit()
                else:
                    raise
        raise Quit()

    if not (self_dir / "Temp/Temp.archive").is_file():
        if pack_log:
            error_file = save_error_log(pack_log)
            messagebox.showerror(
                "Packing error!",
                "Something went wrong packing the mod archive!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        else:
            messagebox.showerror(
                "Packing error!",
                "Something went wrong packing the mod archive and the installer couldn't catch the error log!\n\n"
                "Please report this on NexusMods..."
            )
        raise Quit()


def move_to_game_dir():
    root.status_btn["text"] = "Moving to game folder..."

    ensure_dir_exists(cp2077_path / "archive/pc/mod")
    for file in (cp2077_path / "archive/pc/mod").glob("WillyJL_BetterMinimap*.archive"):
        try:
            file.unlink()
        except Exception:
            pass
    shutil.move(
        self_dir / "Temp/Temp.archive",
        cp2077_path / "archive/pc/mod/WillyJL_BetterMinimap_User.archive",
    )


def install():
    root.status_btn = root.install_btn
    update_disabled_buttons(disable_all=True)
    try:
        ensure_cp2077_path()
        ensure_temp_dir()
        setup_variables()
        extract_inkwidget()
        replace_inkwidget_values()
        pack_archive()
        move_to_game_dir()
    except Exception as exc:
        if not isinstance(exc, Quit):
            error_log = "".join(traceback.format_exception(*sys.exc_info()))
            error_file = save_error_log(error_log)
            messagebox.showerror(
                "Error!",
                "Something went wrong!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        return
    finally:
        root.status_btn["text"] = "Install!"
        update_disabled_buttons()
    messagebox.showinfo(
        "Success!",
        "Successfully installed BetterMinimap!"
    )


def uninstall():
    root.status_btn = root.uninstall_btn
    update_disabled_buttons(disable_all=True)
    try:
        ensure_cp2077_path()
        root.status_btn["text"] = "Preparing..."
        ensure_dir_exists(cp2077_path / "archive/pc/mod")
        ensure_dir_exists(cp2077_path / "engine/config/platform/pc")
        root.status_btn["text"] = "Removing mod..."
        for file in (cp2077_path / "archive/pc/mod").glob("WillyJL_BetterMinimap*.archive"):
            try:
                file.unlink()
            except Exception:
                pass
        root.status_btn["text"] = "Removing distancefix..."
        for file in (cp2077_path / "engine/config/platform/pc").glob("WillyJL_BetterMinimap*.ini"):
            try:
                file.unlink()
            except Exception:
                pass
    except Exception:
        return
    finally:
        root.status_btn["text"] = "Uninstall :("
        update_disabled_buttons()
    messagebox.showinfo(
        "Uninstalled!",
        'The mod *should* be gone, if it isn\'t then delete the file yourself at "Cyberpunk 2077\\archive\\pc\\mod"'
    )


def update_disabled_buttons(disable_all=False):
    if disable_all:
        root.compass_radio["state"] = "disabled"
        root.minimap_radio["state"] = "disabled"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_low_zoom_radio["state"] = "disabled"
        root.veh_normal_zoom_radio["state"] = "disabled"
        root.veh_high_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_low_zoom_radio["state"] = "disabled"
        root.ped_normal_zoom_radio["state"] = "disabled"
        root.ped_high_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "disabled"
        root.uninstall_btn["state"] = "disabled"
    elif root.compass_or_minimap_var.get() == "minimap":
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "normal"
        root.transparent_minimap_check["state"] = "normal"
        root.no_minimap_border_check["state"] = "normal"
        root.veh_low_zoom_radio["state"] = "normal"
        root.veh_normal_zoom_radio["state"] = "normal"
        root.veh_high_zoom_radio["state"] = "normal"
        root.veh_ultra_zoom_radio["state"] = "normal"
        root.ped_low_zoom_radio["state"] = "normal"
        root.ped_normal_zoom_radio["state"] = "normal"
        root.ped_high_zoom_radio["state"] = "normal"
        root.ped_ultra_zoom_radio["state"] = "normal"
        root.install_btn["state"] = "normal"
        root.uninstall_btn["state"] = "normal"
    elif root.compass_or_minimap_var.get() == "compass":
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_low_zoom_radio["state"] = "disabled"
        root.veh_normal_zoom_radio["state"] = "disabled"
        root.veh_high_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_low_zoom_radio["state"] = "disabled"
        root.ped_normal_zoom_radio["state"] = "disabled"
        root.ped_high_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "normal"
        root.uninstall_btn["state"] = "normal"
    else:
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_low_zoom_radio["state"] = "disabled"
        root.veh_normal_zoom_radio["state"] = "disabled"
        root.veh_high_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_low_zoom_radio["state"] = "disabled"
        root.ped_normal_zoom_radio["state"] = "disabled"
        root.ped_high_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "disabled"
        root.uninstall_btn["state"] = "normal"


def setup_gui():
    # Padding
    padding = ttk.Label(
        root,
        image=empty,
        width=0
    )
    padding.grid(
        row=0,
        column=0
    )
    # Compass or minimap
    root.compass_or_minimap_var = tk.StringVar()
    root.compass_radio = ttk.Radiobutton(
        root,
        text="Compass Only",
        variable=root.compass_or_minimap_var,
        value="compass",
        command=update_disabled_buttons,
        takefocus=False
    )
    root.compass_radio.grid(
        column=0,
        row=1,
        padx=10,
        pady=5
    )
    root.minimap_radio = ttk.Radiobutton(
        root,
        text="Minimap",
        variable=root.compass_or_minimap_var,
        value="minimap",
        command=update_disabled_buttons,
        takefocus=False
    )
    root.minimap_radio.grid(
        column=1,
        row=1,
        padx=10,
        pady=5
    )
    # Bigger minimap
    root.bigger_minimap_var = tk.BooleanVar()
    root.bigger_minimap_check = ttk.Checkbutton(
        root,
        text="Bigger Minimap + Remove Compass",
        variable=root.bigger_minimap_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.bigger_minimap_check.grid(
        column=0,
        columnspan=2,
        row=2,
        padx=10,
        pady=5
    )
    # Transparent minimap
    root.transparent_minimap_var = tk.BooleanVar()
    root.transparent_minimap_check = ttk.Checkbutton(
        root,
        text="Transparent Minimap",
        variable=root.transparent_minimap_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.transparent_minimap_check.grid(
        column=0,
        columnspan=2,
        row=3,
        padx=10,
        pady=5
    )
    # No minimap border
    root.no_minimap_border_var = tk.BooleanVar()
    root.no_minimap_border_check = ttk.Checkbutton(
        root,
        text="No  Minimap  Border",
        variable=root.no_minimap_border_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.no_minimap_border_check.grid(
        column=0,
        columnspan=2,
        row=4,
        padx=10,
        pady=5
    )
    # Vehicle zoom
    root.veh_zoom_var = tk.StringVar(None, "normal")
    root.veh_low_zoom_radio = ttk.Radiobutton(
        root,
        text="Slight Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="slight",
        state="disabled",
        takefocus=False
    )
    root.veh_low_zoom_radio.grid(
        column=2,
        row=1,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_normal_zoom_radio = ttk.Radiobutton(
        root,
        text="Medium Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="medium",
        state="disabled",
        takefocus=False
    )
    root.veh_normal_zoom_radio.grid(
        column=2,
        row=2,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_high_zoom_radio = ttk.Radiobutton(
        root,
        text="Big Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="big",
        state="disabled",
        takefocus=False
    )
    root.veh_high_zoom_radio.grid(
        column=2,
        row=3,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_ultra_zoom_radio = ttk.Radiobutton(
        root,
        text="Ultra Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="ultra",
        state="disabled",
        takefocus=False
    )
    root.veh_ultra_zoom_radio.grid(
        column=2,
        row=4,
        padx=10,
        pady=5,
        sticky="w"
    )
    # Ped zoom
    root.ped_zoom_var = tk.StringVar(None, "normal")
    root.ped_low_zoom_radio = ttk.Radiobutton(
        root,
        text="Slight On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="slight",
        state="disabled",
        takefocus=False
    )
    root.ped_low_zoom_radio.grid(
        column=3,
        row=1,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_normal_zoom_radio = ttk.Radiobutton(
        root,
        text="Medium On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="medium",
        state="disabled",
        takefocus=False
    )
    root.ped_normal_zoom_radio.grid(
        column=3,
        row=2,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_high_zoom_radio = ttk.Radiobutton(
        root,
        text="Big On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="big",
        state="disabled",
        takefocus=False
    )
    root.ped_high_zoom_radio.grid(
        column=3,
        row=3,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_ultra_zoom_radio = ttk.Radiobutton(
        root,
        text="Ultra On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="ultra",
        state="disabled",
        takefocus=False
    )
    root.ped_ultra_zoom_radio.grid(
        column=3,
        row=4,
        padx=10,
        pady=5,
        sticky="w"
    )
    # Install button
    root.install_btn = ttk.Button(
        root,
        text="Install!",
        command=install,
        state="disabled",
        takefocus=False
    )
    root.install_btn.grid(
        column=0,
        columnspan=3,
        row=5,
        padx=10,
        pady=10,
        ipady=6,
        sticky="nesw"
    )
    # Uninstall button
    root.uninstall_btn = ttk.Button(
        root,
        text="Uninstall :(",
        command=uninstall,
        takefocus=False
    )
    root.uninstall_btn.grid(
        column=3,
        row=5,
        padx=10,
        pady=10,
        ipady=6,
        sticky="nesw"
    )
    # Setup UI
    root.resizable(False, False)
    style = ttk.Style(root)
    style.theme_use("kewlthem")
    style.configure("TButton", width=0)
    root.configure(bg=style.lookup("TLabel", "background"))
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry("+%d+%d" % (x, y))


def delete_temp_files(*_):
    for file in temp_files:
        try:
            os.unlink(file)
        except Exception:
            pass


if __name__ == "__main__":
    cp2077_path = None
    settings = {}
    temp_files = []
    root = tk.Tk()
    root.title("BetterMinimap Installer")
    root.tk.eval(
        """
    set base_theme_dir TclTheme/
    package ifneeded ttk::theme::kewlthem 1.0 \
        [list source [file join $base_theme_dir kewlthem.tcl]]
    """
    )
    empty = tk.PhotoImage(height=2, width=2)
    setup_gui()
    root.install_btn.bind('<Destroy>', delete_temp_files)
    root.mainloop()
