from django.forms import Widget, HiddenInput
from django.utils.safestring import mark_safe
from django.conf import settings
from django.forms.widgets import Media, MediaDefiningClass
import logging

class LocationWidget(Widget, metaclass=MediaDefiningClass):
    class Media:
        js = [
            'https://maps.googleapis.com/maps/api/js?key={}&libraries=places'.format(settings.GOOGLE_MAPS_API_KEY),
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
        ]

    def __init__(self, attrs=None):
        default_attrs = {'class': 'location-widget'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        lat, lng = None, None
        if value:
            lat, lng = value.coords

        width = '100%'
        height = '400px'
        default_location = 'new google.maps.LatLng(-1.2921, 36.8219)'
        if lat and lng:
            default_location = f'new google.maps.LatLng({lat}, {lng})'

        html = f"""
            <div id="map-canvas" style="width:{width};height:{height}"></div>
            <input type="hidden" name="{name}" id="{name}" value="{value}" />
            <script>
                var marker, map;

                function initialize() {{
                    var mapOptions = {{
                        zoom: 8,
                        center: {default_location}
                    }};
                    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
                    marker = new google.maps.Marker({{
                        position: {default_location},
                        map: map,
                        draggable:true
                    }});
                    marker.addListener('dragend', function(event) {{
                        document.getElementById('{name}').value = marker.getPosition();
                    }});
                }}

                function handleNetworkError(event) {{
                    alert('There was a network error while loading the Google Maps API. Please try again later.');
                }}

                window.addEventListener('load', function() {{
                    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {{
                        window.removeEventListener('online', handleNetworkError);
                        window.addEventListener('online', initialize);
                        window.addEventListener('offline', handleNetworkError);
                        handleNetworkError();
                    }} else {{
                        initialize();
                    }}
                }});

                async function get_messages() {{
                    const response = await fetch('https://maps.googleapis.com/maps/api/js?key={0}&libraries=places', {{method: 'GET'}});
                    const result = await response.json();
                    //console.log(result);
                }}
            </script>
        """
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            lat, lng = [float(x) for x in value[1:-1].split(',')]
            return Point(lng, lat)
        return None

