"""lakeformation base URL and path."""
from .responses import LakeFormationResponse

url_bases = [
    r"https?://lakeformation\.(.+)\.amazonaws\.com",
]


response = LakeFormationResponse()


url_paths = {
    "{0}/.*$": response.dispatch,
}
