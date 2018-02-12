import React, { Component } from 'react';
import LocationForm from './LocationForm';
import * as config from './config.json';
import './App.css';

class Home extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="container">
        <div className="App-info">
          Design your own tactile maps to explore and navigate.
        </div>
        <div className="form-area">
          <LocationForm 
          setMapAddress={this.props.setMapAddress}
          googleMapURL={config.googleMapsApiUri}
          loadingElement={<div/>} />
        </div>
      </div>
    );
  }
}

export default Home;