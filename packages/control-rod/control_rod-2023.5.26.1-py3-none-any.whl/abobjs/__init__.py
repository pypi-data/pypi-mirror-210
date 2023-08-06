from .base import AB_Base

from .control import AB_Control
from .workspace import AB_Workspace
from .region import AB_Region
from .entity import AB_Entity
from .process import AB_Process
from .subprocess import AB_SubProcess
from .risk import AB_Risk
from .assertion import AB_Assertion
from .test_section import AB_TestSection
from .controls_data import AB_Controls_Data
from .effectiveness_option import AB_EffectivenessOption
from .status_option import AB_StatusOption
from .test_type import AB_TestType
from .test import AB_Test
from .file import AB_File

from .continuous_monitoring_systems import AB_Continous_Monitoring_Systems
from .continuous_monitoring_monitors import AB_Continous_Monitoring_Monitors
from .continuous_monitoring_monitor_results import AB_Continous_Monitoring_Monitor_Results

from .auditable_entity import AB_Auditable_Entities
from .auditable_entity_regions import AB_Auditable_Entity_Regions
from .auditable_entity_types import AB_Auditable_Entity_Types
from .vendor_criticalities import AB_Vendor_Criticality

from .buisness_units import AB_Business_Unit
from .departments import AB_Departments

from .custom_field import AB_Custom_Fields

from .multi import AB_Multi

SUBOBJ_LK = {"region_id": {"obj": AB_Region},
             "process_id": {"obj": AB_Process},
             "subprocess_id": {"obj": AB_SubProcess},
             "risk_id": {"obj": AB_Risk},
             "control_id": {"obj": AB_Control},
             "entity_id": {"obj": AB_Entity},
             "controls_datum_ids": {"obj": AB_Controls_Data},
             "test_ids": {"obj": AB_Test},
             "file_ids": {"obj": AB_File},
             "continuous_monitoring_system_id": {"obj": AB_Continous_Monitoring_Systems},
             "continuous_monitoring_monitor_id": {"obj": AB_Continous_Monitoring_Monitors},
             "auditable_entity_id": {"obj": AB_Auditable_Entities},
             "auditable_entity_region_id": {"obj": AB_Auditable_Entity_Regions},
             "vendor_criticalities_id": {"obj": AB_Vendor_Criticality},
             "department_ids": {"obj": AB_Departments}
            }

from .fn_register_cf import fn_register_custom_fields
from .controlrod import AB_ControlRod

USER_AGENT = "control_rod/2023.05.25.0"