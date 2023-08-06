from typing import Any, Dict, Optional

from ._design import _Design, get_available_design_objects
from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from .design_object_uiform import DesignObjectUiForm
from .design_object import DesignObject
from .design_object_type import DesignObjectType
from .helper import find_component_by_label_and_type_dict
from .uiform import SailUiForm


class ApplicationUiForm(SailUiForm):

    def __init__(self, interactor: _Interactor, state: Dict[str, Any], breadcrumb: str = "ApplicationUi"):
        super().__init__(interactor, state, breadcrumb)
        self.__design = _Design(interactor)

    @raises_locust_error
    def click_design_object(self, design_object_name: str) -> DesignObjectUiForm:
        """
        Click on a design object in the design object grid. The current view of the grid must contain the object you wish
        to click.
        Args:
            design_object_name: The name of the design object to click on

        Returns (DesignObjectUiForm): UiForm representing UI of design object

        """
        opaque_id = self.__design.find_design_object_opaque_id_in_grid(design_object_name, self._state)
        breadcrumb = "Design.SelectedObject." + opaque_id[0:10] + ".SailUi"
        return DesignObjectUiForm(self._interactor, self.__design.fetch_design_object_json(opaque_id), breadcrumb)

    @raises_locust_error
    def create_record_type(self, record_type_name: str) -> 'ApplicationUiForm':
        """
        Takes an application form and creates a record type with the given name

        Returns: The SAIL UI Form after the record type is created

        """
        self.__design.create_object(self, link_name='Record Type', object_name=record_type_name)
        return self

    @raises_locust_error
    def create_report(self, report_name: str) -> 'ApplicationUiForm':
        """
        Takes an application form and creates a report with the given name

        Returns: The SAIL UI Form after the report is created

        """
        self.__design.create_object(self, link_name='Report', object_name=report_name)
        return self

    def get_available_design_objects(self) -> Dict[str, DesignObject]:
        """
        Retrieve all available design objects in the application, must be on page with design object list

        Returns (dict): Dictionary mapping design object names to DesignObject
        """
        return get_available_design_objects(self._state)

    def search_objects(self, search_str: str, locust_label: Optional[str] = None) -> 'ApplicationUiForm':
        """
            Search the design object list in an Application, must be on page with design object list
            Args:
                search_str (str): The string to search
                locust_label (str): Label to associate request with

            Returns (ApplicationUiForm): A UiForm with updated state after the search is complete

        """
        new_state = self.__design.search_design_grid(
            search_str, self._get_update_url_for_reeval(self._state), self._state, self.context, self.uuid,
            locust_label if locust_label else f"{self.breadcrumb}.ObjectSearch"
        )
        self._reconcile_state(new_state)
        return self

    def filter_design_objects(self, design_object_types: list[DesignObjectType]) -> 'ApplicationUiForm':
        """
        Filter the design object list in an Application, must be on page with design object list
        Args:
            design_object_types (DesignObjectType): List of the types of objects you wish to filter on

        Returns (ApplicationUiForm): ApplicationUiForm with filtered list of design objects

        """
        self.check_checkbox_by_test_label(test_label="object-type-checkbox",
                                          indices=[design_object_type.value for design_object_type in design_object_types])
        return self
