import React, { Component } from 'react';

class LocationForm extends Component {
construct
  render() {
    return (
      <form>
        <input type="text" placeholder="Search location" />
        <button type="submit">Search</button>
      </form>
    );
  }
}

export default LocationForm;