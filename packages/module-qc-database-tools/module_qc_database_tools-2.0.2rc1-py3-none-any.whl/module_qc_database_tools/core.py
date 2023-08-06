import copy
import json
import logging
import math
from pathlib import Path

import pandas as pd
from rich.logging import RichHandler

from module_qc_database_tools.utils import chip_serial_number_to_uid

log = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)


class Module:
    """
    Module class.
    """

    def __init__(self, client, serial_number, name=None):
        self.client = client
        self.serial_number = serial_number
        self.name = name if name else self.serial_number
        self.module = client.get("getComponent", json={"component": serial_number})
        self.bare_modules = []
        for child in self.module["children"]:
            if child["componentType"]["code"] == "BARE_MODULE":
                self.bare_modules.append(
                    client.get(
                        "getComponent",
                        json={"component": child["component"]["serialNumber"]},
                    )
                )
        self.chips = []
        for bare_module in self.bare_modules:
            for child in bare_module["children"]:
                if child["componentType"]["code"] == "FE_CHIP":
                    self.chips.append(
                        Chip(
                            client,
                            child["component"]["serialNumber"],
                            module_name=self.name,
                        )
                    )
        if len(self.bare_modules) == 3 and len(self.chips) == 3:
            self.module_type = "triplet"
            log.info("triplet %s initiated.", self.serial_number)
        else:
            self.module_type = "quad"
            log.info("quad module %s initiated.", self.serial_number)

    def generate_config(self, chip_template, layer_config, suffix, version):
        """
        Generate module config.
        """
        log.info(
            "generating module config for module %s with %s",
            self.serial_number,
            layer_config,
        )

        configs = {"module": {"chipType": "RD53B", "chips": []}, "chips": []}

        for chip_index, chip in enumerate(self.chips):
            if self.module_type == "triplet":
                rx = [2, 1, 0][chip_index]
            else:
                rx = [2, 1, 0, 3][chip_index]

            try:
                configs["chips"].append(
                    chip.generate_config(
                        copy.deepcopy(
                            chip_template
                        ),  # NB: make sure we copy as Chip::generate_config modifies this in-place
                        chip_index,
                        layer_config,
                        self.module_type,
                        suffix=suffix,
                        version=version,
                    )
                )
            except RuntimeError as snake:
                log.warning(snake)
                continue

            # relative path: e.g. L2_warm/0x15499_L2_warm.json
            chip_config_path = (
                Path(f"{layer_config}{'_'+suffix if suffix else ''}")
                / f"{chip.uid}_{layer_config}{'_'+suffix if suffix else ''}.json"
            )

            configs["module"]["chips"].append(
                {
                    "config": str(chip_config_path),
                    "path": "relToCon",
                    "tx": 0,
                    "rx": rx,
                    "enable": 1,
                    "locked": 0,
                }
            )

        return configs


class Chip:
    """
    Chip class.
    """

    def __init__(self, client, serial_number, module_name=None):
        self.client = client
        self.serial_number = serial_number
        self.uid = chip_serial_number_to_uid(serial_number)
        self.module_name = module_name or self.serial_number
        self.chip = client.get(
            "getComponent", json={"component": serial_number, "noEosToken": False}
        )
        self.attachments = list(self.chip["attachments"])
        self.test_run = None

        log.info("chip %s initiated.", self.uid)

    def get_latest_configs(self, item):
        """use title for filename: 'title': '0x12345_<layer_config>_<suffix>.json'"""
        if item.get("type") == "eos":
            infile = self.client.get(item["url"])
        else:
            infile = self.client.get(
                "uu-app-binarystore/getBinaryData", json={"code": item["code"]}
            )

        with Path(infile.filename).open(mode="r", encoding="UTF-8") as fsnake:
            return json.loads(fsnake.read())

    def load_wafer_probing_data(self):
        """
        Load chip wafer probing data.
        """
        test_id = None
        tests = pd.DataFrame(self.chip["tests"])
        if len(tests[tests["code"] == "FECHIP_TEST"]) > 0:
            test_id = tests[tests["code"] == "FECHIP_TEST"]["testRuns"].iloc[-1][-1][
                "id"
            ]
        if not test_id:
            msg = (
                f"No wafer probing data in production DB for chip {self.serial_number}!"
            )
            raise RuntimeError(msg)
        self.test_run = TestRun(self.client, test_id)

    def generate_config(
        self,
        chip_template,
        chip_index,
        layer_config,
        module_type,
        suffix="",
        version="latest",
    ):
        """
        Generate chip config.
        """
        if version == "latest" and len(self.attachments) >= 3:
            checklist = [".json", layer_config, suffix]
            for item in self.attachments:
                if all(check in item["title"] for check in checklist):
                    log.info(
                        "Latest chip configs found for chip %s %s %s!",
                        self.uid,
                        layer_config,
                        suffix,
                    )
                    try:
                        return self.get_latest_configs(item)
                    except RuntimeError as esnake:
                        log.warning(
                            "Unable to find latest config: %s. Make sure all sets of configs are present in the database.",
                            esnake,
                        )
                        continue
                else:
                    log.warning(
                        "No layer_config %s or suffix %s found in %s",
                        layer_config,
                        suffix,
                        item["title"],
                    )
                    continue
        elif version == "TESTONWAFER" or len(self.attachments) == 0:
            log.info(
                "Generating chip config for chip %s with %s from wafer probing.",
                self.uid,
                layer_config,
            )
            power_config = "LP" if suffix == "LP" else layer_config

            chip_template["RD53B"]["GlobalConfig"]["DiffPreComp"] = {
                "R0": 350,
                "R0.5": 350,
                "L0": 350,
                "L1": 350,
                "L2": 350,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampL"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampM"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampR"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampT"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampTL"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffPreampTR"] = {
                "R0": 900,
                "R0.5": 900,
                "L0": 900,
                "L1": 730,
                "L2": 550,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["DiffVff"] = {
                "R0": 150,
                "R0.5": 150,
                "L0": 150,
                "L1": 150,
                "L2": 60,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["EnCoreCol0"] = {
                "R0": 65535,
                "R0.5": 65535,
                "L0": 65535,
                "L1": 65535,
                "L2": 65535,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["EnCoreCol1"] = {
                "R0": 65535,
                "R0.5": 65535,
                "L0": 65535,
                "L1": 65535,
                "L2": 65535,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["EnCoreCol2"] = {
                "R0": 65535,
                "R0.5": 65535,
                "L0": 65535,
                "L1": 65535,
                "L2": 65535,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["GlobalConfig"]["EnCoreCol3"] = {
                "R0": 63,
                "R0.5": 63,
                "L0": 63,
                "L1": 63,
                "L2": 63,
                "LP": 0,
            }[power_config]
            chip_template["RD53B"]["Parameter"]["Name"] = self.uid

            if module_type == "triplet":
                chip_template["RD53B"]["Parameter"]["ChipId"] = chip_index + 1
                chip_template["RD53B"]["GlobalConfig"]["AuroraActiveLanes"] = {
                    "R0": 7,
                    "R0.5": 3,
                    "L0": 15,
                }[
                    layer_config
                ]  ## TODO: add source for R0 and R0.5
                # chip_template["RD53B"]["GlobalConfig"]["MonitorEnable"] = 0
                # chip_template["RD53B"]["GlobalConfig"]["MonitorV"] = 63
                for index in range(4):
                    chip_template["RD53B"]["GlobalConfig"][
                        f"DataMergeOutMux{index}"
                    ] = (0 + index) % 4
                chip_template["RD53B"]["GlobalConfig"]["SerEnLane"] = {
                    "R0": 7,
                    "R0.5": 3,
                    "L0": 15,
                }[layer_config]
            else:
                chip_template["RD53B"]["Parameter"]["ChipId"] = 12 + chip_index
                chip_template["RD53B"]["GlobalConfig"]["AuroraActiveLanes"] = 1
                for index in range(4):
                    chip_template["RD53B"]["GlobalConfig"][
                        f"DataMergeOutMux{index}"
                    ] = ([2, 0, 1, 0][chip_index] + index) % 4
                chip_template["RD53B"]["GlobalConfig"]["SerEnLane"] = [4, 1, 8, 1][
                    chip_index
                ]

            if not self.test_run:
                self.load_wafer_probing_data()
            if self.test_run:
                chip_template["RD53B"]["GlobalConfig"][
                    "SldoTrimA"
                ] = self.test_run.get_result("VDDA_TRIM")
                chip_template["RD53B"]["GlobalConfig"][
                    "SldoTrimD"
                ] = self.test_run.get_result("VDDD_TRIM")
                chip_template["RD53B"]["Parameter"]["ADCcalPar"][0] = (
                    self.test_run.get_result("ADC_OFFSET") * 1000
                )
                chip_template["RD53B"]["Parameter"]["ADCcalPar"][1] = (
                    self.test_run.get_result("ADC_SLOPE") * 1000
                )
                chip_template["RD53B"]["Parameter"][
                    "InjCap"
                ] = self.test_run.get_result("InjectionCapacitance") * (10**15)

                # For transistor sensors calibration, the ideality factor is calculated following the presentation:
                # https://indico.cern.ch/event/1011941/contributions/4278988/attachments/2210633/3741190/RD53B_calibatrion_sensor_temperature.pdf
                e_charge = 1.602e-19
                kB = 1.38064852e-23
                PC_NTC = self.test_run.get_result("PC_NTC") + 273
                DeltaT = 2  # 2 degree difference between PC NTC and transistor sensors
                chip_template["RD53B"]["Parameter"]["NfDSLDO"] = (
                    self.test_run.get_result("TEMPERATURE_D")
                    * e_charge
                    / (kB * math.log(15) * (PC_NTC + DeltaT))
                )
                chip_template["RD53B"]["Parameter"]["NfASLDO"] = (
                    self.test_run.get_result("TEMPERATURE_A")
                    * e_charge
                    / (kB * math.log(15) * (PC_NTC + DeltaT))
                )
                chip_template["RD53B"]["Parameter"]["NfACB"] = (
                    self.test_run.get_result("TEMPERATURE_C")
                    * e_charge
                    / (kB * math.log(15) * (PC_NTC + DeltaT))
                )

                chip_template["RD53B"]["Parameter"]["VcalPar"] = [
                    abs(
                        self.test_run.get_result("VCAL_HIGH_LARGE_RANGE_OFFSET") * 1000
                    ),
                    self.test_run.get_result("VCAL_HIGH_LARGE_RANGE_SLOPE") * 1000,
                ]
                chip_template["RD53B"]["Parameter"][
                    "IrefTrim"
                ] = self.test_run.get_result("IREF_TRIM")
                chip_template["RD53B"]["Parameter"][
                    "KSenseInA"
                ] = self.test_run.get_result("CURR_MULT_FAC_A")
                chip_template["RD53B"]["Parameter"][
                    "KSenseInD"
                ] = self.test_run.get_result("CURR_MULT_FAC_D")
                chip_template["RD53B"]["Parameter"]["KSenseShuntA"] = (
                    self.test_run.get_result("CURR_MULT_FAC_A") * 26000.0 / 21000.0
                )
                chip_template["RD53B"]["Parameter"]["KSenseShuntD"] = (
                    self.test_run.get_result("CURR_MULT_FAC_D") * 26000.0 / 21000.0
                )
                chip_template["RD53B"]["Parameter"][
                    "KShuntA"
                ] = self.test_run.get_result("VINA_SHUNT_KFACTOR")
                chip_template["RD53B"]["Parameter"][
                    "KShuntD"
                ] = self.test_run.get_result("VIND_SHUNT_KFACTOR")

            return chip_template
        else:
            msg = f"Not able to generate config for chip {self.uid}. Chip configs might not be complete."
            raise RuntimeError(msg)
        return None


class TestRun:
    """
    TestRun class.
    """

    def __init__(self, client, test_run_id):
        self.client = client
        self.identifier = test_run_id
        self.test_run = client.get("getTestRun", json={"testRun": test_run_id})
        self.results = pd.DataFrame(self.test_run["results"])

        log.info("test run %s initiated.", self.identifier)

    def get_result(self, code):
        """
        Get test run result.
        """
        if len(self.results[self.results["code"] == code]) > 0:
            return self.results[self.results["code"] == code]["value"].iloc[-1]
        return None
