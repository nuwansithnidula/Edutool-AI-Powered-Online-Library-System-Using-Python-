from services.search_service import SBERTSearchService

class SearchFactory:
    @staticmethod
    def get_search_service(service_type="sbert"):
        if service_type == "sbert":
            return SBERTSearchService()
        else:
            raise ValueError("Unknown search service type")