import requests
from typing import Dict, List
import base64

class CHAW():
    def __init__(self, api_key: str, url: str = "https://api.company-information.service.gov.uk/"):
        self._url = url
        self._sesh = requests.Session()
        encoded_key = base64.b64encode((api_key + ":").encode("UTF-8")).decode("UTF-8")
        self._sesh.headers.update({"Authorization" : f"Basic {encoded_key}"})

    def get_office_address(self, company_number: str) -> Dict:
        resp = self._sesh.get(f"{self._url}company/{company_number}/registered-office-address")
        err = self.handle_error(resp)
        if not err:
            address_data: Dict = resp.json()
            return address_data
        else:
            raise err

    def get_company_profile(self, company_number: str) -> Dict:
        resp = self._sesh.get(f"{self._url}company/{company_number}")
        err = self.handle_error(resp)
        if not err:
            profile_data: Dict = resp.json()
            return profile_data
        else:
            raise err

    def advanced_search(self, query: Dict[str, List | str]):
        """
            https://github.com/companieshouse/api-enumerations/blob/master/constants.yml
        """
        parameters = ["company_name_includes", "company_name_excludes", "company_status", "company_subtype", 
                      "company_type", "dissolved_from", "dissolved_to", "incorporated_from", "incorporated_to", 
                      "location", "sic_codes", "size", "start_index"]
        query_str = self._generate_query_str(query, parameters)

        resp = self._sesh.get(f"{self._url}advanced-search/companies{query_str}")
        err = self.handle_error(resp)

        if not err:
            search_results: Dict = resp.json()
            return search_results
        else:
            raise err

    def search(self, search_type: str, query: str, start_index: int = 0, items_per_page: int = 50, extras=None):
        match search_type:
            case "all":
                route = f"search?q={query}&items_per_page={items_per_page}&start_index={start_index}"
            case "companies":
                route = f"search/companies?q={query}&items_per_page={items_per_page}&start_index={start_index}"
            case "officers":
                route = f"search/officers?q={query}&items_per_page={items_per_page}&start_index={start_index}"
            case "disqualified-officers":
                route = f"search/disqualified-officers?q={query}&items_per_page={items_per_page}&start_index={start_index}"
            case "dissolved-search":
                if extras is None:
                    raise ValueError("extras argument is required for dissolved search (alphabetical,best-match,previous-name-dissolved)")
                route = f"dissolved-search/companies?q={query}&size={items_per_page}&start_index={start_index}&search_type={extras}"
        
        resp = self._sesh.get(self._url + route)
        err = self.handle_error(resp)

        if not err:
            search_results: Dict = resp.json()
            return search_results
        else:
            raise err

    def list_officers(self, company_number: str, query_parameters: Dict = None):
        parameters = ["items_per_page","register_type","register_view","start_index","order_by"]
        if query_parameters is not None:
            query_str = self._generate_query_str(query_parameters, parameters)
        else:
            query_str = ""

        resp = self._sesh.get(f"{self._url}company/{company_number}/officers{query_str}")
        err = self.handle_error(resp)

        if not err:
            officers: Dict = resp.json()
            return officers
        else:
            raise err

    def get_officer(self, company_number: str, appointment_id: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/appointments/{appointment_id}")
        err = self.handle_error(resp)

        if not err:
            officer: Dict = resp.json()
            return officer
        else:
            raise err

    def get_company_registers(self, company_number: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/registers")
        err = self.handle_error(resp)

        if not err:
            registers: Dict = resp.json()
            return registers
        else:
            raise err

    def list_charges(self, company_number: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/charges")
        err = self.handle_error(resp)

        if not err:
            charges: Dict = resp.json()
            return charges
        else:
            raise err

    def get_charge(self, company_number: str, charge_id: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/charges/{charge_id}")
        err = self.handle_error(resp)

        if not err:
            charge: Dict = resp.json()
            return charge
        else:
            raise err

    def list_filing_history(self, company_number: str, query_parameters: Dict = None):
        parameters = ["category","items_per_page","start_index"]
        if query_parameters is not None:
            query_str = self._generate_query_str(query_parameters, parameters)
        else:
            query_str = ""

        resp = self._sesh.get(f"{self._url}company/{company_number}/filing-history{query_str}")
        err = self.handle_error(resp)

        if not err:
            filings: Dict = resp.json()
            return filings
        else:
            raise err

    def get_filing(self, company_number: str, transaction_id: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/filing-history/{transaction_id}")
        err = self.handle_error(resp)

        if not err:
            filing: Dict = resp.json()
            return filing
        else:
            raise err

    def list_insolvencies(self, company_number: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/insolvency")
        err = self.handle_error(resp)

        if not err:
            insolvencies: Dict = resp.json()
            return insolvencies
        else:
            raise err

    def get_exemptions(self, company_number: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/exemptions")
        err = self.handle_error(resp)

        if not err:
            exemptions: Dict = resp.json()
            return exemptions
        else:
            raise err

    def get_disqualified_corperate_officer(self, officer_id: str):
        resp = self._sesh.get(f"{self._url}disqualified-officers/corporate/{officer_id}")
        err = self.handle_error(resp)

        if not err:
            corp_officer: Dict = resp.json()
            return corp_officer
        else:
            raise err

    def get_disqualified_natural_officer(self, officer_id: str):
        resp = self._sesh.get(f"{self._url}disqualified-officers/natural/{officer_id}")
        err = self.handle_error(resp)

        if not err:
            nat_officer: Dict = resp.json()
            return nat_officer
        else:
            raise err

    def list_officers_appointments(self, officer_id: str):
        resp = self._sesh.get(f"{self._url}officers/{officer_id}/appointments")
        err = self.handle_error(resp)

        if not err:
            appointments: Dict = resp.json()
            return appointments
        else:
            raise err

    def get_uk_establishments(self, company_number: str):
        resp = self._sesh.get(f"{self._url}company/{company_number}/uk-establishments")
        err = self.handle_error(resp)

        if not err:
            appointments: Dict = resp.json()
            return appointments
        else:
            raise err

    def get_psc(self, company_number: str, psc_id: str, psc_type: str):
        psc_types = ["corporate-entity-beneficial-owner","corporate-entity","individual-beneficial-owner",
                     "individual","legal-person-beneficial-owner","legal-person"]
        if psc_type in psc_types:
            resp = self._sesh.get(f"{self._url}company/{company_number}/persons-with-significant-control/{psc_type}/{psc_id}")
            err = self.handle_error(resp)

            if not err:
                psc: Dict = resp.json()
                return psc
            else:
                raise err

    def list_psc(self, company_number: str, query_parameters: Dict = None):
        parameters = ["register_view","items_per_page","start_index"]
        if query_parameters is not None:
            query_str = self._generate_query_str(query_parameters, parameters)
        else:
            query_str = ""

        resp = self._sesh.get(f"{self._url}company/{company_number}/persons-with-significant-control{query_str}")
        err = self.handle_error(resp)

        if not err:
            psc: Dict = resp.json()
            return psc
        else:
            raise err

    def get_document(self, document_id):
        resp = self._sesh.get(f"https://document-api.company-information.service.gov.uk/document/{document_id}/content")
        err = self.handle_error(resp)
        if not err:
            content_type = resp.headers["Content-Type"]
            if content_type in ["application/xml", "application/xhtml+xml", "text/csv"]:
                document_content = resp.content.decode()
            elif content_type in ["application/json"]:
                document_content = resp.json()
            else: # PDF file
                document_content = resp.content
            return document_content

    def _generate_query_str(self, query, parameters):
        query_str = "?"
        for param in query:
            if param in parameters:
                if type(query[param]) is list:
                    for item in query[param]:
                        query_str += f"{param}={item}&"
                else:
                    query_str += f"{param}={query[param]}&"
        return query_str[:-1]

    def handle_error(self, resp: requests.Response):
        if resp.status_code >= 400:
            match resp.status_code:
                case 429:
                    pass # Retry request
                case 404:
                    return ValueError("No results")
                case 400:
                    return ValueError(f"Bad request - {resp.content}")
        else:
            if resp.content == b'':
                return ValueError("No results found")
