import React, { Component } from 'react';
import { Redirect, Link } from 'react-router-dom';

import MapPreviewOl from './MapPreviewOl';
import PlaceResult from './PlaceResult';

import '../App.css';
import '../turret.css';


class MapConfirm extends Component {
  constructor(props) {
    super(props);
    
    this.state = {
      nearbyLocations: null
    };

    this.service = new window.google.maps.places.PlacesService(document.createElement('div'));
   
  }

  componentDidMount() {
    let center = new window.google.maps.LatLng(this.props.data.address.geometry.location.lat(), this.props.data.address.geometry.location.lng());
    let request = {
      location: center,
      radius: 500,
    };
    this.service.nearbySearch(request, (results, status) => {
      if (status == window.google.maps.places.PlacesServiceStatus.OK) {
        if (results.length > 5) {
          results = results.slice(0, 5);
        }
        this.setState({
          nearbyLocations: results
        });
      }
    });
  }

  render() {
    return (
      <div className="row-container">
        <div className="container">
          <nav className="nav-inline">
            <ul>
              <li><Link to="/searchresults">Back to search results</Link></li>
            </ul>
          </nav>
          <div className="header">
            <h2 className="header-title">Confirm Map Center</h2>
          </div>
          <p><PlaceResult address={this.props.data.address}/></p>
          {this.state.nearbyLocations && (
            <div>
              <p>Nearby places:</p>
              <ul>
                {this.state.nearbyLocations.map(location => (
                  <li key={location.id}>{location.name}</li>
                ))}
              </ul>
            </div>
          )}
          <button className="button background-secondary color-white" onClick={() => this.props.history.push('/size')}>Set map size</button>
        </div>
        <div className="container">
          {<MapPreviewOl maxSize={500} data={this.props.data} address={this.props.data.address}/>}
        </div>
      </div>
    )
  }
}

export default MapConfirm;