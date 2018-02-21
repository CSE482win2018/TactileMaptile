import React, { Component } from 'react';
import { withScriptjs } from 'react-google-maps';
import MapPreviewOl from './MapPreviewOl';
import '../App.css';
import '../turret.css';

class LocationForm extends Component {
  constructor(props) {
    super(props);
    this.geocodeInput = this.geocodeInput.bind(this);
    this.geocoder = new window.google.maps.Geocoder();
    this.state = {
      isGeocoding: false
    }
  }

  render() {
    let locationResults = this.state.results;
    let searchButton = !this.state.isGeocoding ? (
      <button type="submit" className={"button swatch color-white background-primary"}>Search</button>
    ) : (
      <button type="submit" className={ "button spinner swatch color-white background-primary"}/>
    );
    return (
      <div>
        <form onSubmit={this.geocodeInput}>
          <fieldset>
            <legend>Search for the map's location</legend>
            <div className="input-group">
              <input type="text" placeholder="Search location" onChange={e => {this.props.updateData({locationInput: e.target.value})}} />
              {searchButton}   
            </div>   
          </fieldset>
        </form>
      </div>
    );
  }

  geocodeInput(event) {
    event.preventDefault();
    console.log(`Geocoding with ${this.state.locationInput}`);
    this.setState({
      isGeocoding: true,
      results: null
    });

    let results = [
      {
        formatted_address: "5268 19th ave NE Seattle WA 98105",
        geometry: {
          location: {
            lng: () => -122.3068156,
            lat: () => 47.6684414
          }
        }
      }
    ];

    // this.setState({
    //   isGeocoding: false
    // });
    // console.log(results);
    // this.setState({
    //   results: results
    // });

    this.geocoder.geocode({address: this.props.data.locationInput}, (results, status) => {
      this.setState({
        isGeocoding: false
      });
      if (status !== 'OK') {
        console.log(`GEOCODING ERROR: ${status}`);
        return;
      }

      this.props.setSearchResults(results);
    });
  }
}

export default withScriptjs(LocationForm);