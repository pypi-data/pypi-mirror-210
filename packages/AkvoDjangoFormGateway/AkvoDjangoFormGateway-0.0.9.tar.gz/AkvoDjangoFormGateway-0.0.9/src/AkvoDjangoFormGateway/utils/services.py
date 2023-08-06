import requests
from AkvoDjangoFormGateway.models import AkvoGatewayAnswer as Answers
from AkvoDjangoFormGateway.constants import QuestionTypes


def geo_service(
    latitude: str,
    longitude: str,
    api_key: str = None,
):
    if api_key is None:
        return None
    if latitude and longitude:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            url += f"?latlng={latitude},{longitude}&key={api_key}"
            response = requests.get(url)
            res_data = response.json()
            if response.status_code == 200 and res_data["status"] == "OK":
                return res_data
        except Exception:
            pass
    return None


def store_geo_service(answer: Answers, api_key: str = None) -> Answers:
    if answer and answer.question.type == QuestionTypes.geo:
        [lat, lng] = answer.options
        res = geo_service(latitude=lat, longitude=lng, api_key=api_key)
        if res:
            answer.name = res["results"][0]["formatted_address"]
            answer.save()
    return answer
