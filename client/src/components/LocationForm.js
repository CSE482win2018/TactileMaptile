import React, { Component } from 'react';
import { withScriptjs } from 'react-google-maps';
import MapPreviewOl from './MapPreviewOl';
import '../App.css';
import '../turret.css';

class LocationForm extends Component {
  constructor(props) {
    super(props);
    this.geocodeInput = this.geocodeInput.bind(this);
    this.handleMultipleResultsSelect = this.handleMultipleResultsSelect.bind(this);
    this.handleMultipleResultsSubmit = this.handleMultipleResultsSubmit.bind(this);
    this.handleAddressSubmit = this.handleAddressSubmit.bind(this);

    this.geocoder = new window.google.maps.Geocoder();
    this.state = {
      locationInput: null,
      isGeocoding: false,
      results: null,
      multipleResults: {
        chosenResultIndex: null,
        showFormError: false
      }
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
              <input type="text" placeholder="Search location" onChange={e => {this.setState({locationInput: e.target.value})}} />
              {searchButton}   
            </div>   
          </fieldset>
        </form>
        {locationResults && !this.state.isGeocoding && this.getResultsUI(locationResults)}
      </div>
    );
  }

  /**
   * 1 result - is it correct address? Button for yes to move on.
   * 0 results - message that no results were found, no buttons.
   * >1 results - list of first five results, notify to search again or choose one of the results, and button for yes to move on.
   */
  getResultsUI(results) {
    if (results.length === 0) {
      return (
        <div>
          <p>Found no results. Try searching again.</p>
        </div>
      );
    } else if (results.length === 1) {
      let address = results[0];
      return (
        <div>
          <fieldset>
            <legend>Confirm address</legend>
            <p>Found 1 results. Hit "OK" if this is the address you want, otherwise try searching again.</p>
            <p>Address found: {address.formatted_address}</p>
            <MapPreviewOl data={this.props.data} address={address}/>
            <form onSubmit={(event) => this.handleAddressSubmit(event, address)}>
              <button type="submit" className={"button swatch color-white background-secondary"}>OK</button>
            </form>
          </fieldset>
        </div>
      );
    } else {
      if (results.length > 5) {
        results = results.slice(0, 5);
      }
      return (
        <div>
          <form onSubmit={this.handleMultipleResultsSubmit}>
            <p>Found {results.length} results. Choose the correct address below and hit "OK", otherwise try searching again.</p>
            <fieldset>
              <legend>Choose an address</legend>
              {results.map((result, index) => (
                <div className="field" key={index}>
                  <input id={"radio-" + index} type="radio" name="address" value={index} onChange={this.handleMultipleResultsSelect}/>
                  <label htmlFor={"radio-" + index}>{result.formatted_address}</label>
                </div>
              ))}
            <button type="submit" className={"button swatch color-white background-secondary"}>OK</button>
            {this.state.multipleResults.showFormError && (
              <p className="form-message error">Choose one of the addresses before hitting "OK"</p>
            )}
            </fieldset>
          </form>
        </div>
      );
    }
  }

  handleAddressSubmit(event, address) {
    event.preventDefault();
    this.props.updateData({...this.props.data, ...{address: address}});
    this.props.setMapAddress(address);
  }

  handleMultipleResultsSelect(event) {
    let multipleResults = {...this.state.multipleResults};
    let resultIndex = +event.currentTarget.value;
    multipleResults.chosenResultIndex = resultIndex;
    this.setState({multipleResults});
  }

  handleMultipleResultsSubmit(event) {
    event.preventDefault();
    if (!this.state.multipleResults.chosenResultIndex) {
      let multipleResults = {...this.state.multipleResults};
      multipleResults.showFormError = true;
      this.setState({multipleResults});
      return;
    }

    let multipleResults = {...this.state.multipleResults};
    multipleResults.showFormError = false;
    this.setState({multipleResults});
    this.props.setData({address: this.state.results[multipleResults.chosenResultIndex]});
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
    this.setState({
      isGeocoding: false
    });
    console.log(results);
    this.setState({
      results: results
    });

    // this.geocoder.geocode({address: this.state.locationInput}, (results, status) => {
    //   this.setState({
    //     isGeocoding: false
    //   });
    //   if (status !== 'OK') {
    //     console.log(`GEOCODING ERROR: ${status}`);
    //     return;
    //   }

    //   console.log(results);
    //   this.setState({
    //     results: results
    //   });
    // });
  }
}

export default withScriptjs(LocationForm);