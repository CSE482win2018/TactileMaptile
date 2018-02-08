import React, { Component } from 'react';
import LocationForm from './LocationForm';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">TactileMaptile</h1>
        </header>
        <div>
          <LocationForm />
        </div>
      </div>
    );
  }
}

export default App;
