
import logging
from agent_config import Config
 
import http.client
import json
from typing import List, Dict, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class InternetSearchInput(BaseModel):
    query: str = Field(..., description="Search query to send to Google via Serper API")

class InternetSearchTool(BaseTool):
    name: str = "internet_search_tool"
    description: str = "Search the internet using Google and return organic search results only"
    args_schema: Type[BaseModel] = InternetSearchInput

    def _run(self, query: str) -> List[Dict[str, str]]:
        logger.info(f"Starting internet search for query: {query}")
        try:
            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({"q": query})
            headers = {
                'X-API-KEY': Config.SERPER_API_TOKEN,  # Replace with your actual API key
                'Content-Type': 'application/json'
            }

            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            json_data = json.loads(data)
            logger.debug(f"Raw response data: {json_data}")

            organic_results = json_data.get("organic", [])
            results = []
            for result in organic_results:
                res_item = {
                    # "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet")
                }
                results.append(res_item)
                logger.debug(f"Parsed search result item: {res_item}")

            logger.info(f"Search completed, found {len(results)} organic results")
            return results

        except Exception as e:
            logger.error(f"Error during internet search: {e}", exc_info=True)
            return [{"error": str(e)}]

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported for this tool.")
