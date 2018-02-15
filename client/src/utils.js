function deg2rad(deg) {
    var conv_factor = (2.0 * Math.PI) / 360.0;
    return (deg * conv_factor);
}

function metersPerDegree(latitude) { // Compute lengths of degrees
    // Convert latitude to radians
    var lat = deg2rad(latitude);

    // Set up "Constants"
    var m1 = 111132.92; // latitude calculation term 1
    var m2 = -559.82; // latitude calculation term 2
    var m3 = 1.175; // latitude calculation term 3
    var m4 = -0.0023; // latitude calculation term 4
    var p1 = 111412.84; // longitude calculation term 1
    var p2 = -93.5; // longitude calculation term 2
    var p3 = 0.118; // longitude calculation term 3

    // Calculate the length of a degree of latitude and longitude in meters
    var latlen = m1 + (m2 * Math.cos(2 * lat)) + (m3 * Math.cos(4 * lat)) + (m4 * Math.cos(6 * lat));
    var longlen = (p1 * Math.cos(lat)) + (p2 * Math.cos(3 * lat)) + (p3 * Math.cos(5 * lat));

    return {
        lat: latlen,
        lon: longlen
    };
}

export function computeLonLat(data, address) {
    address = address || data.address;
    var lat = address.geometry.location.lat();
    var lng = address.geometry.location.lng();
    var metersPerDeg = metersPerDegree(lat);
    return [
        lng + data.offsetX,
        lat + data.offsetY
    ]
}

export function mapDiameter(data) {
    // Map diameter in meters
    return data.size / 100 * data.scale;
}