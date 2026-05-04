# src/validator.py
import logging
from typing import Dict, List, Tuple
from src.schema import FullBuild, PCPart

logger = logging.getLogger(__name__)

class BuildValidator:
    """Deterministic mathematical validation for PC hardware compatibility."""

    @staticmethod
    def extract_components(build: FullBuild) -> Dict[str, PCPart]:
        """Maps component list to a dictionary by category for O(1) lookups."""
        return {part.category: part for part in build.components}

    @classmethod
    def validate_build(cls, build: FullBuild) -> Tuple[bool, List[str]]:
        errors =
        parts = cls.extract_components(build)

        # Ensure all required core components are present
        required_categories = {"CPU", "GPU", "MOBO", "RAM", "PSU", "CASE", "COOLER"}
        missing = required_categories - set(parts.keys())
        if missing:
            errors.append(f"Missing required components: {missing}")
            return False, errors

        cls._check_socket_compatibility(parts, errors)
        cls._check_memory_compatibility(parts, errors)
        cls._check_physical_clearance(parts, errors)
        cls._check_electrical_overhead(parts, errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def _check_socket_compatibility(parts: Dict[str, PCPart], errors: List[str]) -> None:
        cpu, mobo, cooler = parts["CPU"], parts, parts

        # CPU to Motherboard matching
        if cpu.socket!= mobo.socket:
            errors.append(f"Socket mismatch: CPU is {cpu.socket}, MOBO is {mobo.socket}.")

        # Intel LGA1851 edge case logic: LGA1700 coolers are mechanically compatible
        if cpu.socket == "LGA1851" and cooler.socket == "LGA1700":
            pass # Valid mechanically
        elif cooler.socket and cpu.socket not in cooler.socket:
            errors.append(f"Cooler socket mismatch: Cooler supports {cooler.socket}, CPU is {cpu.socket}.")

    @staticmethod
    def _check_memory_compatibility(parts: Dict[str, PCPart], errors: List[str]) -> None:
        mobo, ram = parts, parts
        
        if mobo.memory_type!= ram.memory_type:
            errors.append(f"Memory mismatch: MOBO requires {mobo.memory_type}, RAM is {ram.memory_type}.")

    @staticmethod
    def _check_physical_clearance(parts: Dict[str, PCPart], errors: List[str]) -> None:
        gpu, case, cooler, psu = parts["GPU"], parts, parts, parts

        # GPU Length Clearance
        if gpu.dimensions and case.max_gpu_length:
            # Mandating a 15mm buffer for front intake airflow
            if gpu.dimensions["length"] + 15 > case.max_gpu_length:
                errors.append(f"GPU too long: {gpu.dimensions['length']}mm exceeds case max {case.max_gpu_length}mm with buffer.")

        # CPU Cooler Height Clearance
        if cooler.dimensions and case.max_cooler_height:
            if cooler.dimensions["height"] > case.max_cooler_height:
                errors.append(f"Cooler too tall: {cooler.dimensions['height']}mm exceeds case max {case.max_cooler_height}mm.")
        elif cooler.dimensions and case.dimensions:
            # Fallback heuristic: Case Width must be > Cooler Height + 15mm (standoffs/IHS)
            if cooler.dimensions["height"] + 15 > case.dimensions["width"]:
                errors.append("Fallback check failed: Case width insufficient for cooler height.")

        # PSU Form Factor (SFX vs ATX)
        if case.form_factor == "Mini-ITX" and psu.form_factor == "ATX":
            errors.append("Form factor mismatch: Mini-ITX cases generally require SFX/SFX-L PSUs.")

    @staticmethod
    def _check_electrical_overhead(parts: Dict[str, PCPart], errors: List[str]) -> None:
        cpu, gpu, psu = parts["CPU"], parts["GPU"], parts
        
        # Base system draw + 125W margin for motherboard, RAM, storage, and fans
        system_base_draw = cpu.wattage + gpu.wattage + 125
        
        # Apply 1.25x safety multiplier for transient spikes and peak efficiency curve
        required_wattage = system_base_draw * 1.25

        if required_wattage > psu.wattage:
            errors.append(f"Insufficient PSU: System requires {required_wattage}W overhead, PSU is {psu.wattage}W.")