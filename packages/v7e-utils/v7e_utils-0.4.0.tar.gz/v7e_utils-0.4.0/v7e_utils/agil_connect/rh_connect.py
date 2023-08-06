from v7e_utils.agil_connect.agil_connect import AgilConnection
from urllib.parse import urlencode

class RhSingleEmployee(AgilConnection):
    def __init__(self, url=None):
        super().__init__(url)
        self.set_api_endpoint('paf/employeeBasicInfo/')

    def get_rh_employees_single(self, parameters):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url, parameters)
    
    
class RhEmployees(AgilConnection):
    def __init__(self, url=None):
        super().__init__(url)
        self.set_api_endpoint('paf/allEmployeesBasicInfo/')

    def get_rh_employees_single(self, person):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url,[('person', person)])
    def get_rh_employees_all(self):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url)

    def get_rh_employees_active(self):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url,[('current_category', '1')])

    #esta ultima con parametros no esta ctualmente en uso,
    # pero para que sirva hay que mandarle una tupla como parametro
    def get_rh_employees_with_parameters(self, parameters):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url, parameters)


#rhSupervisors
class RhSupervisors(AgilConnection):

    def __init__(self, url=None):
        super().__init__(url)
        self.set_api_endpoint('paf/allSupervisorBasicInfo/')
    def get_rh_supervisors(self):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url)



#RhEmployees_from_Supervisor
class RhEmployeesSupervisor (AgilConnection):
    def __init__(self, url=None):
        super().__init__(url)
        self.set_api_endpoint('paf/employeesWithSupervisor/')
    def get_rh_employees_supervisor_all(self):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url)

    def get_rh_employees_from_supervisor(self, parameters):
        url = self.ensure_url(self.gateway_url, self.api_endpoint)
        return self.get_result(url, parameters)
