import React, { Component } from 'react';
import { withScriptjs } from 'react-google-maps';
import MapPreviewOl from './MapPreviewOl';
import '../App.css';
import '../turret.css';

class LocationForm extends Component {
  constructor(props) {
    super(props);
    this.geocodeInput = this.geocodeInput.bind(this);
    console.log(window.google);
    this.searchService = new window.google.maps.places.PlacesService(document.createElement('div'));
    console.log(this.searchService);
    this.state = {
      searching: false
    }
  }

  render() {
    let locationResults = this.state.results;
    let searchButton = !this.state.searching ? (
      <button type="submit" className={"button swatch color-white background-primary"}>Search</button>
    ) : (
      <button type="submit" className={ "button spinner swatch color-white background-primary"}/>
    );
    let inputTextStyle = {};
    if (this.props.highContrast) {
      inputTextStyle.color = 'black';
    }

    return (
      <div>
        <form onSubmit={this.geocodeInput}>
          <fieldset>
            <legend>Search for the map's location</legend>
            <div className="input-group">
              <input type="text" style={inputTextStyle} placeholder="Search location" onChange={e => {this.props.updateData({locationInput: e.target.value})}} />
              {searchButton}   
            </div>   
          </fieldset>
        </form>
      </div>
    );
  }

  geocodeInput(event) {
    event.preventDefault();
    console.log(`Searching with ${this.props.data.locationInput}`);
    this.setState({
      searching: true,
    });

    // let results = [
    //   {
    //     formatted_address: "5268 19th ave NE Seattle WA 98105",
    //     geometry: {
    //       location: {
    //         lng: () => -122.3068156,
    //         lat: () => 47.6684414
    //       }
    //     }
    //   }
    // ];
    // this.setState({
    //   searching: false
    // });
    // console.log(results);
    // this.setState({
    //   results: results
    // });

    this.searchService.textSearch({query: this.props.data.locationInput}, (results, status) => {
      this.setState({
        searching: false
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