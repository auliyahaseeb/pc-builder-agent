# tests/test_builds.py
import pytest
from src.schema import PCPart, FullBuild
from src.validator import BuildValidator

def create_mock_part(category, **kwargs):
    base = {
        "name": f"Mock {category}",
        "price": 100.0,
        "vendor": "TestVendor",
        "wattage": 50
    }
    base.update(kwargs)
    return PCPart(category=category, **base)

def test_cross_generation_socket_mismatch():
    """Tests if AMD AM5 CPU is correctly rejected on an Intel LGA1851 Motherboard."""
    cpu = create_mock_part("CPU", socket="AM5", memory_type="DDR5")
    mobo = create_mock_part("MOBO", socket="LGA1851", memory_type="DDR5")
    cooler = create_mock_part("COOLER", socket="AM5")
    
    build = FullBuild(components=[cpu, mobo, cooler])
    is_valid, errors = BuildValidator.validate_build(build)
    
    assert not is_valid
    assert any("Socket mismatch" in err for err in errors)

def test_atx_psu_in_itx_case_rejection():
    """Tests physical form factor logic for power supplies in SFF cases."""
    psu = create_mock_part("PSU", form_factor="ATX")
    case = create_mock_part("CASE", form_factor="Mini-ITX")
    
    build = FullBuild(components=[psu, case])
    is_valid, errors = BuildValidator.validate_build(build)
    
    assert not is_valid
    assert any("Form factor mismatch" in err for err in errors)

def test_tdp_overhead_starvation():
    """Tests if the 1.25x safety multiplier correctly rejects underpowered PSUs."""
    cpu = create_mock_part("CPU", wattage=150)
    gpu = create_mock_part("GPU", wattage=350) # 500W total base
    psu = create_mock_part("PSU", wattage=600) # Base + 125W = 625W * 1.25 = 781.25W requirement
    
    build = FullBuild(components=[cpu, gpu, psu])
    is_valid, errors = BuildValidator.validate_build(build)
    
    assert not is_valid
    assert any("Insufficient PSU" in err for err in errors)