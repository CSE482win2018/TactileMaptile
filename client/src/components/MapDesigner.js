import React, { Component } from "react";
import { withRouter, Link } from "react-router-dom";
import MapPreview3D from './MapPreview3D';
import '../App.css';
import '../turret.css';

class MapDesigner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      options: {
        width: null,
        height: null
      },
      showPreview: false,
      stlId: null
    };

    this.handleDesignSubmit = this.handleDesignSubmit.bind(this);
  }

  render() {
    let address = this.props.address;
    if (!address) {
      address = {
        formatted_address: "123 foo st"
      };
    }
    return (
      <div className="container">
        <nav className="nav-inline">
          <ul>
            <li><Link to="/">Back to location search</Link></li>
          </ul>
        </nav>
        <div className="header">
        <h2 className="header-title">Map designer</h2>
        </div>
        <p>Using address: {address.formatted_address}</p>
        <form onSubmit={this.handleDesignSubmit}>
          <fieldset>
            <legend>Map options</legend>
            <div className="field">
              <label htmlFor="map-width">Map size, east to west (kilometers)</label>
              <input id="map-width" type="number" min="0" max="5" placeholder="1"  step="0.1" onChange={event => this.setState({options: {...this.state.options, width: +event.target.value}})} />
            </div>
            <div className="field">
              <label htmlFor="map-height">Map size, north to south (kilometers)</label>
              <input id="map-height" type="number" min="0" max="5" placeholder="1"  step="0.1" onChange={event => this.setState({options: {...this.state.options, height: +event.target.value}})} />
            </div>
            <button type="submit" className="button color-white background-secondary">Create map</button>
          </fieldset>
        </form>
        {this.state.showPreview && (
          this.state.stlId ? (
           <MapPreview3D mapStlUrl={"/api/map/stl/" + this.state.stlId} />
          ) : (
            <div>LOADING</div>
          )
        )}
      </div>
    );
  }

  handleDesignSubmit(event) {
    event.preventDefault();
    this.setState({
      showPreview: true,
      stlId: null
    });
    let data = {
      lng: this.props.address.geometry.location.lng(),
      lat: this.props.address.geometry.location.lat(),
      width: this.state.options.width,
      height: this.state.options.height
    }
    let formData = new URLSearchParams();
    Object.keys(data).forEach(key => {
      formData.append(key, data[key]);
    });
    console.log(formData);
    fetch('/api/map', {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData.toString(), // must match 'Content-Type' header
      method: 'POST', // *GET, PUT, DELETE, etc.
    })
    .then(response => response.json())
    .then(json => {
      console.log(json)
      this.setState({
        stlId: json.id
      });
    });
  }
}

export default withRouter(MapDesigner);