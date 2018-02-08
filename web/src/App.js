import React, { Component } from 'react';
import LocationForm from './LocationForm';
import './App.css';
import './turret.css';

const GOOGLE_MAPS_API_URI = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCBqE1PQyfBRxAUnLTk-ixdsmCk936YlW4";

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="header">
          <div className="container">
            <h1>TactileMaptile</h1>
          </div>
        </header>
        <main role="main">
          <div class="container">
          <LocationForm 
            googleMapURL={GOOGLE_MAPS_API_URI}
            loadingElement={<div/>} />
          </div>
        </main>
      </div>
    );
  }
}

export default App;
