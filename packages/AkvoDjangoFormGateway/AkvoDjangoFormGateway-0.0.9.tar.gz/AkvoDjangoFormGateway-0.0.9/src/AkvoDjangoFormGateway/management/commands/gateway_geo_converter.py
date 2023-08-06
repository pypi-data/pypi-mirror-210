import re
from django.conf import settings
from django.core.management import BaseCommand
from AkvoDjangoFormGateway.models import AkvoGatewayAnswer
from AkvoDjangoFormGateway.constants import QuestionTypes
from AkvoDjangoFormGateway.utils.services import geo_service

google_map_api_key = settings.GOOGLE_MAPS_API_KEY
geo_pattern = r'^[-+]?[0-9]*\.?[0-9]+,[-+]?[0-9]*\.?[0-9]+$'

'''
The string contains two floats separated by a comma.
-- ^ and $ denote the start and end of the string, respectively.
-- [-+]? matches an optional positive or negative sign.
-- [0-9]* matches zero or more digits.
-- .? matches an optional decimal point.
-- [0-9]+ matches one or more digits.
-- , matches the comma character.
-- The second part of the pattern is the same as the first part,
-- representing the second float.
'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = AkvoGatewayAnswer.objects.filter(
                question__type=QuestionTypes.geo
                ).all()
        for d in data:
            if re.match(geo_pattern, str(d.options)):
                coordinates = [float(o.strip()) for o in d.options.split(",")]
                d.options = coordinates
                d.save()
            address = geo_service(
                    latitude=str(d.options[0]),
                    longitude=str(d.options[1]),
                    api_key=google_map_api_key)
            if address:
                d.name = address["results"][0]["formatted_address"]
            d.save()
