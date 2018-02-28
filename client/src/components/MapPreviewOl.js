import React, { Component } from 'react';
import Map from 'ol/map';
import View from 'ol/view';
import Proj from 'ol/proj';
import TileLayer from 'ol/layer/tile';
import SourceOSM from 'ol/source/osm';
import { computeLonLat, mapDiameter } from '../utils';

import '../App.css';
import '../turret.css';
import 'ol/ol.css';
import Collection from 'ol/collection';
import Overlay from 'ol/overlay';

class MapPreviewOl extends Component {
    constructor(props) {
        super(props);
        this.zoom = this.zoom.bind(this);
        this.updateMap = this.updateMap.bind(this);
    }

    componentDidMount() {
        let loc = this.props.address.geometry.location;
        this.marker = new Overlay({
            element: this.markerEl,
            position: Proj.fromLonLat([loc.lng(), loc.lat()]),
            positioning: 'center-center',
        });
        this.map = new Map({
            target: 'map',
            layers: [
                new TileLayer({
                    source: new SourceOSM()
                })
            ],
            view: new View({
                center: Proj.fromLonLat([loc.lng(), loc.lat()]),
                zoom: 4
            }),
            overlays: new Collection([
                this.marker
            ]),
            controls: []
        });

        this.updateMap(this.props);
    }

    componentWillReceiveProps(nextProps) {
        console.log("receiving props:", this.props, nextProps);
        let checkedProps = ['scale', 'size'];
        if (checkedProps.some(key => this.props.data[key] !== nextProps.data[key]) || this.props.address.formatted_address !== nextProps.address.formatted_address) {
            this.updateMap(nextProps);
        }
    }

    render() {
        return (
            <div>
                <a className="skiplink" href="#map">Focus map</a>
                <div style={{width: '50vw', height: '50vw'}} id="map" className="map" tabIndex="0" ref={map => this.mapEl = map}/>
                <div className="marker" title={this.props.address.formatted_address} ref={marker => this.markerEl = marker}/>
                <button onClick={() => this.zoom(-1)}>Zoom out</button>
                <button onClick={() => this.zoom(1)}>Zoom in</button>
            </div>
        );
    }

    zoom(z) {
        let view = this.map.getView();
        view.setZoom(view.getZoom() + z);
    }

    updateMap(props) {
        console.log("updating map:", props.data);
        // this.map.setSize([this.maxSize, this.maxSize]);
        let lng = props.address.geometry.location.lng();
        let lat = props.address.geometry.location.lat();
        var view = this.map.getView();
        var newCenter = Proj.fromLonLat(computeLonLat(props.data, props.address));
        var diameter = mapDiameter(props.data);
        var metersPerPixel = diameter / this.mapEl.offsetWidth;
        var resolutionAtCoords = metersPerPixel / Proj.getPointResolution(view.getProjection(), 1, newCenter);
        view.setResolution(resolutionAtCoords);
        view.setCenter(newCenter);
        this.marker.setPosition(Proj.fromLonLat([ lng, lat ]));
        let extent = Proj.transformExtent(this.map.getView().calculateExtent(), 'EPSG:3857', 'EPSG:4326');
        if (this.props.updateData) {
            console.log("updating extent:", extent);
            this.props.updateData({
                minLat: extent[1],
                maxLat: extent[3],
                minLng: extent[0],
                maxLng: extent[2]
            });
        }
    }
}

export default MapPreviewOl;