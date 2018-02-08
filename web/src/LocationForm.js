import React, { Component } from 'react';
import { withScriptjs } from 'react-google-maps';

class LocationForm extends Component {
  constructor(props) {
    super(props);
    this.geocodeInput = this.geocodeInput.bind(this);
    this.geocoder = new window.google.maps.Geocoder();
    this.state = {
      locationInput: null,
      results: null
    }
  }

  render() {
    let locationResults = this.state.results;
    return (
      <div>
        <form onSubmit={this.geocodeInput}>
          <input type="text" placeholder="Search location" onChange={e => {this.setState({locationInput: e.target.value})}} />
          <button type="submit">Search</button>
        </form>
        {locationResults && (
          <div>
            <p>Found {locationResults.length} result{locationResults.length == 1 ? '' : 's'}:</p>
            {this.state.results.map(result => (
              <div key={result.formatted_address}>
                {result.formatted_address}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  geocodeInput(event) {
    event.preventDefault();
    console.log(`Geocoding with ${this.state.locationInput}`);
    this.geocoder.geocode({address: this.state.locationInput}, (results, status) => {
      if (status !== 'OK') {
        console.log(`GEOCODING ERROR: ${status}`);
        return;
      }

      console.log(results);
      this.setState({
        results: results
      });
    });
  }

}

export default withScriptjs(LocationForm);